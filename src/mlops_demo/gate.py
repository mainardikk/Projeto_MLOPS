"""Portão de qualidade (quality gate): decide se o candidato pode substituir o campeão.

Uso:
    python -m mlops_demo.gate              # avalia candidato x campeão e escreve reports/gate.*
    python -m mlops_demo.gate --promover   # copia o candidato para models/champion/

Código de saída: 0 = aprovado, 1 = reprovado (o workflow do GitHub Actions fica vermelho).
"""

import json
import shutil
import sys

import joblib
import pandas as pd

from mlops_demo import config
from mlops_demo.evaluate import avaliar
from mlops_demo.spambase import sha256


def hashes_artefatos() -> dict:
    return {
        nome: sha256(caminho.read_bytes())
        for nome, caminho in {
            "candidato": config.MODELO_CANDIDATO,
            "campeao": config.MODELO_CAMPEAO,
            "metricas_campeao": config.METRICAS_CAMPEAO,
            "avaliacao": config.AVALIACAO_PROCESSADA,
            "contrato": config.RAIZ / "src" / "mlops_demo" / "config.py",
            "params": config.PARAMS,
        }.items()
    }


def decidir(candidato: dict, campeao: dict) -> dict:
    """Aplica as regras do portão a duas dicts de métricas e devolve o veredito."""
    verificacoes = [
        {
            "regra": f"recall spam do candidato >= {config.RECALL_MINIMO:.2f}",
            "ok": candidato["recall_spam"] >= config.RECALL_MINIMO,
            "valor": round(candidato["recall_spam"], 4),
        },
        {
            "regra": f"precisão spam do candidato >= {config.PRECISAO_MINIMA:.2f}",
            "ok": candidato["precisao_spam"] >= config.PRECISAO_MINIMA,
            "valor": round(candidato["precisao_spam"], 4),
        },
        {
            "regra": "precisão spam do candidato >= precisão do campeão (mesmo conjunto)",
            "ok": candidato["precisao_spam"]
            >= campeao["precisao_spam"] - config.TOLERANCIA_CAMPEAO,
            "valor": f"{candidato['precisao_spam']:.4f} x {campeao['precisao_spam']:.4f}",
        },
    ]
    return {
        "aprovado": all(v["ok"] for v in verificacoes),
        "verificacoes": verificacoes,
        "candidato": candidato,
        "campeao": campeao,
    }


def resumo_markdown(resultado: dict) -> str:
    """Texto em Markdown, usado no GITHUB_STEP_SUMMARY e no corpo do PR."""
    selo = "APROVADO: o candidato pode virar campeão" if resultado["aprovado"] else "REPROVADO"
    linhas = [f"## Portão de qualidade: {selo}", ""]
    linhas += ["| Modelo | Recall spam | Precisão spam | Amostras |", "|---|---|---|---|"]
    for nome in ("campeao", "candidato"):
        m = resultado[nome]
        celulas = [nome, f"{m['recall_spam']:.3f}", f"{m['precisao_spam']:.3f}"]
        linhas.append("| " + " | ".join([*celulas, str(m["n_amostras"])]) + " |")
    linhas += ["", "| Regra | Resultado | Valor |", "|---|---|---|"]
    for v in resultado["verificacoes"]:
        linhas.append(f"| {v['regra']} | {'passou' if v['ok'] else 'FALHOU'} | {v['valor']} |")
    if "artefatos" in resultado:
        linhas += ["", f"SHA-256 do campeão avaliado: `{resultado['artefatos']['campeao']}`"]
    return "\n".join(linhas) + "\n"


def executar() -> int:
    artefatos = hashes_artefatos()
    avaliacao = pd.read_csv(config.AVALIACAO_PROCESSADA)
    candidato = avaliar(joblib.load(config.MODELO_CANDIDATO), avaliacao)
    campeao = avaliar(joblib.load(config.MODELO_CAMPEAO), avaliacao)
    resultado = decidir(candidato, campeao)
    resultado["artefatos"] = artefatos

    config.RELATORIO_GATE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.RELATORIO_GATE, "w", encoding="utf-8", newline="\n") as arquivo:
        json.dump(resultado, arquivo, indent=2, ensure_ascii=False)
    texto = resumo_markdown(resultado)
    config.RESUMO_GATE.write_text(texto, encoding="utf-8")
    print(texto)
    return 0 if resultado["aprovado"] else 1


def promover() -> None:
    """Candidato vira campeão. Em produção, isso vai para um PR revisado por uma pessoa."""
    with open(config.RELATORIO_GATE, encoding="utf-8") as arquivo:
        resultado = json.load(arquivo)
    if not resultado["aprovado"]:
        raise SystemExit("O candidato foi reprovado no portão: promoção bloqueada.")
    if resultado.get("artefatos") != hashes_artefatos():
        raise SystemExit("Artefatos mudaram desde a avaliação: execute novamente o portão.")
    config.MODELO_CAMPEAO.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config.MODELO_CANDIDATO, config.MODELO_CAMPEAO)
    metricas = dict(
        resultado["candidato"],
        origem="treinamento contínuo (CT)",
        dataset="Spambase",
        classe_positiva=config.CLASSE_SPAM,
        sha256_avaliacao=resultado["artefatos"]["avaliacao"],
    )
    with open(config.METRICAS_CAMPEAO, "w", encoding="utf-8", newline="\n") as arquivo:
        json.dump(metricas, arquivo, indent=2, ensure_ascii=False)
    print("Campeão atualizado em", config.MODELO_CAMPEAO)


def verificar_campeao() -> None:
    """Prova que a avaliação, aprovada ou reprovada, preservou modelo e métricas do campeão."""
    resultado = json.loads(config.RELATORIO_GATE.read_text(encoding="utf-8"))
    atuais = {
        "campeao": sha256(config.MODELO_CAMPEAO.read_bytes()),
        "metricas_campeao": sha256(config.METRICAS_CAMPEAO.read_bytes()),
    }
    anteriores = {chave: resultado["artefatos"][chave] for chave in atuais}
    preservado = anteriores == atuais
    config.RELATORIO_PRESERVACAO.write_text(
        json.dumps({"preservado": preservado, "antes": anteriores, "depois": atuais}, indent=2)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not preservado:
        raise SystemExit("O campeão mudou durante a avaliação do candidato.")
    print("Campeão preservado: SHA-256 do modelo e das métricas não mudou.")


if __name__ == "__main__":
    if "--promover" in sys.argv:
        promover()
    elif "--verificar-campeao" in sys.argv:
        verificar_campeao()
    else:
        sys.exit(executar())
