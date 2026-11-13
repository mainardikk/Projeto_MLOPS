"""Configuração central do projeto: caminhos, nomes de colunas e limiares de qualidade."""

from pathlib import Path

import yaml

from mlops_demo.spambase import ALVO_SPAMBASE, FEATURES_SPAMBASE, PASTA_SPAMBASE

RAIZ = Path(__file__).resolve().parents[2]

# dados
DADOS_BRUTOS = RAIZ / "data" / "raw"
DADOS_LOTES = DADOS_BRUTOS / "lotes"
DADOS_PROCESSADOS = RAIZ / "data" / "processed"
BASE_TREINO = DADOS_BRUTOS / "base_treino.csv"
BASE_HOLDOUT = DADOS_BRUTOS / "base_holdout.csv"
BASE_RESERVA = PASTA_SPAMBASE / "preparado" / "base_reserva.csv"
TREINO_PROCESSADO = DADOS_PROCESSADOS / "treino.csv"
AVALIACAO_PROCESSADA = DADOS_PROCESSADOS / "avaliacao.csv"

# modelos e relatórios
MODELO_CAMPEAO = RAIZ / "models" / "champion" / "model.joblib"
METRICAS_CAMPEAO = RAIZ / "models" / "champion" / "metrics.json"
MODELO_CANDIDATO = RAIZ / "models" / "candidate" / "model.joblib"
METRICAS_CANDIDATO = RAIZ / "reports" / "candidate_metrics.json"
RELATORIO_GATE = RAIZ / "reports" / "gate.json"
RESUMO_GATE = RAIZ / "reports" / "gate.md"
RELATORIO_DRIFT = RAIZ / "reports" / "drift.md"
RELATORIO_DRIFT_JSON = RAIZ / "reports" / "drift.json"
RELATORIO_PRESERVACAO = RAIZ / "reports" / "champion_preservation.json"
PARAMS = RAIZ / "params.yaml"

# esquema dos dados
FEATURES = FEATURES_SPAMBASE.copy()
ALVO = ALVO_SPAMBASE
CLASSE_SPAM = 1
COLUNAS_INDICIOS_SPAM = [
    "word_freq_free",
    "word_freq_money",
    "char_freq_dollar",
    "char_freq_exclamation",
]
COLUNAS_DRIFT = [*COLUNAS_INDICIOS_SPAM, "word_freq_you", "word_freq_your"]

# limiares de qualidade (o "contrato" do modelo). Mudar aqui exige revisão em PR.
RECALL_MINIMO = 0.85
PRECISAO_MINIMA = 0.93
TOLERANCIA_CAMPEAO = 0.0  # a precisão do candidato não pode cair em relação ao campeão
PISO_RECALL_SANIDADE = 0.80
PISO_PRECISAO_SANIDADE = 0.90
LIMITE_DRIFT_P = 0.01  # p-valor do teste KS
MIN_FEATURES_DRIFT = 4  # gatilho entre os 57 atributos; quatro alterações disparam o CT


def carregar_params() -> dict:
    """Lê o params.yaml (hiperparâmetros e semente)."""
    with open(PARAMS, encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo)
