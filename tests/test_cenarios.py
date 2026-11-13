"""Executa os cinco cenários em cópias temporárias, sem corromper o projeto ativo."""

import importlib.util
import json
import shutil

import pandas as pd
import pytest
import yaml

from mlops_demo import config
from mlops_demo.data import carregar_lotes_validados, preparar_particoes, validar_dataframe
from mlops_demo.evaluate import avaliar
from mlops_demo.gate import decidir
from mlops_demo.spambase import sha256
from mlops_demo.train import treinar


@pytest.fixture
def cenarios_isolados(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("cenarios_demo", config.RAIZ / "demo/cenarios.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    for relativo in ("params.yaml", "src/mlops_demo/features.py", "data/raw/base_treino.csv"):
        destino = tmp_path / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config.RAIZ / relativo, destino)
    monkeypatch.setattr(modulo, "RAIZ", tmp_path)
    monkeypatch.setattr(config, "DADOS_LOTES", tmp_path / "data/raw/lotes")
    return modulo, tmp_path


@pytest.mark.codigo
def test_cenario_1_remove_um_atributo_real_do_spambase(cenarios_isolados, base_treino):
    modulo, raiz = cenarios_isolados
    modulo.cenario_1()
    spec = importlib.util.spec_from_file_location(
        "features_com_bug", raiz / "src/mlops_demo/features.py"
    )
    features = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(features)
    X, _ = features.separar_xy(base_treino)
    assert X.shape[1] == 56
    assert "capital_run_length_total" not in X.columns


@pytest.mark.dados
def test_cenario_2_corrompe_as_colunas_do_novo_dominio(cenarios_isolados):
    modulo, raiz = cenarios_isolados
    modulo.cenario_2()
    corrompido = pd.read_csv(raiz / "data/raw/base_treino.csv")
    assert corrompido["word_freq_free"].isna().sum() == 5
    assert (corrompido["char_freq_dollar"] < 0).sum() == 3
    assert validar_dataframe(corrompido)


@pytest.mark.modelo
def test_cenario_3_reprova_o_recall_por_regularizacao_extrema(
    cenarios_isolados, base_treino, base_holdout
):
    modulo, raiz = cenarios_isolados
    modulo.cenario_3()
    params = yaml.safe_load((raiz / "params.yaml").read_text(encoding="utf-8"))
    metricas = avaliar(treinar(base_treino, params), base_holdout)
    assert metricas["recall_spam"] < config.RECALL_MINIMO


@pytest.mark.dados
def test_cenario_4_cria_lote_reproduzivel_e_nao_o_sobrescreve(cenarios_isolados):
    modulo, _ = cenarios_isolados
    modulo.cenario_4()
    caminho = config.DADOS_LOTES / "lote_demo_spam.csv"
    antes = caminho.read_bytes()
    modulo.cenario_4()
    assert caminho.read_bytes() == antes
    meta = json.loads(caminho.with_suffix(".json").read_text(encoding="utf-8"))
    assert meta["sha256_csv"] == sha256(antes)
    assert len(meta["indices_reserva"]) == 400
    assert meta["fator_drift"] == 3.0


@pytest.mark.modelo
def test_cenario_5_recall_alto_nao_compensa_precisao_baixa(cenarios_isolados, campeao):
    modulo, raiz = cenarios_isolados
    hash_antes = sha256(config.MODELO_CAMPEAO.read_bytes())
    modulo.cenario_5()
    params = yaml.safe_load((raiz / "params.yaml").read_text(encoding="utf-8"))
    lotes, _ = carregar_lotes_validados()
    treino, avaliacao = preparar_particoes(lotes)
    metricas = avaliar(treinar(treino, params), avaliacao)
    assert metricas["recall_spam"] >= 0.99
    assert metricas["precisao_spam"] < config.PRECISAO_MINIMA
    assert not decidir(metricas, avaliar(campeao, avaliacao))["aprovado"]
    assert sha256(config.MODELO_CAMPEAO.read_bytes()) == hash_antes
