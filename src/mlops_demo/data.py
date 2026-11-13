"""Spambase: ativação da base reproduzível, validação e preparação do CT.

Uso na linha de comando:
    python -m mlops_demo.data base      # cria base_treino.csv e base_holdout.csv (uma vez)
    python -m mlops_demo.data preparar  # junta base + lotes e gera data/processed/
    python -m mlops_demo.data validar   # valida todos os CSVs de data/raw/
"""

import json
import re
import shutil
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from mlops_demo import config
from mlops_demo.spambase import PASTA_SPAMBASE, SEMENTE, sha256, validar_spambase, verificar

SEMENTE_DADOS = SEMENTE  # a divisão do commit 2 é fixa; não sorteie um holdout novo


def dividir_dataset() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Lê, sem novo sorteio, treino, holdout e reserva preparados e verificados."""
    verificar()
    return tuple(
        pd.read_csv(PASTA_SPAMBASE / "preparado" / f"base_{nome}.csv")
        for nome in ("treino", "holdout", "reserva")
    )


def criar_base() -> None:
    """Ativa os CSVs certificados no commit 2, preservando seus bytes e o holdout fixo."""
    verificar()
    config.DADOS_BRUTOS.mkdir(parents=True, exist_ok=True)
    config.DADOS_LOTES.mkdir(parents=True, exist_ok=True)
    for destino in (config.BASE_TREINO, config.BASE_HOLDOUT):
        shutil.copyfile(PASTA_SPAMBASE / "preparado" / destino.name, destino)
    print("Spambase ativado: 2522 linhas de treino e 841 de holdout; reserva isolada.")


def aplicar_drift(df: pd.DataFrame, fator: float) -> pd.DataFrame:
    """Simula mudanças em frequências promocionais, respeitando o intervalo percentual."""
    if not np.isfinite(fator) or fator <= 0:
        raise ValueError("O fator de drift deve ser finito e positivo.")
    saida = df.copy()
    for coluna in config.COLUNAS_DRIFT:
        saida[coluna] = (saida[coluna] * fator).clip(upper=100)
    return saida


def gerar_lote(nome: str, n: int = 400, fator_drift: float = 1.0, semente: int = 1) -> str:
    """Cria data/raw/lotes/<nome>.csv a partir da reserva, opcionalmente com drift."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", nome):
        raise ValueError("Nome do lote deve conter apenas letras, números, hífen e sublinhado.")
    if n < 4:
        raise ValueError("Um lote precisa de pelo menos quatro linhas para treino/avaliação.")
    caminho = config.DADOS_LOTES / f"{nome}.csv"
    if caminho.exists() or caminho.with_suffix(".json").exists():
        raise FileExistsError(f"O lote {nome} já existe; não será sobrescrito.")
    _, _, reserva = dividir_dataset()
    _, usados = carregar_lotes_validados()
    disponiveis = reserva.drop(index=sorted(usados))
    if n > len(disponiveis):
        raise ValueError(
            f"Reserva insuficiente: solicitadas {n} linhas, disponíveis {len(disponiveis)}."
        )
    amostra = disponiveis.sample(n=n, random_state=semente)
    indices = [int(i) for i in amostra.index]
    lote = amostra.reset_index(drop=True)
    if set(lote[config.ALVO]) != {0, 1} or lote[config.ALVO].value_counts().min() < 2:
        raise ValueError("O lote precisa de pelo menos duas mensagens de cada classe.")
    if fator_drift != 1.0:
        lote = aplicar_drift(lote, fator_drift)
    config.DADOS_LOTES.mkdir(parents=True, exist_ok=True)
    validar_spambase(lote)
    conteudo = lote.to_csv(index=False, float_format="%.10g", lineterminator="\n").encode("utf-8")
    metadados = {
        "dataset": "Spambase",
        "sha256_reserva": sha256(config.BASE_RESERVA.read_bytes()),
        "indices_reserva": indices,
        "semente": semente,
        "fator_drift": fator_drift,
        "sha256_csv": sha256(conteudo),
    }
    caminho.write_bytes(conteudo)
    caminho.with_suffix(".json").write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return str(caminho)


def validar_dataframe(df: pd.DataFrame) -> list[str]:
    """Devolve a lista de problemas encontrados (lista vazia = dados válidos)."""
    try:
        validar_spambase(df)
    except ValueError as erro:
        return [str(erro)]
    return []


def listar_lotes() -> list:
    """Arquivos CSV de lotes novos, em ordem alfabética."""
    if not config.DADOS_LOTES.exists():
        return []
    return sorted(config.DADOS_LOTES.glob("*.csv"))


def carregar_lotes_validados() -> tuple[list[pd.DataFrame], set[int]]:
    """Confere a origem dos lotes sintéticos e impede reutilizar a mesma linha da reserva."""
    tabelas, usados = [], set()
    reserva = pd.read_csv(config.BASE_RESERVA)
    hash_reserva = sha256(config.BASE_RESERVA.read_bytes())
    for caminho in listar_lotes():
        tabela = pd.read_csv(caminho)
        validar_spambase(tabela)
        meta = json.loads(caminho.with_suffix(".json").read_text(encoding="utf-8"))
        if not isinstance(meta, dict):
            raise ValueError(f"Metadados inválidos no lote {caminho.name}.")
        indices = meta.get("indices_reserva", [])
        fator = meta.get("fator_drift")
        if (
            not isinstance(indices, list)
            or not isinstance(fator, (int, float))
            or isinstance(fator, bool)
            or not np.isfinite(fator)
            or fator <= 0
        ):
            raise ValueError(f"Índices ou fator de drift inválidos no lote {caminho.name}.")
        if (
            meta.get("dataset") != "Spambase"
            or meta.get("sha256_reserva") != hash_reserva
            or meta.get("sha256_csv") != sha256(caminho.read_bytes())
            or len(indices) != len(tabela)
            or any(type(i) is not int or i < 0 or i >= len(reserva) for i in indices)
            or len(set(indices)) != len(indices)
        ):
            raise ValueError(f"Proveniência ou hash inválido no lote {caminho.name}.")
        if usados.intersection(indices):
            raise ValueError(f"Linhas da reserva reutilizadas no lote {caminho.name}.")
        esperado = aplicar_drift(reserva.loc[indices].reset_index(drop=True), fator)
        if not np.allclose(tabela.to_numpy(), esperado.to_numpy(), rtol=0, atol=1e-8):
            raise ValueError(f"O lote {caminho.name} diverge das linhas de reserva declaradas.")
        usados.update(indices)
        tabelas.append(tabela)
    return tabelas, usados


def preparar_particoes(lotes: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Metade de cada lote treina, a outra metade avalia; as metades são fixas.

    O holdout fixo e as metades de avaliação dos lotes formam a base de avaliação. Assim campeão
    e candidato são comparados no MESMO conjunto, sem treinar nessas linhas de avaliação.
    """
    treino = [pd.read_csv(config.BASE_TREINO)]
    avaliacao = [pd.read_csv(config.BASE_HOLDOUT)]
    validar_spambase(treino[0])
    validar_spambase(avaliacao[0])
    for lote in lotes:
        validar_spambase(lote)
        metade_treino, metade_aval = train_test_split(
            lote, test_size=0.5, stratify=lote[config.ALVO], random_state=SEMENTE_DADOS
        )
        treino.append(metade_treino)
        avaliacao.append(metade_aval)
    treino = pd.concat(treino, ignore_index=True)
    avaliacao = pd.concat(avaliacao, ignore_index=True)
    chaves_treino = set(map(tuple, treino[config.FEATURES].to_numpy()))
    chaves_aval = set(map(tuple, avaliacao[config.FEATURES].to_numpy()))
    if len(chaves_treino) != len(treino) or len(chaves_aval) != len(avaliacao):
        raise ValueError("Há vetores duplicados nos conjuntos preparados para CT.")
    if not chaves_treino.isdisjoint(chaves_aval):
        raise ValueError("Vazamento: treino e avaliação do CT compartilham atributos.")
    return treino, avaliacao


def preparar() -> None:
    lotes, _ = carregar_lotes_validados()
    treino, avaliacao = preparar_particoes(lotes)
    config.DADOS_PROCESSADOS.mkdir(parents=True, exist_ok=True)
    treino.to_csv(config.TREINO_PROCESSADO, index=False, float_format="%.10g", lineterminator="\n")
    avaliacao.to_csv(
        config.AVALIACAO_PROCESSADA, index=False, float_format="%.10g", lineterminator="\n"
    )
    print(f"lotes usados: {len(lotes)}")
    print(f"treino: {len(treino)} linhas | avaliação: {len(avaliacao)} linhas")


def validar_tudo() -> int:
    """Valida todos os CSVs de data/raw/. Devolve o código de saída (0 = tudo certo)."""
    arquivos = [config.BASE_TREINO, config.BASE_HOLDOUT, *listar_lotes()]
    codigo = 0
    for caminho in arquivos:
        problemas = validar_dataframe(pd.read_csv(caminho))
        status = "OK" if not problemas else "FALHOU: " + "; ".join(problemas)
        print(f"{caminho.name}: {status}")
        codigo |= 1 if problemas else 0
    if not codigo:
        try:
            lotes, _ = carregar_lotes_validados()
            preparar_particoes(lotes)
        except (OSError, ValueError, KeyError) as erro:
            print(f"Proveniência/separação dos lotes: FALHOU: {erro}")
            return 1
    return codigo


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else ""
    if comando == "base":
        criar_base()
    elif comando == "preparar":
        preparar()
    elif comando == "validar":
        sys.exit(validar_tudo())
    else:
        print(__doc__)
        sys.exit(2)
