"""Teste de fumaça HTTP sem dependências externas, também usado no CI e no CD.

python demo/smoke_test.py http://localhost:8000 --aguardar 60
"""

import argparse
import csv
import json
import math
import time
import urllib.error
import urllib.request
from pathlib import Path

HOLDOUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "base_holdout.csv"


def chamar(url: str, caminho: str, corpo: dict | None = None) -> dict:
    dados = json.dumps(corpo, allow_nan=False).encode() if corpo is not None else None
    requisicao = urllib.request.Request(
        url + caminho, data=dados, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(requisicao, timeout=10) as resposta:
        return json.loads(resposta.read())


def verificar(url: str, aguardar: int = 0) -> None:
    limite = time.monotonic() + aguardar
    while True:
        try:
            saude = chamar(url, "/health")
            assert saude["status"] == "ok", saude
            break
        except (OSError, ValueError, AssertionError):
            if time.monotonic() >= limite:
                raise
            time.sleep(0.5)
    print("health ok | versão:", saude["versao_codigo"])
    esquema = chamar(url, "/schema")
    assert esquema["quantidade_atributos"] == 57, esquema
    assert esquema["alvo"] == "spam" and esquema["classe_positiva"] == 1, esquema
    assert len(set(esquema["atributos"])) == 57, esquema
    exemplos = {}
    with open(HOLDOUT, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        assert leitor.fieldnames == [*esquema["atributos"], "spam"], leitor.fieldnames
        for linha in leitor:
            exemplos.setdefault(linha["spam"], linha)
            if len(exemplos) == 2:
                break
    assert set(exemplos) == {"0", "1"}, "Teste de fumaça exige exemplos das duas classes."
    classes = set()
    for linha in exemplos.values():
        atributos = [float(linha[nome]) for nome in esquema["atributos"]]
        predicao = chamar(url, "/predict", {"atributos": atributos})
        assert set(predicao) == {"classe", "probabilidade_spam", "versao_codigo"}, predicao
        assert predicao["classe"] in {"spam", "legitimo"}, predicao
        assert math.isfinite(predicao["probabilidade_spam"]), predicao
        assert 0 <= predicao["probabilidade_spam"] <= 1, predicao
        assert predicao["versao_codigo"] == saude["versao_codigo"], predicao
        classes.add(predicao["classe"])
        print("predict ok |", predicao)
    assert classes == {"spam", "legitimo"}, "Os exemplos fixos devem exercitar as duas respostas."
    invalidos = [float(exemplos["0"][nome]) for nome in esquema["atributos"]]
    invalidos[esquema["atributos"].index("word_freq_free")] = 101.0
    try:
        chamar(url, "/predict", {"atributos": invalidos})
    except urllib.error.HTTPError as erro:
        assert erro.code == 422, erro.code
        print("validação ok | frequência acima de 100% rejeitada com HTTP 422")
    else:
        raise AssertionError("API aceitou frequência de palavra impossível.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default="http://localhost:8000")
    parser.add_argument("--aguardar", type=int, default=0)
    args = parser.parse_args()
    if args.aguardar < 0:
        parser.error("--aguardar deve ser não negativo")
    verificar(args.url.rstrip("/"), args.aguardar)


if __name__ == "__main__":
    main()
