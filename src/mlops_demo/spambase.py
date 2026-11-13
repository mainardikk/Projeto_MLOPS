"""Obtenção e preparação isolada do Spambase; não altera os dados ativos.

python -m mlops_demo.spambase baixar      # única etapa que precisa de internet
python -m mlops_demo.spambase preparar    # limpeza e divisão, sem internet
python -m mlops_demo.spambase verificar   # confere os artefatos, sem gravar arquivos
"""

import argparse
import hashlib
import json
from io import BytesIO
from itertools import combinations
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from sklearn.model_selection import train_test_split

PASTA_SPAMBASE = Path(__file__).resolve().parents[2] / "data" / "spambase"
URL_FONTE = "https://archive.ics.uci.edu/dataset/94/spambase"
URL_DOWNLOAD = "https://archive.ics.uci.edu/static/public/94/spambase.zip"
DOI = "https://doi.org/10.24432/C53G6X"
LICENCA = "https://creativecommons.org/licenses/by/4.0/"
AUTORES = ["Mark Hopkins", "Erik Reeber", "George Forman", "Jaap Suermondt"]
SEMENTE = 42
HASHES_ORIGINAIS = {
    "spambase.data": "b1ef93de71f97714d3d7d4f58fc9f718da7bbc8ac8a150eff2778616a8097b12",
    "spambase.names": "df418fab7923f929237b81efa0987ddfaf2d68cf61291243625aadc684d5ab6a",
}

PALAVRAS = (
    "make address all 3d our over remove internet order mail receive will people report "
    "addresses free business email you credit your font 000 money hp hpl george 650 lab "
    "labs telnet 857 data 415 85 technology 1999 parts pm direct cs meeting original "
    "project re edu table conference"
).split()
# Mesma ordem do arquivo .names. Somente os seis nomes com símbolos são normalizados.
NOMES_CARACTERES = {
    "char_freq_;": "char_freq_semicolon",
    "char_freq_(": "char_freq_parenthesis",
    "char_freq_[": "char_freq_bracket",
    "char_freq_!": "char_freq_exclamation",
    "char_freq_$": "char_freq_dollar",
    "char_freq_#": "char_freq_hash",
}
COLUNAS_MAIUSCULAS = [
    "capital_run_length_average",
    "capital_run_length_longest",
    "capital_run_length_total",
]
FEATURES_SPAMBASE = [
    *(f"word_freq_{palavra}" for palavra in PALAVRAS),
    *NOMES_CARACTERES.values(),
    *COLUNAS_MAIUSCULAS,
]
ALVO_SPAMBASE = "spam"
COLUNAS_SPAMBASE = [*FEATURES_SPAMBASE, ALVO_SPAMBASE]
COLUNAS_FREQUENCIAS = FEATURES_SPAMBASE[:54]
COLUNAS_CONTAGENS = COLUNAS_MAIUSCULAS[1:]
ARQUIVOS_PARTICOES = {
    "treino": "base_treino.csv",
    "holdout": "base_holdout.csv",
    "reserva": "base_reserva.csv",
}


def sha256(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def conferir_original(nome: str, conteudo: bytes) -> None:
    if sha256(conteudo) != HASHES_ORIGINAIS[nome]:
        raise ValueError(f"SHA-256 divergente em {nome}: fonte alterada ou arquivo corrompido.")


def baixar(pasta: Path = PASTA_SPAMBASE) -> None:
    """Baixa o ZIP oficial e só grava os dois arquivos após conferir ambos os hashes."""
    with urlopen(URL_DOWNLOAD, timeout=30) as resposta:
        arquivo_zip = resposta.read()
    with ZipFile(BytesIO(arquivo_zip)) as arquivo:
        originais = {nome: arquivo.read(nome) for nome in HASHES_ORIGINAIS}
    for nome, conteudo in originais.items():
        conferir_original(nome, conteudo)
    destino = pasta / "original"
    destino.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in originais.items():
        (destino / nome).write_bytes(conteudo)


def validar_spambase(df: pd.DataFrame) -> None:
    """Rejeita esquema, tipos e valores incompatíveis com os atributos do Spambase."""
    if list(df.columns) != COLUNAS_SPAMBASE:
        raise ValueError("Esquema Spambase inválido: esperados 57 atributos em ordem e alvo spam.")
    if df.empty:
        raise ValueError("Tabela Spambase vazia.")
    if any(not is_numeric_dtype(df[c]) or is_bool_dtype(df[c]) for c in COLUNAS_SPAMBASE):
        raise ValueError("Todas as colunas devem ter tipo numérico, sem booleanos.")
    if df.isna().any().any() or not np.isfinite(df.to_numpy()).all():
        raise ValueError("Valores nulos ou não finitos no Spambase.")
    if not df[ALVO_SPAMBASE].isin([0, 1]).all():
        raise ValueError("O alvo spam deve pertencer a {0, 1}.")
    frequencias = df[COLUNAS_FREQUENCIAS]
    if ((frequencias < 0) | (frequencias > 100)).any().any():
        raise ValueError("Frequências devem estar entre 0 e 100 por cento.")
    if (df[COLUNAS_MAIUSCULAS] < 1).any().any():
        raise ValueError("Comprimentos de sequências de maiúsculas devem ser pelo menos 1.")
    if (df[COLUNAS_CONTAGENS] % 1 != 0).any().any():
        raise ValueError("Maior sequência e total de maiúsculas devem ser inteiros.")
    media, maior, total = (df[c] for c in COLUNAS_MAIUSCULAS)
    if ((media > maior) | (maior > total)).any():
        raise ValueError("Maiúsculas devem respeitar média <= maior sequência <= total.")


def carregar_original(pasta: Path = PASTA_SPAMBASE) -> pd.DataFrame:
    arquivos = {}
    for nome in HASHES_ORIGINAIS:
        conteudo = (pasta / "original" / nome).read_bytes()
        conferir_original(nome, conteudo)
        arquivos[nome] = conteudo
    nomes = [
        linha.split(":", 1)[0].strip()
        for linha in arquivos["spambase.names"].decode("utf-8").splitlines()
        if ":" in linha and not linha.lstrip().startswith("|")
    ]
    normalizados = [NOMES_CARACTERES.get(nome, nome) for nome in nomes]
    if normalizados != FEATURES_SPAMBASE:
        raise ValueError("Ordem de atributos divergente da documentação original.")
    df = pd.read_csv(BytesIO(arquivos["spambase.data"]), header=None)
    if df.shape != (4601, 58):
        raise ValueError(f"Tamanho inesperado do original: {df.shape}.")
    df.columns = COLUNAS_SPAMBASE
    validar_spambase(df)
    for coluna in [*COLUNAS_CONTAGENS, ALVO_SPAMBASE]:
        df[coluna] = df[coluna].astype("int64")
    return df


def limpar_duplicatas(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Exclui todos os rótulos conflitantes e mantém a primeira ocorrência dos demais."""
    validar_spambase(df)
    conflitos = df.groupby(FEATURES_SPAMBASE, sort=False)[ALVO_SPAMBASE].transform("nunique") > 1
    sem_conflitos = df.loc[~conflitos]
    limpo = sem_conflitos.drop_duplicates(subset=FEATURES_SPAMBASE, keep="first")
    analise = {
        "linhas_originais": len(df),
        "duplicatas_completas_excedentes": int(df.duplicated().sum()),
        "duplicatas_atributos_excedentes": int(df.duplicated(subset=FEATURES_SPAMBASE).sum()),
        "grupos_com_rotulos_conflitantes": len(
            df.loc[conflitos, FEATURES_SPAMBASE].drop_duplicates()
        ),
        "linhas_conflitantes_excluidas": int(conflitos.sum()),
        "linhas_duplicadas_excluidas_apos_conflitos": len(sem_conflitos) - len(limpo),
        "linhas_limpas": len(limpo),
    }
    return limpo.reset_index(drop=True), analise


def dividir_spambase(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Divisão estratificada 60/20/20; a entrada já deve estar limpa de duplicatas."""
    validar_spambase(df)
    if df.duplicated(subset=FEATURES_SPAMBASE).any():
        raise ValueError("Remova duplicatas e conflitos antes de dividir o Spambase.")
    treino, restante = train_test_split(
        df, test_size=0.4, stratify=df[ALVO_SPAMBASE], random_state=SEMENTE
    )
    holdout, reserva = train_test_split(
        restante,
        test_size=0.5,
        stratify=restante[ALVO_SPAMBASE],
        random_state=SEMENTE,
    )
    return {
        nome: tabela.reset_index(drop=True)
        for nome, tabela in (("treino", treino), ("holdout", holdout), ("reserva", reserva))
    }


def conferir_particoes(particoes: dict[str, pd.DataFrame]) -> None:
    chaves = {}
    for nome, df in particoes.items():
        validar_spambase(df)
        if set(df[ALVO_SPAMBASE]) != {0, 1}:
            raise ValueError(f"A partição {nome} deve conter as duas classes.")
        chaves[nome] = set(map(tuple, df[FEATURES_SPAMBASE].to_numpy()))
        if len(chaves[nome]) != len(df):
            raise ValueError(f"Duplicatas na partição {nome}.")
    for a, b in combinations(chaves, 2):
        if not chaves[a].isdisjoint(chaves[b]):
            raise ValueError(f"Sobreposição de atributos entre {a} e {b}.")


def gerar_artefatos(pasta: Path = PASTA_SPAMBASE) -> dict[str, bytes]:
    original = carregar_original(pasta)
    limpo, analise = limpar_duplicatas(original)
    particoes = dividir_spambase(limpo)
    conferir_particoes(particoes)
    artefatos = {
        ARQUIVOS_PARTICOES[nome]: df.to_csv(
            index=False, float_format="%.10g", lineterminator="\n"
        ).encode("utf-8")
        for nome, df in particoes.items()
    }
    manifesto = {
        "dataset": "Spambase",
        "fonte": URL_FONTE,
        "download": URL_DOWNLOAD,
        "doi": DOI,
        "autores": AUTORES,
        "ano": 1999,
        "licenca": {"nome": "CC BY 4.0", "url": LICENCA},
        "sha256_originais": HASHES_ORIGINAIS,
        "semente": SEMENTE,
        "divisao": "60/20/20, estratificada por spam, em duas etapas train_test_split",
        "classe_positiva": 1,
        "atributos_numericos": len(FEATURES_SPAMBASE),
        "valores_nulos_originais": int(original.isna().sum().sum()),
        "classes_originais": original[ALVO_SPAMBASE].value_counts().sort_index().to_dict(),
        "analise_duplicatas": analise,
        "transformacoes": [
            "Normalizar os nomes dos seis atributos char_freq, sem mudar sua ordem.",
            "Excluir todos os registros de grupos de atributos com rótulos conflitantes.",
            "Manter a primeira ocorrência dos demais atributos duplicados.",
            "Converter contagens de maiúsculas e alvo para inteiros; sem imputação ou escala.",
        ],
        "nomes_normalizados": NOMES_CARACTERES,
        "particoes": {
            nome: {
                "arquivo": ARQUIVOS_PARTICOES[nome],
                "linhas": len(df),
                "classes": df[ALVO_SPAMBASE].value_counts().sort_index().to_dict(),
                "proporcao_spam": round(float(df[ALVO_SPAMBASE].mean()), 6),
                "sha256": sha256(artefatos[ARQUIVOS_PARTICOES[nome]]),
            }
            for nome, df in particoes.items()
        },
        "sobreposicoes_entre_particoes": 0,
    }
    artefatos["manifesto.json"] = (
        json.dumps(manifesto, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return artefatos


def preparar(pasta: Path = PASTA_SPAMBASE) -> None:
    artefatos = gerar_artefatos(pasta)
    destino = pasta / "preparado"
    destino.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in artefatos.items():
        (destino / nome).write_bytes(conteudo)


def verificar(pasta: Path = PASTA_SPAMBASE) -> None:
    """Recalcula a preparação e exige igualdade byte a byte com os arquivos publicados."""
    for nome, esperado in gerar_artefatos(pasta).items():
        caminho = pasta / "preparado" / nome
        if caminho.read_bytes() != esperado:
            raise ValueError(f"Artefato divergente da preparação reproduzível: {caminho.name}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comando", choices=["baixar", "preparar", "verificar"])
    comando = parser.parse_args().comando
    try:
        {"baixar": baixar, "preparar": preparar, "verificar": verificar}[comando]()
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Spambase: {erro}\n")
    print(f"Spambase: {comando} concluído. Dados ativos em data/raw/ preservados.")


if __name__ == "__main__":
    main()
