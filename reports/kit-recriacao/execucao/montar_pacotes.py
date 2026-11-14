"""Monta os seis kits pessoais e verifica patches sem criar commits ou fazer push."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import zipfile


ROOT = Path(__file__).resolve().parent.parent
SOURCE_REPO = ROOT.parent.parent
SOURCE_KIT = ROOT / "execucao/kit-original/reports/kit-recriacao"
OUT = ROOT / "pacotes-individuais"
REMOTE = "https://github.com/thalescr77/Projeto_MLOPS"
PEOPLE = [
    (1, "Thales", "Thales Serschon", "thalescr77", "01-base-original.zip"),
    (2, "Bruno", "Bruno Mainardi", "mainardikk", "02-dados.patch"),
    (3, "Jhonatan", "Jhonatan Margraf", "Jhonatan-Margraf", "03-adaptacao-spam.patch"),
    (4, "Davi", "Davi Specia", "davispecia", "04-pipelines-drift.patch"),
    (5, "Kaique", "Kaique Geska", "kaiquegeska", "05-falha-controlada.patch"),
    (6, "Victor", "Victor Ibarrola", "VictorOliveiraIbarrola", "06-documentacao.patch"),
]
MESSAGES = {
    1: "chore: adiciona base original de CI/CD/CT para ML",
    2: "feat: prepara Spambase reproduzivel sem vazamento de dados",
    3: "feat: adapta modelo API e contrato para classificacao de spam",
    4: "feat: reforca pipelines e demonstra CT com drift por PR",
    5: "test: registra falha controlada e protecao do campeao",
    6: "docs: finaliza relatorio evidencias e instrucoes de entrega",
}


def clean(value: str) -> str:
    return textwrap.dedent(value).strip() + "\n"


def block(value: str) -> str:
    return "\n```powershell\n" + clean(value) + "```\n\n"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={cwd.as_posix()}", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def introduction(number: int, short: str, name: str, login: str, payload: str) -> str:
    prerequisites = {
        1: "Comece com o repositório público e vazio, criado pelo Thales.",
        2: "Comece depois que Thales publicar a etapa 1 e o CI ficar verde.",
        3: "Comece depois que Bruno publicar a etapa 2 e o CI ficar verde.",
        4: "Comece depois que Jhonatan publicar a etapa 3 e o CI ficar verde.",
        5: "Comece depois que Davi concluir a etapa 4, incluindo CI, CT, tag e publicação pública.",
        6: "Comece depois que Kaique conferir E2/E4 e fechar o PR de falha sem merge.",
    }
    value = clean(f"""
        # Etapa {number} — {name}

        Repositório de entrega: [{REMOTE}]({REMOTE}).
        Sua conta: **`{login}`**. Execute esta etapa no seu PC, autenticado nessa conta.

        {prerequisites[number]}

        Este pacote contém `{payload}`, este tutorial, ajuda e um manifesto de integridade.
        Os arquivos foram reaproveitados da base do grupo. Sua parte é revisar, executar,
        validar e criar seu próprio commit. Mantenham a declaração de reaproveitamento e IA.

        ## 1. Abrir o pacote e conferir os programas

        Extraia o ZIP recebido. No Explorador do Windows, abra a pasta que contém este
        `LEIA-PRIMEIRO.md` e `{payload}` e escolha **Abrir no Terminal**, usando PowerShell.
        Os comandos abaixo usam Windows, Git e Python 3.11. Docker local é opcional.

        Execute um bloco por vez, na mesma janela do PowerShell. Se um comando falhar,
        pare e leia `AJUDA.md`. Na etapa 5, as falhas esperadas de CI/CT estão indicadas.
        Não avance para o próximo integrante antes das conferências finais desta etapa.
    """)
    value += block(f"""
        $ErrorActionPreference = "Stop"
        $kit = (Get-Location).Path
        if (-not (Test-Path -LiteralPath (Join-Path $kit "{payload}"))) {{
            throw "Abra o PowerShell na pasta extraida que contem o arquivo da sua etapa."
        }}
        git --version
        if ($LASTEXITCODE -ne 0) {{ throw "Instale o Git e reabra o terminal." }}
        py -3.11 --version
        if ($LASTEXITCODE -ne 0) {{ throw "Instale o Python 3.11 e reabra o terminal." }}
    """)
    value += clean("""
        ## 2. Preparar uma pasta nova e sua identidade

        O clone ficará em `Documentos/MLOPS-ENTREGA`, separado dos arquivos deste pacote.
        Se a pasta do clone já existir, pare e escolha outro nome: não apague trabalho anterior.
    """)
    value += block(f"""
        $trabalho = Join-Path $env:USERPROFILE "Documents\\MLOPS-ENTREGA"
        New-Item -ItemType Directory -Path $trabalho -Force | Out-Null
        $repo = Join-Path $trabalho "MLOPS_{short.upper()}"
        if (Test-Path -LiteralPath $repo) {{
            throw "A pasta do clone ja existe. Escolha outra pasta antes de continuar."
        }}
    """)
    if number == 1:
        value += block(f"""
            New-Item -ItemType Directory -Path $repo | Out-Null
            Set-Location -LiteralPath $repo
            git init -b main
            if ($LASTEXITCODE -ne 0) {{ throw "Falha ao inicializar o repositorio." }}
            git remote add origin {REMOTE}.git
            if ($LASTEXITCODE -ne 0) {{ throw "Falha ao configurar origin." }}
            Expand-Archive -LiteralPath (Join-Path $kit "{payload}") -DestinationPath .
        """)
    else:
        value += block(f"""
            git clone {REMOTE}.git "$repo"
            if ($LASTEXITCODE -ne 0) {{ throw "O clone falhou; confira o acesso ao repositorio." }}
            Set-Location -LiteralPath $repo
        """)
    value += clean(f"""
        Informe um email **verificado na sua conta `{login}`**, ou o endereço `noreply`
        mostrado no GitHub em **Settings > Emails**. O nome/email abaixo definem a autoria;
        a autenticação para publicar será feita separadamente pelo Git.
    """)
    if number == 1:
        value += "\nO email informado pelo grupo para Thales é `thales.serschon17.10@gmail.com`; confirme que está vinculado à sua conta.\n"
    value += block(f"""
        $emailGit = Read-Host "Seu email verificado no GitHub (ou noreply)"
        if ($emailGit -notmatch '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$') {{
            throw "Email invalido. Confira em GitHub > Settings > Emails."
        }}
        git config --local user.name "{name}"
        git config --local user.email "$emailGit"
        git config --local user.useConfigOnly true
        git config --local core.autocrlf false
        git config --local credential.https://github.com.username {login}
        git config --local --get user.name
        git config --local --get user.email
        git remote -v
    """)
    if number != 1:
        value += block("""
            git switch main
            if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel entrar na main." }
            git pull --ff-only origin main
            if ($LASTEXITCODE -ne 0) { throw "Pare e revise a base antes de aplicar o patch." }
            git status --short
        """)
        value += "A saída de `git status --short` deve estar vazia antes de aplicar o patch.\n"
    return value + "\n## 3. Aplicar e validar sua etapa\n\n"


def apply_patch(payload: str) -> str:
    return block(f"""
        git apply --index --whitespace=nowarn (Join-Path $kit "{payload}")
        if ($LASTEXITCODE -ne 0) {{ throw "O patch falhou. Pare; nao reaplique parcialmente." }}
    """)


def environment(constraints: bool = False) -> str:
    install = '-c constraints.txt -e ".[dev,ct]"' if constraints else '-e ".[dev,ct]"'
    return block(f"""
        py -3.11 -m venv .venv
        if ($LASTEXITCODE -ne 0) {{ throw "Falha ao criar o ambiente Python 3.11." }}
        .\\.venv\\Scripts\\python.exe -m pip install {install}
        if ($LASTEXITCODE -ne 0) {{ throw "A instalacao falhou; nao continue." }}
    """)


def ci() -> str:
    return block("""
        .\.venv\Scripts\python.exe demo/local.py ci
        if ($LASTEXITCODE -ne 0) { throw "CI local reprovado. Resolva antes de commitar." }
    """)


def commit(number: int, files: str = "--all", remote_branch: str = "main", section: int = 4) -> str:
    add = f"git add {files}"
    push = f"git push {'-u ' if remote_branch != 'main' or number == 1 else ''}origin {remote_branch}"
    value = f"\n## {section}. Revisar, criar seu commit e publicar\n\n"
    value += "Confira os arquivos e a identidade antes de publicar. O nome/email devem ser os seus.\n"
    value += block(f"""
        {add}
        if ($LASTEXITCODE -ne 0) {{ throw "Falha ao preparar os arquivos." }}
        git diff --cached --stat
        git diff --cached --check
        if ($LASTEXITCODE -ne 0) {{ throw "Revise os problemas indicados no diff." }}
        git config --local --get user.name
        git config --local --get user.email
    """)
    value += "Depois de revisar a saída, execute:\n"
    value += block(f"""
        git commit -m "{MESSAGES[number]}"
        if ($LASTEXITCODE -ne 0) {{ throw "O commit falhou; nao execute o push." }}
        git log -1 --format="%h | %an | %ae | %s"
        {push}
        if ($LASTEXITCODE -ne 0) {{ throw "O push falhou. Confira a conta e o convite; nao use force." }}
    """)
    return value


def tutorial(person: tuple[int, str, str, str, str]) -> str:
    number, short, name, login, payload = person
    value = introduction(*person)
    if number == 1:
        value += environment() + ci() + commit(1)
        value += clean(f"""
            ## 5. Conferir no GitHub e liberar Bruno

            1. Se o Git pedir autenticação, entre na conta **`{login}`** no seu PC.
            2. Abra [Actions]({REMOTE}/actions) e aguarde o CI deste commit. Os três jobs
               devem ficar verdes: lint e testes em Python 3.11 e 3.12.
            3. Abra o commit no GitHub e confira a associação ao perfil do Thales.
            4. Envie ao grupo o SHA do commit e a URL da execução inicial de CI.
            5. Avise Bruno que a etapa 2 está liberada somente depois dessas conferências.

            Como dono do repositório, configure também:

            - **Settings > Collaborators**: convide `mainardikk`, `Jhonatan-Margraf`,
              `davispecia`, `kaiquegeska` e `VictorOliveiraIbarrola` para colaborar com escrita.
              Cada um precisa aceitar o convite na própria conta antes de publicar.
            - **Settings > Actions > General > Workflow permissions**: Read and write permissions.
              Marque Allow GitHub Actions to create and approve pull requests, se disponível.
            - **Settings > Secrets and variables > Actions > Variables**:
              crie `PROMOCAO_AUTOMATICA` com valor `false` e `PERMITIR_PROMOCAO` com valor `false`.

            Até a etapa 4, não dispare CT manualmente: a versão antiga pode criar um commit de
            campeão. Se a montagem atravessar segunda-feira às 03h de Brasília, desative
            temporariamente apenas o workflow CT e avise Davi para reativá-lo antes do PR 4.

            Não crie outro README no GitHub, não importe o histórico anterior e não faça um
            segundo commit para correções sem combinar com o grupo: o roteiro prevê seis no total.
        """)
    elif number == 2:
        value += apply_patch(payload) + environment()
        value += block("""
            .\.venv\Scripts\python.exe -m mlops_demo.spambase verificar
            if ($LASTEXITCODE -ne 0) { throw "Os dados Spambase nao foram validados." }
        """)
        value += ci() + commit(2)
        value += clean(f"""
            ## 5. Conferir e liberar Jhonatan

            Aguarde os três jobs verdes do CI em [Actions]({REMOTE}/actions).
            Confira que seu commit está associado a `mainardikk` e que há dois commits na main.
            Envie ao grupo o SHA, a URL do CI e a confirmação para Jhonatan iniciar.
            O modelo/API do domínio original ainda permanece ativo nesta etapa; isso é esperado.
        """)
    elif number == 3:
        value += apply_patch(payload) + environment()
        value += block("""
            .\.venv\Scripts\python.exe -m mlops_demo.data validar
            if ($LASTEXITCODE -ne 0) { throw "Os dados ativos nao foram validados." }
        """)
        value += ci()
        value += clean("""
            O patch já traz o campeão e os CSVs da adaptação. Não execute `data base` nem
            `train --campeao` só para copiá-los de novo. O CI treina o código atual para validar
            o contrato; preserve os artefatos fornecidos.
        """)
        value += commit(3)
        value += clean(f"""
            ## 5. Conferir e liberar Davi

            Aguarde CI verde em [Actions]({REMOTE}/actions), confira a autoria no seu perfil
            e envie ao grupo o SHA e a URL desse CI de adaptação. Agora devem existir três
            commits na main. Avise Davi que ele pode iniciar a etapa 4.
        """)
    elif number == 4:
        value += block("""
            git switch -c entrega/04-qualidade-operacao
            if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel criar a branch da entrega 4." }
        """)
        value += apply_patch(payload) + environment(True) + ci()
        value += commit(4, remote_branch="entrega/04-qualidade-operacao")
        value += clean(f"""
            ## 5. Abrir PR, conferir E3 e integrar sem commit extra

            1. Se o CT estiver desativado, reative-o em Actions **antes** de abrir o PR.
            2. Abra um PR de `entrega/04-qualidade-operacao` para `main` no repositório novo.
            3. Aguarde CI verde e CT aprovado. Confira o drift, o portão e a preservação do campeão.
               O cenário previsto tem cinco atributos com drift; confira o resultado do run.
            4. Guarde a URL do PR e a **URL do CT desse PR como E3**.
            5. Depois dos checks, integre pelo terminal abaixo. **Não use o botão de merge,
               squash ou rebase**, pois o roteiro precisa manter apenas o commit desta etapa.
        """)
        value += block("""
            git switch main
            if ($LASTEXITCODE -ne 0) { throw "Falha ao voltar para main." }
            git pull --ff-only origin main
            if ($LASTEXITCODE -ne 0) { throw "A main mudou. Pare e confira com o grupo." }
            git merge --ff-only entrega/04-qualidade-operacao
            if ($LASTEXITCODE -ne 0) { throw "O fast-forward falhou. Nao use outro tipo de merge." }
            git push origin main
            if ($LASTEXITCODE -ne 0) { throw "A integracao nao foi publicada." }
        """)
        value += clean("""
            Confira que o GitHub reconheceu o PR como integrado. Aguarde o CI da main verde
            e salve a **URL desse CI como E1**. A main deve ter quatro commits.
            Mantenha as duas variáveis de promoção em `false`.

            ## 6. Publicar a tag, conferir E5 e o pacote público

            Somente com o CI da main verde, crie a tag na etapa 4:
        """)
        value += block("""
            git tag -a v1.0.0 -m "Primeira publicacao da API de spam"
            if ($LASTEXITCODE -ne 0) { throw "Falha ao criar a tag. Confira se ela ja existe." }
            git push origin v1.0.0
            if ($LASTEXITCODE -ne 0) { throw "A tag nao foi publicada." }
        """)
        value += clean(f"""
            Aguarde CD verde e salve a URL como **E5**. A imagem deste repositório é
            **`ghcr.io/thalescr77/projeto_mlops:1.0.0`**.

            Em Packages, abra o pacote `projeto_mlops` da conta `thalescr77` e confira
            a visibilidade **Public**. Se necessário, peça ao Thales para alterá-la em
            Package settings. Depois, em Actions > CD > Run workflow, selecione a tag
            `v1.0.0` e marque `verificar_publica=true`. Confira que a verificação anônima passou.

            Envie ao grupo: SHA da etapa 4; número/URL do PR; E1; E3; E5; URL da verificação
            pública; URL do pacote; digest da imagem mostrado no Summary do CD.
            Só então libere Kaique. A tag permanece nesta etapa, inclusive depois da documentação.
        """)
    elif number == 5:
        value += block("""
            git switch -c evidencia/05-portao-reprovado
            if ($LASTEXITCODE -ne 0) { throw "Falha ao criar a branch da evidencia." }
            $baseAprovada = git rev-parse origin/main
            Write-Output "Commit aprovado de partida: $baseAprovada"
        """)
        value += apply_patch(payload) + environment(True)
        value += clean("""
            Esta etapa deve reprovar o modelo e o portão. Execute os comandos abaixo e
            confira o motivo de cada falha. Se falhar instalação, importação, dados ou DVC,
            isso não comprova a falha controlada esperada.
        """)
        value += block("""
            .\.venv\Scripts\python.exe demo/local.py ci
            Write-Output "Saida do CI (esperado 1): $LASTEXITCODE"
            .\.venv\Scripts\python.exe demo/local.py ct
            Write-Output "Saida do CT (esperado 1, no portao): $LASTEXITCODE"
            .\.venv\Scripts\python.exe -m mlops_demo.gate --verificar-campeao
            if ($LASTEXITCODE -ne 0) { throw "O campeao nao foi preservado. Pare e revise." }
            Get-FileHash -LiteralPath models/champion/model.joblib -Algorithm SHA256
        """)
        value += clean("""
            **Antes do commit**, abra `docs/FALHA_CONTROLADA.md` no editor:

            - Substitua a referência antiga `704184255579918b50cd0c1b0bb435e3a92676de` pelo
              valor de `$baseAprovada` mostrado acima.
            - Confira métricas, contagens e hashes com seus relatórios em `reports/`.
              Atualize o texto com os resultados efetivamente obtidos.
            - O texto reaproveitado descreve ensaios antigos. Ajuste a descrição do que você
              executou; remova afirmações de comandos que você não rodou, como uma tentativa
              adicional de promoção. Não mantenha resultados antigos como se fossem seus.

            O CT pode alterar `dvc.lock`. Confira o diff e restaure **somente** essa alteração
            gerada pelo ensaio, como abaixo. Não corrija o peso ruim de `params.yaml`, não
            remova testes e não versione candidato/relatórios.
        """)
        value += block("""
            git diff -- dvc.lock
            git restore --worktree -- dvc.lock
            if ($LASTEXITCODE -ne 0) { throw "Revise dvc.lock antes de continuar." }
        """)
        value += commit(5, files="-- params.yaml docs/FALHA_CONTROLADA.md", remote_branch="evidencia/05-portao-reprovado")
        value += clean(f"""
            ## 5. Abrir o PR vermelho e registrar E2/E4

            Abra um PR de `evidencia/05-portao-reprovado` para `main` em [{REMOTE}]({REMOTE}).
            Aguarde as execuções e confirme:

            - **E2 — CI:** vermelho nos testes de modelo; lint, código e dados aprovados.
            - **E4 — CT:** drift detectado, DVC concluído, portão reprovado, confirmação de
              preservação do campeão aprovada. Promoção pulada e artifact
              `candidato-e-relatorios` disponível.

            Salve as duas URLs dos runs e o número/URL do PR. **Feche o PR sem merge**.
            Mantenha a branch remota de evidência, não crie tag e não publique essa branch na main.
            Avise Victor que a main continua na etapa 4 e envie E2/E4 ao grupo.
        """)
    else:
        value += apply_patch(payload) + environment(True)
        value += clean(f"""
            ## 4. Atualizar a documentação com evidências novas

            Aplique esta etapa à main da entrega 4. O PR de Kaique deve estar fechado **sem merge**.
            O patch contém documentação e um PDF antigos como base; eles precisam ser atualizados
            antes do seu commit. Peça ao grupo a ficha `EVIDENCIAS-PARA-O-GRUPO.md` preenchida.

            Revise `README.md`, `ADAPTACAO.md`, `ENTREGA.md`, `docs/OPERACAO.md` e
            as referências em `docs/VALIDACAO.md`:

            1. Use o repositório `{REMOTE}` nos endereços do projeto.
            2. Coloque as cinco URLs reais: E1 CI da main após etapa 4; E2 CI do PR 5;
               E3 CT do PR 4; E4 CT do PR 5; E5 CD da tag `v1.0.0`.
            3. Atualize números/URLs dos PRs, hashes dos commits, pacote público, verificação
               anônima, imagem e digest. A imagem é `ghcr.io/thalescr77/projeto_mlops:1.0.0`.
            4. Atualize também referências ao CI inicial e ao CI da adaptação, se presentes.
               Apenas trocar o dono nos links de Actions deixa IDs antigos: substitua a URL inteira.
            5. Descreva os resultados efetivamente conferidos nos novos runs.
            6. Preserve a fonte/licença UCI, a declaração de IA/reaproveitamento e a divisão do grupo.

            `mainardikk` continua sendo o usuário de Bruno na tabela. Não substitua esse nome
            isoladamente em todos os arquivos. Os hashes dos dados UCI e das bases também
            permanecem iguais; os hashes dos commits são novos.

            Confira o histórico disponível:
        """)
        value += block("""
            git fetch origin
            if ($LASTEXITCODE -ne 0) { throw "Falha ao buscar o historico." }
            git log --all --format="%h | %an | %ae | %s"
            git status --short
        """)
        value += clean("""
            ## 5. Gerar o PDF novo e validar

            O PC precisa ter Chrome ou Edge instalado. Execute a partir da raiz do clone,
            depois de atualizar o Markdown. O script exige duas páginas A4 e links HTTPS.
        """)
        value += block(f"""
            .\\.venv\\Scripts\\python.exe -m pip install markdown-it-py pypdf
            if ($LASTEXITCODE -ne 0) {{ throw "Falha ao instalar as ferramentas do PDF." }}
            .\\.venv\\Scripts\\python.exe (Join-Path $kit "gerar_relatorio.py") --repositorio {REMOTE}
            if ($LASTEXITCODE -ne 0) {{ throw "O PDF nao foi validado. Revise antes de commitar." }}
        """)
        value += "Abra `ADAPTACAO.pdf` e confira visualmente as duas páginas e os links.\n"
        value += ci()
        value += commit(6, files="-- README.md ADAPTACAO.md ADAPTACAO.pdf ENTREGA.md docs/OPERACAO.md docs/VALIDACAO.md", section=6)
        value += clean(f"""
            ## 7. Conferir a entrega completa

            Aguarde CI final verde em [Actions]({REMOTE}/actions). Faça a conferência:
        """)
        value += block("""
            git fetch origin
            git log --all --format="%h | %an | %ae | %s"
            git rev-list --all --count
            git rev-list --count origin/main
            git status --short
            git rev-parse 'v1.0.0^{commit}'
        """)
        value += clean("""
            Espere seis commits distintos no total, cinco na main, um por integrante e pasta limpa.
            Confira que a branch de Kaique permanece no remoto e que o PR foi fechado sem merge.
            A tag `v1.0.0` aponta para o commit de Davi, etapa 4. Não mova a tag nem republique
            a imagem para a mudança documental.

            Para o D2L: URL do repositório público, E1–E5 e URL/print do pacote público.
            O Markdown e o PDF devem apontar para essas mesmas evidências reais.
        """)
    return value


HELP = clean("""
    # Ajuda para esta entrega

    ## Conta, autoria e convite

    Use sua própria conta no seu PC. Aceite o convite do Thales antes de publicar.
    `git config user.name` e `user.email` definem a autoria do commit; não fazem login no GitHub.
    O email precisa estar vinculado/verificado na sua conta para o GitHub associar o perfil.
    No push, faça a autenticação solicitada pelo Git usando sua conta. Não compartilhe senhas ou tokens.
    Se outra conta estiver salva no seu PC, confira a conta selecionada pelo Git Credential Manager.

    ## Um comando falhou

    - Pare e compartilhe com o grupo a mensagem de erro, a etapa e a saída de `git status --short`.
    - Patch falhou: confira se a etapa anterior terminou e se a main foi atualizada.
      Não use `--reject`, não reaplique parcialmente e não apague arquivos para tentar encaixar.
    - Use `--whitespace=nowarn` como no tutorial. `--whitespace=fix` pode alterar dados UCI
      cujos hashes precisam ser preservados.
    - Push rejeitado: confira a conta, o convite e se a main recebeu mudanças de outro colega.
      Não use `--force`. A execução em ordem evita conflitos.
    - Nas etapas 1, 2, 3, 4 e 6, CI local reprovado impede a publicação. Na etapa 5, a reprovação
      de modelo/portão é esperada; falha de instalação/importação/DVC não é a evidência desejada.
    - Se um commit já foi publicado e precisa de correção, pare e combine a solução com o grupo
      para não ultrapassar os seis commits nem reescrever trabalho de outra pessoa.

    ## Arquivos que ficam fora do novo repositório

    Este tutorial, o manifesto e os ZIPs/patches ficam na pasta do pacote, fora do clone.
    O tutorial usa caminhos separados para isso. `git apply --index` prepara as alterações,
    e o `git commit` seguinte será seu. Não use `git am` ou cherry-pick com autoria antiga.
    Ambiente `.venv`, candidato e relatórios gerados ficam ignorados; não force sua inclusão.

    ## Conferência opcional de integridade do pacote

    Na pasta que contém este arquivo, execute:

    ```powershell
    $manifesto = Get-Content -LiteralPath SHA256-ARQUIVOS.json -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($item in $manifesto.PSObject.Properties) {
        $hash = (Get-FileHash -LiteralPath $item.Name -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -ne $item.Value) { throw "Arquivo alterado ou corrompido: $($item.Name)" }
        Write-Output "OK: $($item.Name)"
    }
    ```
""")


COORDINATION = clean(f"""
    # Coordenação da recriação — um pacote por integrante

    Novo repositório público: [{REMOTE}]({REMOTE}). Dono: `thalescr77`.
    Envie a cada integrante somente o ZIP com o nome dele. Cada pessoa extrai o ZIP,
    abre `LEIA-PRIMEIRO.md` e executa sua etapa no próprio PC e na própria conta GitHub.
    Os tutoriais usam Windows/PowerShell, Git e Python 3.11; Docker local é opcional.

    ## Ordem obrigatória

    | Ordem | ZIP | Quem executa | Condição para passar ao próximo |
    |---|---|---|---|
    | 1 | `01-Thales.zip` | Thales (`thalescr77`) | Primeiro commit e CI verde; convites/configurações feitos. |
    | 2 | `02-Bruno.zip` | Bruno (`mainardikk`) | Dados validados, segundo commit e CI verde. |
    | 3 | `03-Jhonatan.zip` | Jhonatan (`Jhonatan-Margraf`) | Adaptação validada, terceiro commit e CI verde. |
    | 4 | `04-Davi.zip` | Davi (`davispecia`) | PR integrado por fast-forward; E1/E3/E5 e pacote público conferidos. |
    | 5 | `05-Kaique.zip` | Kaique (`kaiquegeska`) | E2/E4 conferidos; PR vermelho fechado sem merge. |
    | 6 | `06-Victor.zip` | Victor (`VictorOliveiraIbarrola`) | Documentação/PDF com evidências novas e CI final verde. |

    A divisão de responsabilidades é a mesma do kit original. Confirmem se os usuários estão
    corretos antes de convidar. Cada integrante informa no próprio PC seu email verificado ou
    `noreply`; não precisa enviar senha, token ou conta para o coordenador.

    ## O que Thales configura

    Convide os outros cinco integrantes com acesso de escrita e peça que aceitem o convite.
    Depois do primeiro push, em Settings > Actions > General habilite Read and write permissions
    e, quando disponível, Allow GitHub Actions to create and approve pull requests.
    Em Settings > Secrets and variables > Actions > Variables, defina
    `PROMOCAO_AUTOMATICA=false` e `PERMITIR_PROMOCAO=false`.

    Antes da etapa 4, não execute CT manualmente. Se o processo atravessar segunda-feira às
    03h de Brasília, desative temporariamente só o CT; Davi precisa reativá-lo antes de abrir o PR.
    Se Davi não puder alterar a visibilidade do pacote, Thales deixa o pacote GHCR público.

    ## Histórico e evidências

    ```text
    1 -- 2 -- 3 -- 4 -- 6    main (5 commits)
                   \\
                    5       branch de falha, PR fechado sem merge
    ```

    São seis commits distintos no total. A tag `v1.0.0` aponta para a etapa 4 e não adiciona
    um commit. Não usar squash, rebase de commits publicados, merge com commit adicional,
    importação do histórico antigo ou commits automáticos de promoção.

    | Evidência | Execução nova a guardar | Responsável |
    |---|---|---|
    | E1 | CI verde da main após integrar etapa 4 | Davi |
    | E2 | CI vermelho nos testes de modelo do PR 5 | Kaique |
    | E3 | CT aprovado no PR 4 | Davi |
    | E4 | CT reprovado no portão, campeão preservado, no PR 5 | Kaique |
    | E5 | CD verde da tag `v1.0.0` | Davi |

    Preencham `EVIDENCIAS-PARA-O-GRUPO.md` e enviem os valores a Victor antes do último commit.
    Guardem também o CI inicial e o CI da adaptação. A imagem nova será
    `ghcr.io/thalescr77/projeto_mlops:1.0.0`, com digest e verificação anônima próprios.
    Links de Actions precisam ser copiados das novas execuções; trocar apenas o dono/repo de
    um link antigo não cria evidência.

    ## O que já foi conferido na preparação dos pacotes

    Os arquivos de cada etapa foram conferidos por SHA-256. Os patches foram aplicados em
    repositórios locais de validação, sem criar commits, comparando as seis árvores Git com
    as etapas da base original. Isso verifica a montagem e a preservação dos arquivos.
    Cada integrante ainda executará os testes locais e os novos runs do GitHub Actions.
    O relatório `VALIDACAO-DOS-PACOTES.json` registra a conferência de montagem.
""")


EVIDENCE = clean(f"""
    # Ficha de evidências do novo repositório

    Repositório: {REMOTE}
    Preencher com valores novos reais e enviar a Victor antes da etapa 6.
    Esta ficha é de coordenação: não é necessário adicioná-la como arquivo extra ao repositório.

    | Item | Valor |
    |---|---|
    | SHA etapa 1 / Thales | PREENCHER |
    | URL CI inicial verde | PREENCHER |
    | SHA etapa 2 / Bruno | PREENCHER |
    | URL CI etapa 2 | PREENCHER |
    | SHA etapa 3 / Jhonatan | PREENCHER |
    | URL CI da adaptação | PREENCHER |
    | SHA etapa 4 / Davi (também tag v1.0.0) | PREENCHER |
    | Número e URL PR 4 | PREENCHER |
    | E1 — CI main após etapa 4 | PREENCHER |
    | E3 — CT do PR 4 | PREENCHER |
    | E5 — CD tag v1.0.0 | PREENCHER |
    | URL verificação anônima CD (verificar_publica=true) | PREENCHER |
    | URL pacote público GHCR | PREENCHER |
    | Imagem | ghcr.io/thalescr77/projeto_mlops:1.0.0 |
    | Digest da imagem (sha256:...) | PREENCHER |
    | SHA etapa 5 / Kaique | PREENCHER |
    | Número e URL PR 5 fechado sem merge | PREENCHER |
    | E2 — CI vermelho do PR 5 | PREENCHER |
    | E4 — CT reprovado do PR 5 com campeão preservado | PREENCHER |
    | SHA-256 do campeão preservado | PREENCHER |
    | Métricas e contagens observadas / localização dos relatórios | PREENCHER |
    | SHA etapa 6 / Victor (depois do último commit) | PREENCHER |
    | URL CI final verde (depois do último commit) | PREENCHER |

    O sexto commit não pode conter a própria URL de um CI que ainda não ocorreu; os valores
    finais podem ser enviados ao grupo/D2L após o push, sem criar um sétimo commit.
""")


def validate_payloads() -> dict:
    """Aplica os patches e compara árvores sem importar commits para a nova entrega."""
    base = Path(tempfile.mkdtemp(prefix="validacao-pacotes-", dir=ROOT / "execucao"))
    expected = json.loads((SOURCE_KIT / "VERIFICACAO.json").read_text(encoding="utf-8"))
    results = []

    def new_repo(label: str, archive: Path) -> Path:
        target = base / label
        target.mkdir()
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.namelist():
                if not (target / member).resolve().is_relative_to(target.resolve()):
                    raise ValueError(f"Caminho fora da pasta de validacao: {member}")
            bundle.extractall(target)
        git(target, "init", "-b", "main")
        git(target, "config", "--local", "core.autocrlf", "false")
        git(target, "add", "--all")
        return target

    def compare(number: int, target: Path) -> None:
        reference = expected["etapas"][number - 1]["commit_fonte"]
        wanted = git(SOURCE_REPO, "rev-parse", f"{reference}^{{tree}}")
        actual = git(target, "write-tree")
        if actual != wanted:
            raise ValueError(f"Arvore diferente na etapa {number}: {actual} != {wanted}")
        results.append({"etapa": number, "arvore": actual, "igual_a_base": True})

    linear = new_repo("etapas-1-a-4", SOURCE_KIT / "01-base-original.zip")
    compare(1, linear)
    for number in (2, 3, 4):
        payload = SOURCE_KIT / PEOPLE[number - 1][4]
        git(linear, "apply", "--index", "--whitespace=nowarn", str(payload))
        compare(number, linear)
    approved = base / "etapa-4.zip"
    reference4 = expected["etapas"][3]["commit_fonte"]
    git(SOURCE_REPO, "archive", "--format=zip", f"--output={approved}", reference4)
    for number in (5, 6):
        target = new_repo(f"etapa-{number}", approved)
        git(target, "apply", "--index", "--whitespace=nowarn", str(SOURCE_KIT / PEOPLE[number - 1][4]))
        compare(number, target)
    return {
        "repositorio_destino": REMOTE,
        "metodo": "Aplicacao com git apply --index e comparacao das seis arvores; sem commits ou push.",
        "validacao_de_execucoes_ci_ct": "A realizar por cada integrante e no novo GitHub Actions.",
        "etapas": results,
    }


def main() -> None:
    manifest = json.loads((SOURCE_KIT / "SHA256.json").read_text(encoding="utf-8"))
    for filename, wanted in manifest.items():
        if sha(SOURCE_KIT / filename) != wanted:
            raise ValueError(f"Hash divergente na fonte do kit: {filename}")
    validation = validate_payloads()
    OUT.mkdir(exist_ok=True)
    write(OUT / "00-COORDENACAO.md", COORDINATION)
    write(OUT / "EVIDENCIAS-PARA-O-GRUPO.md", EVIDENCE)
    for person in PEOPLE:
        number, short, _, _, payload = person
        slug = f"{number:02}-{short}"
        folder = OUT / slug
        folder.mkdir(exist_ok=True)
        shutil.copyfile(SOURCE_KIT / payload, folder / payload)
        if number == 6:
            shutil.copyfile(SOURCE_KIT / "gerar_relatorio.py", folder / "gerar_relatorio.py")
            write(folder / "EVIDENCIAS-PARA-O-GRUPO.md", EVIDENCE)
        write(folder / "LEIA-PRIMEIRO.md", tutorial(person))
        write(folder / "AJUDA.md", HELP)
        file_manifest = {
            path.name: sha(path)
            for path in sorted(folder.iterdir())
            if path.name != "SHA256-ARQUIVOS.json"
        }
        write(folder / "SHA256-ARQUIVOS.json", json.dumps(file_manifest, indent=2, ensure_ascii=False) + "\n")
        zip_path = OUT / f"{slug}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(folder.iterdir()):
                bundle.write(path, f"{slug}/{path.name}")
        with zipfile.ZipFile(zip_path) as bundle:
            if bundle.testzip() is not None:
                raise ValueError(f"ZIP corrompido: {zip_path}")
            for filename, wanted in file_manifest.items():
                actual = hashlib.sha256(bundle.read(f"{slug}/{filename}")).hexdigest()
                if actual != wanted:
                    raise ValueError(f"Hash divergente dentro de {zip_path.name}: {filename}")
        print(f"OK {zip_path.name}: {zip_path.stat().st_size} bytes")
    write(OUT / "VALIDACAO-DOS-PACOTES.json", json.dumps(validation, indent=2, ensure_ascii=False) + "\n")
    zip_manifest = {path.name: sha(path) for path in sorted(OUT.glob("*.zip"))}
    write(OUT / "SHA256-ZIPS.json", json.dumps(zip_manifest, indent=2) + "\n")
    print("Seis etapas: arvores identicas a base. Seis ZIPs: integridade conferida.")


if __name__ == "__main__":
    main()
