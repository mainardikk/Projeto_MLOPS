"""Pré-processamento e construção do pipeline de modelo."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from mlops_demo.config import ALVO, FEATURES


def separar_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separa atributos e alvo, garantindo as colunas esperadas e a ordem."""
    faltando = [c for c in FEATURES + [ALVO] if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes: {faltando}")
    X = df[FEATURES].copy()
    y = df[ALVO].astype(int)
    return X, y


def construir_pipeline(params: dict) -> Pipeline:
    """Log1p reduz a assimetria das frequências/contagens; o scaler só ajusta no treino."""
    modelo = params["modelo"]
    return Pipeline(
        [
            (
                "logaritmo",
                FunctionTransformer(
                    np.log1p if params["preprocessamento"]["log1p"] else None,
                    feature_names_out="one-to-one",
                ),
            ),
            ("padronizar", StandardScaler()),
            (
                "classificador",
                LogisticRegression(
                    C=modelo["C"],
                    max_iter=modelo["max_iter"],
                    class_weight=modelo["class_weight"],
                    random_state=params["semente"],
                ),
            ),
        ]
    )
