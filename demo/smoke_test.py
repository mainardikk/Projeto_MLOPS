"""Teste de fumaça: chama /health e /predict de uma API em execução (sem dependências externas).

Uso: python demo/smoke_test.py http://localhost:8000
"""

import csv
import json
import sys
import urllib.request
from pathlib import Path

URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
HOLDOUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "base_holdout.csv"


def chamar(caminho: str, corpo: dict | None = None) -> dict:
    dados = json.dumps(corpo).encode() if corpo is not None else None
    requisicao = urllib.request.Request(
        URL + caminho, data=dados, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(requisicao, timeout=10) as resposta:
        return json.loads(resposta.read())


saude = chamar("/health")
assert saude["status"] == "ok", saude
print("health ok | versão:", saude["versao_codigo"])

with open(HOLDOUT, encoding="utf-8") as arquivo:
    linha = next(csv.DictReader(arquivo))
esquema = chamar("/schema")
assert esquema["quantidade_atributos"] == 57, esquema
assert esquema["alvo"] == "spam" and esquema["classe_positiva"] == 1, esquema
atributos = [float(linha[nome]) for nome in esquema["atributos"]]
predicao = chamar("/predict", {"atributos": atributos})
assert predicao["classe"] in {"spam", "legitimo"}, predicao
assert 0 <= predicao["probabilidade_spam"] <= 1, predicao
print("predict ok |", predicao)
