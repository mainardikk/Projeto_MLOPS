"""Detecção de drift: compara os lotes novos com a base de treino (teste KS por atributo).

Uso:
    python -m mlops_demo.monitor

Escreve reports/drift.md e, quando roda no GitHub Actions, publica a saída `retreinar`
(true ou false) em $GITHUB_OUTPUT para o workflow decidir se dispara o retreino.
"""

import json
import os

import pandas as pd
from scipy.stats import ks_2samp

from mlops_demo import config
from mlops_demo.data import carregar_lotes_validados, listar_lotes
from mlops_demo.spambase import validar_spambase


def detectar_drift(base: pd.DataFrame, novo: pd.DataFrame) -> pd.DataFrame:
    """Teste KS (duas amostras) em cada atributo. Marca drift quando p < LIMITE_DRIFT_P."""
    validar_spambase(base)
    validar_spambase(novo)
    linhas = []
    for coluna in config.FEATURES:
        estatistica, p_valor = ks_2samp(base[coluna], novo[coluna])
        linhas.append(
            {
                "atributo": coluna,
                "ks": round(float(estatistica), 3),
                "p_valor": float(p_valor),
                "drift": bool(p_valor < config.LIMITE_DRIFT_P),
            }
        )
    return pd.DataFrame(linhas).sort_values("ks", ascending=False).reset_index(drop=True)


def deve_retreinar(n_features_drift: int) -> bool:
    """Gatilho do CT por evento: drift em MIN_FEATURES_DRIFT atributos ou mais."""
    return n_features_drift >= config.MIN_FEATURES_DRIFT


def executar() -> bool:
    lotes = listar_lotes()
    registros = []
    if not lotes:
        texto = "## Drift\n\nNenhum lote novo em `data/raw/lotes/`. Nada a comparar.\n"
        n_drift = 0
    else:
        base = pd.read_csv(config.BASE_TREINO)
        tabelas, _ = carregar_lotes_validados()
        novo = pd.concat(tabelas, ignore_index=True)
        tabela = detectar_drift(base, novo)
        registros = tabela.to_dict(orient="records")
        n_drift = int(tabela["drift"].sum())
        marcados = tabela[tabela["drift"]].head(10)
        texto = (
            f"## Drift: {n_drift} de {len(config.FEATURES)} atributos\n\n"
            f"Lotes comparados: {', '.join(c.name for c in lotes)} ({len(novo)} linhas)\n\n"
            "| Atributo | KS | p-valor |\n|---|---|---|\n"
            + "\n".join(
                f"| {r.atributo} | {r.ks} | {r.p_valor:.1e} |" for r in marcados.itertuples()
            )
            + "\n"
        )
    retreinar = deve_retreinar(n_drift)
    texto += (
        f"\nGatilho (>= {config.MIN_FEATURES_DRIFT} atributos com drift): "
        f"{'DISPARADO, retreinar' if retreinar else 'não disparado'}\n"
    )
    config.RELATORIO_DRIFT.parent.mkdir(parents=True, exist_ok=True)
    config.RELATORIO_DRIFT.write_text(texto, encoding="utf-8")
    config.RELATORIO_DRIFT_JSON.write_text(
        json.dumps(
            {
                "lotes": [c.name for c in lotes],
                "atributos_drift": n_drift,
                "minimo_atributos": config.MIN_FEATURES_DRIFT,
                "limite_p": config.LIMITE_DRIFT_P,
                "retreinar": retreinar,
                "atributos": registros,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(texto)
    saida = os.environ.get("GITHUB_OUTPUT")
    if saida:
        with open(saida, "a", encoding="utf-8") as arquivo:
            arquivo.write(f"retreinar={'true' if retreinar else 'false'}\n")
    return retreinar


if __name__ == "__main__":
    executar()
