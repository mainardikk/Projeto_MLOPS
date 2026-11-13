"""Testes de contrato da API: formato de entrada e de saída do /predict."""

import pytest
from fastapi.testclient import TestClient

from mlops_demo import config
from mlops_demo.api import app

pytestmark = pytest.mark.api

cliente = TestClient(app)


def test_health_responde_ok():
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


def test_predict_devolve_o_formato_combinado(base_holdout):
    atributos = base_holdout[config.FEATURES].iloc[0].tolist()
    resposta = cliente.post("/predict", json={"atributos": atributos})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"classe", "probabilidade_spam", "versao_codigo"}
    assert corpo["classe"] in {"spam", "legitimo"}
    assert 0.0 <= corpo["probabilidade_spam"] <= 1.0


def test_predict_rejeita_quantidade_errada_de_atributos():
    resposta = cliente.post("/predict", json={"atributos": [1.0, 2.0]})
    assert resposta.status_code == 422


def test_predict_devolve_spam_e_legitimo_nos_casos_de_maior_confianca(base_holdout, campeao):
    """Escolhe os casos mais claros (maior confiança do campeão) de cada classe."""
    X = base_holdout[config.FEATURES]
    coluna = list(campeao.classes_).index(config.CLASSE_SPAM)
    p_spam = campeao.predict_proba(X)[:, coluna]
    i_spam = int(p_spam.argmax())
    i_legitimo = int(p_spam.argmin())
    for indice, esperado in ((i_spam, "spam"), (i_legitimo, "legitimo")):
        resposta = cliente.post("/predict", json={"atributos": X.iloc[indice].tolist()})
        assert resposta.json()["classe"] == esperado


def test_schema_publica_a_ordem_dos_57_atributos():
    resposta = cliente.get("/schema")
    assert resposta.status_code == 200
    assert resposta.json()["atributos"] == config.FEATURES
    assert resposta.json()["quantidade_atributos"] == 57
    assert resposta.json()["classe_positiva"] == 1


@pytest.mark.parametrize(
    ("coluna", "valor"),
    [
        ("word_freq_free", 101),
        ("char_freq_dollar", -1),
        ("capital_run_length_longest", 2.5),
        ("word_freq_money", "1.0"),
        ("word_freq_money", True),
    ],
)
def test_predict_rejeita_atributos_invalidos_do_dominio(base_treino, coluna, valor):
    atributos = base_treino[config.FEATURES].iloc[0].tolist()
    atributos[config.FEATURES.index(coluna)] = valor
    resposta = cliente.post("/predict", json={"atributos": atributos})
    assert resposta.status_code == 422


def test_probabilidade_publicada_corresponde_ao_rotulo_spam_1(base_treino, campeao):
    X = base_treino[config.FEATURES].iloc[[0]]
    resposta = cliente.post("/predict", json={"atributos": X.iloc[0].tolist()})
    coluna = list(campeao.classes_).index(1)
    esperado = float(campeao.predict_proba(X)[0, coluna])
    assert resposta.status_code == 200
    assert resposta.json()["probabilidade_spam"] == pytest.approx(esperado, abs=0.00005)


def test_predict_rejeita_rotulo_fornecido_pelo_cliente(base_treino):
    atributos = base_treino[config.FEATURES].iloc[0].tolist()
    resposta = cliente.post("/predict", json={"atributos": atributos, "spam": 1})
    assert resposta.status_code == 422


def test_predict_rejeita_sequencia_maior_que_total_de_maiusculas(base_treino):
    atributos = base_treino[config.FEATURES].iloc[0].tolist()
    atributos[config.FEATURES.index("capital_run_length_longest")] = 100
    atributos[config.FEATURES.index("capital_run_length_total")] = 1
    assert cliente.post("/predict", json={"atributos": atributos}).status_code == 422
