"""API de inferência (FastAPI) servindo o modelo campeão.

Local:   uvicorn mlops_demo.api:app --reload
Docker:  docker run -p 8000:8000 mlops-demo
"""

import json
import os
from pathlib import Path
from typing import Annotated, Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, field_validator

from mlops_demo import __version__, config
from mlops_demo.spambase import validar_spambase

CAMINHO_MODELO = Path(os.environ.get("MODEL_PATH", config.MODELO_CAMPEAO))
CAMINHO_METRICAS = CAMINHO_MODELO.with_name("metrics.json")

app = FastAPI(title="Filtro de spam — Spambase (CI/CD/CT)", version=__version__)
_modelo = joblib.load(CAMINHO_MODELO)


class Mensagem(BaseModel):
    """Os 57 atributos numéricos do email, na ordem publicada em /schema."""

    model_config = ConfigDict(extra="forbid")
    atributos: list[Annotated[float, Field(strict=True, allow_inf_nan=False)]] = Field(
        min_length=len(config.FEATURES), max_length=len(config.FEATURES)
    )

    @field_validator("atributos")
    @classmethod
    def validar_atributos(cls, valores: list[float]) -> list[float]:
        entrada = pd.DataFrame([valores], columns=config.FEATURES)
        entrada[config.ALVO] = 0  # rótulo auxiliar apenas para reutilizar o contrato de atributos
        validar_spambase(entrada)
        return valores


class Predicao(BaseModel):
    classe: Literal["spam", "legitimo"]
    probabilidade_spam: float = Field(ge=0, le=1)
    versao_codigo: str


@app.get("/health")
def saude() -> dict:
    metricas = {}
    if CAMINHO_METRICAS.exists():
        metricas = json.loads(CAMINHO_METRICAS.read_text(encoding="utf-8"))
    return {"status": "ok", "versao_codigo": __version__, "metricas_do_campeao": metricas}


@app.post("/predict", response_model=Predicao)
def prever(mensagem: Mensagem) -> Predicao:
    entrada = pd.DataFrame([mensagem.atributos], columns=config.FEATURES)
    previsto = int(_modelo.predict(entrada)[0])
    coluna = list(_modelo.classes_).index(config.CLASSE_SPAM)
    p_spam = float(_modelo.predict_proba(entrada)[0][coluna])
    return Predicao(
        classe="spam" if previsto == config.CLASSE_SPAM else "legitimo",
        probabilidade_spam=round(p_spam, 4),
        versao_codigo=__version__,
    )


@app.get("/schema")
def esquema() -> dict:
    return {
        "atributos": config.FEATURES,
        "quantidade_atributos": len(config.FEATURES),
        "alvo": config.ALVO,
        "classe_positiva": config.CLASSE_SPAM,
        "classes": {"0": "legitimo", "1": "spam"},
    }
