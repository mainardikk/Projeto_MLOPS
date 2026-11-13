"""Precisão (principal) e recall da classe positiva spam, rótulo 1."""

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score

from mlops_demo.config import CLASSE_SPAM
from mlops_demo.features import separar_xy
from mlops_demo.spambase import validar_spambase


def calcular_metricas(y_real, y_previsto) -> dict:
    """Falso positivo significa mensagem legítima enviada para spam."""
    tn, fp, fn, tp = confusion_matrix(y_real, y_previsto, labels=[0, 1]).ravel()
    return {
        "precisao_spam": float(
            precision_score(y_real, y_previsto, pos_label=CLASSE_SPAM, zero_division=0)
        ),
        "recall_spam": float(
            recall_score(y_real, y_previsto, pos_label=CLASSE_SPAM, zero_division=0)
        ),
        "acuracia": float(accuracy_score(y_real, y_previsto)),
        "n_amostras": int(len(y_real)),
        "verdadeiros_negativos": int(tn),
        "falsos_positivos": int(fp),
        "falsos_negativos": int(fn),
        "verdadeiros_positivos": int(tp),
    }


def avaliar(modelo, df: pd.DataFrame) -> dict:
    """Avalia um modelo treinado em um DataFrame com as colunas do projeto."""
    validar_spambase(df)
    X, y = separar_xy(df)
    return calcular_metricas(y, modelo.predict(X))
