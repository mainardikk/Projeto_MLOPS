"""Gera ADAPTACAO.pdf em duas páginas a partir do Markdown do NOVO repositório.

Preparação: python -m pip install markdown-it-py pypdf
Uso, dentro do novo clone:
    python gerar_relatorio.py --repositorio https://github.com/DONO/NOVO_REPO
"""

import argparse
import html
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


def normalizar_repositorio(valor: str) -> str:
    if valor.startswith("git@github.com:"):
        valor = "https://github.com/" + valor.split(":", 1)[1]
    valor = valor.rstrip("/")
    if valor.endswith(".git"):
        valor = valor[:-4]
    url = urlsplit(valor)
    partes = url.path.strip("/").split("/")
    if (
        url.scheme != "https"
        or url.netloc.lower() != "github.com"
        or len(partes) != 2
        or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", parte) for parte in partes)
    ):
        raise ValueError("Use a URL HTTPS de um repositório do GitHub, sem token.")
    return "https://github.com/" + "/".join(partes)


def localizar_navegador() -> str:
    candidatos = [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
        / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
        / "Microsoft/Edge/Application/msedge.exe",
    ]
    for candidato in candidatos:
        if candidato.is_file():
            return str(candidato)
    for nome in ("google-chrome", "chromium", "chromium-browser"):
        executavel = shutil.which(nome)
        if executavel:
            return executavel
    raise RuntimeError("Chrome ou Edge não encontrado. Instale um navegador antes de exportar.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repositorio", required=True)
    args = parser.parse_args()
    repositorio = normalizar_repositorio(args.repositorio)
    raiz = Path.cwd()
    resultado = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
    )
    origem = normalizar_repositorio(resultado.stdout.strip())
    if origem.lower() != repositorio.lower():
        raise ValueError("O origin desta pasta não é o novo repositório informado. Confira o clone.")
    markdown = (raiz / "ADAPTACAO.md").read_text(encoding="utf-8")
    if repositorio.lower() != "https://github.com/mainardikk/projeto_mlops":
        for antigo in (
            "https://github.com/mainardikk/Projeto_MLOPS/actions/runs/",
            "ghcr.io/mainardikk/projeto_mlops:",
        ):
            if antigo in markdown:
                raise ValueError("Ainda há evidência ou imagem do repositório antigo no relatório.")

    from markdown_it import MarkdownIt
    from pypdf import PdfReader

    corpo = MarkdownIt("commonmark", {"html": True}).enable("table").render(markdown)
    css = """
    @page { size: A4; margin: 12mm 13mm; }
    body { font: 10pt/1.22 Arial, sans-serif; color: #18212b; margin: 0; }
    h1 { font-size: 16pt; line-height: 1.15; margin: 0 0 4mm; }
    h2 { font-size: 11.3pt; margin: 3.3mm 0 1.6mm; break-after: avoid; }
    p { margin: 1.5mm 0; }
    table { width: 100%; border-collapse: collapse; font-size: 8.7pt; margin: 2mm 0; }
    th,td { text-align: left; vertical-align: top; padding: 1.1mm 1.5mm;
            border: 0.2mm solid #ccd2d8; }
    th { background: #edf2f7; }
    tr { break-inside: avoid; }
    a { color: #075895; text-decoration: none; }
    code { font-family: Consolas, monospace; font-size: 8.4pt; overflow-wrap: anywhere; }
    .quebra-pagina { break-before: page; }
    """
    pagina = (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        f'<base href="{html.escape(repositorio + "/blob/main/", quote=True)}">'
        "<title>Relatorio de adaptacao - Spambase</title>"
        f"<style>{css}</style></head><body>{corpo}</body></html>"
    )
    pasta_relatorios = raiz / "reports"
    pasta_relatorios.mkdir(exist_ok=True)
    caminho_html = pasta_relatorios / "adaptacao-impressao.html"
    caminho_html.write_text(pagina, encoding="utf-8", newline="\n")
    perfil = raiz / "venv" / "impressao"
    perfil.mkdir(parents=True, exist_ok=True)
    pdf = raiz / "ADAPTACAO.pdf"
    comando = [
        localizar_navegador(),
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-component-update",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-pdf-header-footer",
        "--user-data-dir=" + str(perfil),
        "--print-to-pdf=" + str(pdf),
        caminho_html.as_uri(),
    ]
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=45,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if resultado.returncode:
        raise RuntimeError("Falha ao exportar PDF: " + resultado.stderr[-1000:])
    leitor = PdfReader(pdf)
    if len(leitor.pages) != 2:
        raise ValueError(
            f"O relatório gerou {len(leitor.pages)} páginas. Compacte a redação para caber em duas."
        )
    for folha in leitor.pages:
        for anotacao in folha.get("/Annots", []):
            acao = anotacao.get_object().get("/A", {})
            uri = acao.get("/URI")
            if uri and not str(uri).startswith("https://"):
                raise ValueError("Link não portátil no PDF: " + str(uri))
    print("ADAPTACAO.pdf gerado: duas páginas A4, com links HTTPS.")


if __name__ == "__main__":
    main()
