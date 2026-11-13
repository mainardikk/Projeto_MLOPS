"""Treino do candidato: lê data/processed/, treina, avalia e salva o modelo e as métricas.

Uso:
    python -m mlops_demo.train                # treina o CANDIDATO (etapa do pipeline DVC)
    python -m mlops_demo.train --campeao      # treina direto sobre a base e grava o CAMPEÃO
                                              # (uso único, para criar o primeiro campeão)
    python -m mlops_demo.train --validar      # validação cruzada somente na base de treino
    python -m mlops_demo.train --selecionar   # reproduz a busca no treino, sem alterar params
"""

import json
import sys
from copy import deepcopy

import joblib
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from mlops_demo import config
from mlops_demo.evaluate import avaliar, calcular_metricas
from mlops_demo.features import construir_pipeline, separar_xy
from mlops_demo.spambase import sha256, validar_spambase


def treinar(df_treino: pd.DataFrame, params: dict):
    """Treina o pipeline com os hiperparâmetros do params.yaml."""
    validar_spambase(df_treino)
    X, y = separar_xy(df_treino)
    modelo = construir_pipeline(params)
    modelo.fit(X, y)
    return modelo


def validar_treino(df_treino: pd.DataFrame, params: dict) -> dict:
    """Predições fora de cada fold; log1p, scaler e classificador ajustam só nos folds de treino."""
    validar_spambase(df_treino)
    X, y = separar_xy(df_treino)
    folds = StratifiedKFold(
        n_splits=params["validacao"]["n_splits"], shuffle=True, random_state=params["semente"]
    )
    previstos = cross_val_predict(construir_pipeline(params), X, y, cv=folds)
    return dict(
        calcular_metricas(y, previstos),
        metodo="predições fora do fold em validação cruzada estratificada",
        n_splits=params["validacao"]["n_splits"],
        semente=params["semente"],
    )


def conferir_contrato(metricas: dict) -> None:
    if (
        metricas["precisao_spam"] < config.PRECISAO_MINIMA
        or metricas["recall_spam"] < config.RECALL_MINIMO
    ):
        raise ValueError(f"O campeão inicial não cumpre o contrato: {metricas}")


def selecionar_parametros(df_treino: pd.DataFrame, params: dict) -> dict:
    """Busca restrita ao treino; exige margem de recall antes de maximizar a precisão."""
    resultados = []
    for c in params["validacao"]["grade_C"]:
        for peso in params["validacao"]["pesos_classe_legitima"]:
            tentativa = deepcopy(params)
            tentativa["modelo"]["C"] = c
            tentativa["modelo"]["class_weight"] = {0: peso, 1: 1.0}
            metricas = validar_treino(df_treino, tentativa)
            resultados.append(
                {
                    "C": c,
                    "class_weight": tentativa["modelo"]["class_weight"],
                    "precisao_spam": metricas["precisao_spam"],
                    "recall_spam": metricas["recall_spam"],
                }
            )
    elegiveis = [
        r
        for r in resultados
        if r["precisao_spam"] >= config.PRECISAO_MINIMA
        and r["recall_spam"] >= params["validacao"]["recall_selecao_minimo"]
    ]
    if not elegiveis:
        raise ValueError("Nenhuma combinação cumpre os critérios de seleção no treino.")
    escolhido = max(elegiveis, key=lambda r: (r["precisao_spam"], r["recall_spam"], -r["C"]))
    return {"resultados": resultados, "escolhido": escolhido}


def salvar(modelo, metricas: dict, caminho_modelo, caminho_metricas) -> None:
    caminho_modelo.parent.mkdir(parents=True, exist_ok=True)
    caminho_metricas.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, caminho_modelo)
    with open(caminho_metricas, "w", encoding="utf-8", newline="\n") as arquivo:
        json.dump(metricas, arquivo, indent=2, ensure_ascii=False)


def treinar_candidato() -> dict:
    params = config.carregar_params()
    modelo = treinar(pd.read_csv(config.TREINO_PROCESSADO), params)
    metricas = avaliar(modelo, pd.read_csv(config.AVALIACAO_PROCESSADA))
    salvar(modelo, metricas, config.MODELO_CANDIDATO, config.METRICAS_CANDIDATO)
    print("candidato:", json.dumps(metricas, ensure_ascii=False))
    return metricas


def treinar_campeao_inicial() -> dict:
    params = config.carregar_params()
    base = pd.read_csv(config.BASE_TREINO)
    validacao = validar_treino(base, params)
    conferir_contrato(validacao)
    modelo = treinar(base, params)
    metricas = avaliar(modelo, pd.read_csv(config.BASE_HOLDOUT))
    conferir_contrato(metricas)
    metricas["origem"] = "base_treino.csv"
    metricas["dataset"] = "Spambase"
    metricas["classe_positiva"] = config.CLASSE_SPAM
    metricas["validacao_interna"] = validacao
    metricas["params"] = params
    metricas["sha256_treino"] = sha256(config.BASE_TREINO.read_bytes())
    metricas["sha256_holdout"] = sha256(config.BASE_HOLDOUT.read_bytes())
    salvar(modelo, metricas, config.MODELO_CAMPEAO, config.METRICAS_CAMPEAO)
    print("campeão inicial:", json.dumps(metricas, ensure_ascii=False))
    return metricas


if __name__ == "__main__":
    if "--campeao" in sys.argv:
        treinar_campeao_inicial()
    elif "--validar" in sys.argv:
        resultado = validar_treino(pd.read_csv(config.BASE_TREINO), config.carregar_params())
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    elif "--selecionar" in sys.argv:
        resultado = selecionar_parametros(pd.read_csv(config.BASE_TREINO), config.carregar_params())
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        treinar_candidato()
