"""Testes de dados: esquema, valores e vazamento entre treino e teste."""

import pandas as pd
import pytest

from mlops_demo import config
from mlops_demo.data import listar_lotes, validar_dataframe
from mlops_demo.spambase import PASTA_SPAMBASE

pytestmark = pytest.mark.dados


def _arquivos_de_dados():
    return [config.BASE_TREINO, config.BASE_HOLDOUT, *listar_lotes()]


@pytest.mark.parametrize("caminho", _arquivos_de_dados(), ids=lambda c: c.name)
def test_arquivo_respeita_esquema_e_valores(caminho):
    problemas = validar_dataframe(pd.read_csv(caminho))
    assert problemas == [], f"{caminho.name}: {problemas}"


def test_base_de_treino_tem_as_duas_classes_em_proporcao_razoavel(base_treino):
    proporcao_spam = (base_treino[config.ALVO] == config.CLASSE_SPAM).mean()
    assert 0.35 <= proporcao_spam <= 0.45


def test_nao_ha_vazamento_entre_treino_e_holdout(base_treino, base_holdout):
    chaves_treino = set(map(tuple, base_treino[config.FEATURES].round(6).to_numpy()))
    chaves_holdout = set(map(tuple, base_holdout[config.FEATURES].round(6).to_numpy()))
    assert chaves_treino.isdisjoint(chaves_holdout)


def test_nao_ha_linhas_duplicadas_na_base_de_treino(base_treino):
    assert not base_treino.duplicated().any()


def test_validador_detecta_nulos(base_treino):
    corrompido = base_treino.copy()
    corrompido.loc[0, "word_freq_free"] = None
    problemas = validar_dataframe(corrompido)
    assert any("nulos" in p for p in problemas)


def test_validador_detecta_frequencia_negativa(base_treino):
    corrompido = base_treino.copy()
    corrompido.loc[0, "char_freq_dollar"] = -5.0
    assert any("entre 0 e 100" in p for p in validar_dataframe(corrompido))


def test_validador_detecta_esquema_diferente(base_treino):
    assert validar_dataframe(base_treino.drop(columns=["word_freq_free"]))


def test_bases_ativas_sao_exatamente_as_particoes_certificadas():
    for caminho in (config.BASE_TREINO, config.BASE_HOLDOUT):
        assert caminho.read_bytes() == (PASTA_SPAMBASE / "preparado" / caminho.name).read_bytes()


def test_reserva_do_ct_nao_aparece_no_treino_nem_no_holdout(base_treino, base_holdout):
    reserva = pd.read_csv(config.BASE_RESERVA)
    chaves = set(map(tuple, reserva[config.FEATURES].to_numpy()))
    for base in (base_treino, base_holdout):
        assert chaves.isdisjoint(set(map(tuple, base[config.FEATURES].to_numpy())))
