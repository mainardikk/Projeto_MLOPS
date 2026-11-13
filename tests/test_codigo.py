"""Testes de código: funções e pipeline se comportam como o contrato diz."""

import json

import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from mlops_demo import config
from mlops_demo import gate as modulo_gate
from mlops_demo.evaluate import calcular_metricas
from mlops_demo.features import construir_pipeline, separar_xy
from mlops_demo.gate import decidir

pytestmark = pytest.mark.codigo


def test_separar_xy_devolve_57_atributos_e_alvo(base_treino):
    X, y = separar_xy(base_treino)
    assert X.shape == (len(base_treino), 57)
    assert len(y) == len(base_treino)


def test_separar_xy_impoe_a_ordem_das_colunas(base_treino):
    embaralhado = base_treino[list(reversed(base_treino.columns))]
    X, _ = separar_xy(embaralhado)
    assert list(X.columns) == config.FEATURES


def test_separar_xy_falha_quando_falta_coluna(base_treino):
    sem_coluna = base_treino.drop(columns=["word_freq_free"])
    with pytest.raises(ValueError, match="Colunas ausentes"):
        separar_xy(sem_coluna)


def test_separar_xy_nao_altera_o_dataframe_original(base_treino):
    antes = base_treino.copy()
    separar_xy(base_treino)
    pd.testing.assert_frame_equal(base_treino, antes)


def test_pipeline_tem_padronizacao_e_classificador(params):
    pipeline = construir_pipeline(params)
    assert isinstance(pipeline, Pipeline)
    assert [nome for nome, _ in pipeline.steps] == ["logaritmo", "padronizar", "classificador"]


def test_metricas_usam_spam_1_como_classe_positiva():
    # Chutar tudo como spam tem recall 1, mas envia todas as mensagens legítimas para spam.
    y_real = [0, 0, 1, 1]
    metricas = calcular_metricas(y_real, [1, 1, 1, 1])
    assert metricas["recall_spam"] == 1.0
    assert metricas["precisao_spam"] == pytest.approx(0.5)
    assert metricas["falsos_positivos"] == 2


# --- o próprio portão de qualidade precisa ser testado ---------------------------------------


def _metricas(recall, precisao):
    return {"recall_spam": recall, "precisao_spam": precisao, "n_amostras": 100}


def test_gate_aprova_candidato_melhor_e_dentro_dos_limiares():
    assert decidir(_metricas(0.97, 0.95), _metricas(0.95, 0.95))["aprovado"]


def test_gate_reprova_recall_abaixo_do_limiar():
    assert not decidir(_metricas(0.80, 0.99), _metricas(0.80, 0.99))["aprovado"]


def test_gate_reprova_precisao_abaixo_do_limiar():
    # recall perfeito não compensa uma precisão ruim
    assert not decidir(_metricas(1.0, 0.70), _metricas(0.95, 0.95))["aprovado"]


def test_gate_reprova_candidato_pior_que_o_campeao():
    assert not decidir(_metricas(0.95, 0.94), _metricas(0.90, 0.96))["aprovado"]


def test_gate_admite_queda_de_recall_dentro_do_contrato_quando_precisao_melhora():
    assert decidir(_metricas(0.87, 0.97), _metricas(0.92, 0.95))["aprovado"]


def test_metricas_sem_predicoes_de_spam_nao_dividem_por_zero():
    metricas = calcular_metricas([0, 1, 1], [0, 0, 0])
    assert metricas["precisao_spam"] == 0.0
    assert metricas["recall_spam"] == 0.0


@pytest.fixture
def portao_temporario(tmp_path, monkeypatch):
    for atributo in (
        "MODELO_CANDIDATO",
        "MODELO_CAMPEAO",
        "METRICAS_CAMPEAO",
        "AVALIACAO_PROCESSADA",
        "PARAMS",
        "RELATORIO_GATE",
        "RELATORIO_PRESERVACAO",
    ):
        caminho = tmp_path / atributo
        caminho.write_text(f"artefato de teste: {atributo}", encoding="utf-8")
        monkeypatch.setattr(config, atributo, caminho)
    resultado = decidir(_metricas(0.90, 0.96), _metricas(0.88, 0.95))
    resultado["artefatos"] = modulo_gate.hashes_artefatos()
    config.RELATORIO_GATE.write_text(json.dumps(resultado), encoding="utf-8")
    return resultado


def test_portao_reprovado_preserva_modelo_e_metricas_do_campeao(portao_temporario):
    portao_temporario["aprovado"] = False
    config.RELATORIO_GATE.write_text(json.dumps(portao_temporario), encoding="utf-8")
    antes = (config.MODELO_CAMPEAO.read_bytes(), config.METRICAS_CAMPEAO.read_bytes())
    with pytest.raises(SystemExit, match="reprovado"):
        modulo_gate.promover()
    modulo_gate.verificar_campeao()
    assert antes == (config.MODELO_CAMPEAO.read_bytes(), config.METRICAS_CAMPEAO.read_bytes())


def test_promocao_rejeita_candidato_alterado_apos_aprovacao(portao_temporario):
    antes = config.MODELO_CAMPEAO.read_bytes()
    config.MODELO_CANDIDATO.write_bytes(b"outro candidato")
    with pytest.raises(SystemExit, match="Artefatos mudaram"):
        modulo_gate.promover()
    assert config.MODELO_CAMPEAO.read_bytes() == antes


def test_promocao_aprovada_copia_o_candidato_certificado(portao_temporario):
    modulo_gate.promover()
    assert config.MODELO_CAMPEAO.read_bytes() == config.MODELO_CANDIDATO.read_bytes()
    assert json.loads(config.METRICAS_CAMPEAO.read_text(encoding="utf-8"))["classe_positiva"] == 1
