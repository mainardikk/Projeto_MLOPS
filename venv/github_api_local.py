import os
import subprocess
import requests


def sessao():
    ambiente = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
    resultado = subprocess.run(
        ['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
        capture_output=True, text=True, env=ambiente,
    )
    if resultado.returncode:
        raise RuntimeError('Autenticacao Git local indisponivel; nenhum segredo foi exibido.')
    credencial = dict(linha.split('=', 1) for linha in resultado.stdout.splitlines() if '=' in linha)
    if not credencial.get('password'):
        raise RuntimeError('Credencial sem token para github.com.')
    cliente = requests.Session()
    cliente.headers.update({
        'Authorization': 'Bearer ' + credencial['password'],
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    })
    return cliente
