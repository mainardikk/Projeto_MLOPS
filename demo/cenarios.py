"""Cenários de prática: cada um aplica uma mudança para você ver o pipeline reagir.

Uso (a partir da raiz do projeto, sempre em uma branch nova):
    python demo/cenarios.py listar
    python demo/cenarios.py aplicar 1

Depois de aplicar: git add -A, git commit, git push e abra o Pull Request.
"""

import sys
from pathlib import Path

import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from mlops_demo import config  # noqa: E402
from mlops_demo.data import carregar_lotes_validados, gerar_lote  # noqa: E402

NOME_LOTE_DEMO = "lote_demo_spam"
N_LOTE_DEMO = 400
FATOR_DRIFT_DEMO = 3.0
SEMENTE_LOTE_DEMO = 1

DESCRICAO = {
    1: "Bug no pré-processamento: remove a última coluna. Esperado: CI falha em test_codigo.",
    2: "Nulos em word_freq_free e char_freq_dollar negativo. CI falha na validação dos dados.",
    3: "Hiperparâmetro ruim (C muito pequeno). Esperado: CI falha em test_modelo (recall).",
    4: "Lote novo com drift. Esperado: CI verde e CT dispara, retreina e o portão aprova.",
    5: "Peso extremo para spam + lote com drift: CI falha em modelo e CT reprova no portão.",
}


def _substituir(arquivo: Path, antigo: str, novo: str) -> None:
    texto = arquivo.read_text(encoding="utf-8")
    if antigo not in texto:
        raise SystemExit(f"Trecho não encontrado em {arquivo.name}. O cenário já foi aplicado?")
    arquivo.write_text(texto.replace(antigo, novo, 1), encoding="utf-8")
    print(f"alterado: {arquivo.relative_to(RAIZ)}")


def cenario_1() -> None:
    _substituir(
        RAIZ / "src" / "mlops_demo" / "features.py",
        "X = df[FEATURES].copy()",
        "X = df[FEATURES[:-1]].copy()",
    )


def cenario_2() -> None:
    caminho = RAIZ / "data" / "raw" / "base_treino.csv"
    df = pd.read_csv(caminho)
    df.loc[0:4, "word_freq_free"] = None
    df.loc[5:7, "char_freq_dollar"] = -10.0
    df.to_csv(caminho, index=False, float_format="%.10g", lineterminator="\n")
    print("alterado: base_treino.csv (5 nulos em word_freq_free; char_freq_dollar negativo)")


def _alterar_modelo(chave: str, valor) -> None:
    caminho = RAIZ / "params.yaml"
    params = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    params["modelo"][chave] = valor
    caminho.write_text(
        yaml.safe_dump(params, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )


def cenario_3() -> None:
    _alterar_modelo("C", 0.0000001)


def cenario_4() -> None:
    caminho = config.DADOS_LOTES / f"{NOME_LOTE_DEMO}.csv"
    if caminho.exists():
        carregar_lotes_validados()
        print("lote de demonstração já existe e foi validado:", caminho.name)
        return
    caminho = gerar_lote(
        NOME_LOTE_DEMO, n=N_LOTE_DEMO, fator_drift=FATOR_DRIFT_DEMO, semente=SEMENTE_LOTE_DEMO
    )
    print("criado:", Path(caminho).name, "(seis frequências promocionais x 3, limitadas a 100%)")


def cenario_5() -> None:
    cenario_4()  # sem drift, um push apenas em params poderia não chegar ao portão do CT
    _alterar_modelo("class_weight", {0: 1.0, 1: 10000.0})


CENARIOS = {1: cenario_1, 2: cenario_2, 3: cenario_3, 4: cenario_4, 5: cenario_5}

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "listar":
        for numero, texto in DESCRICAO.items():
            print(f"{numero}. {texto}")
    elif len(sys.argv) == 3 and sys.argv[1] == "aplicar" and sys.argv[2].isdigit():
        numero = int(sys.argv[2])
        if numero not in CENARIOS:
            raise SystemExit("Cenário inexistente. Use: python demo/cenarios.py listar")
        print(f"Cenário {numero}: {DESCRICAO[numero]}")
        CENARIOS[numero]()
    else:
        print(__doc__)
        sys.exit(2)
