"""Spambase: ativação da base reproduzível, validação e preparação do CT.

Uso na linha de comando:
    python -m mlops_demo.data base      # cria base_treino.csv e base_holdout.csv (uma vez)
    python -m mlops_demo.data preparar  # junta base + lotes e gera data/processed/
    python -m mlops_demo.data validar   # valida todos os CSVs de data/raw/
"""

import re
import shutil
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from mlops_demo import config
from mlops_demo.spambase import PASTA_SPAMBASE, SEMENTE, validar_spambase, verificar

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


def gerar_lote(nome: str, n: int = 120, fator_drift: float = 1.0, semente: int = 1) -> str:
    """Cria data/raw/lotes/<nome>.csv a partir da reserva, opcionalmente com drift."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", nome):
        raise ValueError("Nome do lote deve conter apenas letras, números, hífen e sublinhado.")
    if n < 4:
        raise ValueError("Um lote precisa de pelo menos quatro linhas para treino/avaliação.")
    _, _, reserva = dividir_dataset()
    lote = reserva.sample(n=min(n, len(reserva)), random_state=semente).reset_index(drop=True)
    if fator_drift != 1.0:
        lote = aplicar_drift(lote, fator_drift)
    config.DADOS_LOTES.mkdir(parents=True, exist_ok=True)
    caminho = config.DADOS_LOTES / f"{nome}.csv"
    if caminho.exists():
        raise FileExistsError(f"O lote {nome} já existe; não será sobrescrito.")
    validar_spambase(lote)
    lote.to_csv(caminho, index=False, float_format="%.10g", lineterminator="\n")
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


def preparar() -> None:
    """Junta a base com os lotes. Metade de cada lote treina, a outra metade avalia.

    O holdout fixo e as metades de avaliação dos lotes formam a base de avaliação. Assim campeão
    e candidato são comparados no MESMO conjunto, e o campeão nunca viu esses dados.
    """
    treino = [pd.read_csv(config.BASE_TREINO)]
    avaliacao = [pd.read_csv(config.BASE_HOLDOUT)]
    validar_spambase(treino[0])
    validar_spambase(avaliacao[0])
    for caminho in listar_lotes():
        lote = pd.read_csv(caminho)
        validar_spambase(lote)
        metade_treino, metade_aval = train_test_split(
            lote, test_size=0.5, stratify=lote[config.ALVO], random_state=SEMENTE_DADOS
        )
        treino.append(metade_treino)
        avaliacao.append(metade_aval)
    config.DADOS_PROCESSADOS.mkdir(parents=True, exist_ok=True)
    pd.concat(treino, ignore_index=True).to_csv(
        config.TREINO_PROCESSADO, index=False, float_format="%.10g", lineterminator="\n"
    )
    pd.concat(avaliacao, ignore_index=True).to_csv(
        config.AVALIACAO_PROCESSADA, index=False, float_format="%.10g", lineterminator="\n"
    )
    print(f"lotes usados: {len(listar_lotes())}")
    n_treino = sum(len(t) for t in treino)
    n_avaliacao = sum(len(a) for a in avaliacao)
    print(f"treino: {n_treino} linhas | avaliação: {n_avaliacao} linhas")


def validar_tudo() -> int:
    """Valida todos os CSVs de data/raw/. Devolve o código de saída (0 = tudo certo)."""
    arquivos = [config.BASE_TREINO, config.BASE_HOLDOUT, *listar_lotes()]
    codigo = 0
    for caminho in arquivos:
        problemas = validar_dataframe(pd.read_csv(caminho))
        status = "OK" if not problemas else "FALHOU: " + "; ".join(problemas)
        print(f"{caminho.name}: {status}")
        codigo |= 1 if problemas else 0
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
