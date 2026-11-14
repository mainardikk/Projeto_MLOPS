# Etapa 4 — Davi Specia

Repositório de entrega: [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS).
Sua conta: **`davispecia`**. Execute esta etapa no seu PC, autenticado nessa conta.

Comece depois que Jhonatan publicar a etapa 3 e o CI ficar verde.

Este pacote contém `04-pipelines-drift.patch`, este tutorial, ajuda e um manifesto de integridade.
Os arquivos foram reaproveitados da base do grupo. Sua parte é revisar, executar,
validar e criar seu próprio commit. Mantenham a declaração de reaproveitamento e IA.

## 1. Abrir o pacote e conferir os programas

Extraia o ZIP recebido. No Explorador do Windows, abra a pasta que contém este
`LEIA-PRIMEIRO.md` e `04-pipelines-drift.patch` e escolha **Abrir no Terminal**, usando PowerShell.
Os comandos abaixo usam Windows, Git e Python 3.11. Docker local é opcional.

Execute um bloco por vez, na mesma janela do PowerShell. Se um comando falhar,
pare e leia `AJUDA.md`. Na etapa 5, as falhas esperadas de CI/CT estão indicadas.
Não avance para o próximo integrante antes das conferências finais desta etapa.

```powershell
$ErrorActionPreference = "Stop"
$kit = (Get-Location).Path
if (-not (Test-Path -LiteralPath (Join-Path $kit "04-pipelines-drift.patch"))) {
    throw "Abra o PowerShell na pasta extraida que contem o arquivo da sua etapa."
}
git --version
if ($LASTEXITCODE -ne 0) { throw "Instale o Git e reabra o terminal." }
py -3.11 --version
if ($LASTEXITCODE -ne 0) { throw "Instale o Python 3.11 e reabra o terminal." }
```

## 2. Preparar uma pasta nova e sua identidade

O clone ficará em `Documentos/MLOPS-ENTREGA`, separado dos arquivos deste pacote.
Se a pasta do clone já existir, pare e escolha outro nome: não apague trabalho anterior.

```powershell
$trabalho = Join-Path $env:USERPROFILE "Documents\MLOPS-ENTREGA"
New-Item -ItemType Directory -Path $trabalho -Force | Out-Null
$repo = Join-Path $trabalho "MLOPS_DAVI"
if (Test-Path -LiteralPath $repo) {
    throw "A pasta do clone ja existe. Escolha outra pasta antes de continuar."
}
```


```powershell
git clone https://github.com/thalescr77/Projeto_MLOPS.git "$repo"
if ($LASTEXITCODE -ne 0) { throw "O clone falhou; confira o acesso ao repositorio." }
Set-Location -LiteralPath $repo
```

Informe um email **verificado na sua conta `davispecia`**, ou o endereço `noreply`
mostrado no GitHub em **Settings > Emails**. O nome/email abaixo definem a autoria;
a autenticação para publicar será feita separadamente pelo Git.

```powershell
$emailGit = Read-Host "Seu email verificado no GitHub (ou noreply)"
if ($emailGit -notmatch '^[^@\s]+@[^@\s]+\.[^@\s]+$') {
    throw "Email invalido. Confira em GitHub > Settings > Emails."
}
git config --local user.name "Davi Specia"
git config --local user.email "$emailGit"
git config --local user.useConfigOnly true
git config --local core.autocrlf false
git config --local credential.https://github.com.username davispecia
git config --local --get user.name
git config --local --get user.email
git remote -v
```


```powershell
git switch main
if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel entrar na main." }
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw "Pare e revise a base antes de aplicar o patch." }
git status --short
```

A saída de `git status --short` deve estar vazia antes de aplicar o patch.

## 3. Aplicar e validar sua etapa


```powershell
git switch -c entrega/04-qualidade-operacao
if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel criar a branch da entrega 4." }
```


```powershell
git apply --index --whitespace=nowarn (Join-Path $kit "04-pipelines-drift.patch")
if ($LASTEXITCODE -ne 0) { throw "O patch falhou. Pare; nao reaplique parcialmente." }
```


```powershell
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente Python 3.11." }
.\.venv\Scripts\python.exe -m pip install -c constraints.txt -e ".[dev,ct]"
if ($LASTEXITCODE -ne 0) { throw "A instalacao falhou; nao continue." }
```


```powershell
.\.venv\Scripts\python.exe demo/local.py ci
if ($LASTEXITCODE -ne 0) { throw "CI local reprovado. Resolva antes de commitar." }
```


## 4. Revisar, criar seu commit e publicar

Confira os arquivos e a identidade antes de publicar. O nome/email devem ser os seus.

```powershell
git add --all
if ($LASTEXITCODE -ne 0) { throw "Falha ao preparar os arquivos." }
git diff --cached --stat
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "Revise os problemas indicados no diff." }
git config --local --get user.name
git config --local --get user.email
```

Depois de revisar a saída, execute:

```powershell
git commit -m "feat: reforca pipelines e demonstra CT com drift por PR"
if ($LASTEXITCODE -ne 0) { throw "O commit falhou; nao execute o push." }
git log -1 --format="%h | %an | %ae | %s"
git push -u origin entrega/04-qualidade-operacao
if ($LASTEXITCODE -ne 0) { throw "O push falhou. Confira a conta e o convite; nao use force." }
```

## 5. Abrir PR, conferir E3 e integrar sem commit extra

1. Se o CT estiver desativado, reative-o em Actions **antes** de abrir o PR.
2. Abra um PR de `entrega/04-qualidade-operacao` para `main` no repositório novo.
3. Aguarde CI verde e CT aprovado. Confira o drift, o portão e a preservação do campeão.
   O cenário previsto tem cinco atributos com drift; confira o resultado do run.
4. Guarde a URL do PR e a **URL do CT desse PR como E3**.
5. Depois dos checks, integre pelo terminal abaixo. **Não use o botão de merge,
   squash ou rebase**, pois o roteiro precisa manter apenas o commit desta etapa.

```powershell
git switch main
if ($LASTEXITCODE -ne 0) { throw "Falha ao voltar para main." }
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw "A main mudou. Pare e confira com o grupo." }
git merge --ff-only entrega/04-qualidade-operacao
if ($LASTEXITCODE -ne 0) { throw "O fast-forward falhou. Nao use outro tipo de merge." }
git push origin main
if ($LASTEXITCODE -ne 0) { throw "A integracao nao foi publicada." }
```

Confira que o GitHub reconheceu o PR como integrado. Aguarde o CI da main verde
e salve a **URL desse CI como E1**. A main deve ter quatro commits.
Mantenha as duas variáveis de promoção em `false`.

## 6. Publicar a tag, conferir E5 e o pacote público

Somente com o CI da main verde, crie a tag na etapa 4:

```powershell
git tag -a v1.0.0 -m "Primeira publicacao da API de spam"
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar a tag. Confira se ela ja existe." }
git push origin v1.0.0
if ($LASTEXITCODE -ne 0) { throw "A tag nao foi publicada." }
```

Aguarde CD verde e salve a URL como **E5**. A imagem deste repositório é
**`ghcr.io/thalescr77/projeto_mlops:1.0.0`**.

Em Packages, abra o pacote `projeto_mlops` da conta `thalescr77` e confira
a visibilidade **Public**. Se necessário, peça ao Thales para alterá-la em
Package settings. Depois, em Actions > CD > Run workflow, selecione a tag
`v1.0.0` e marque `verificar_publica=true`. Confira que a verificação anônima passou.

Envie ao grupo: SHA da etapa 4; número/URL do PR; E1; E3; E5; URL da verificação
pública; URL do pacote; digest da imagem mostrado no Summary do CD.
Só então libere Kaique. A tag permanece nesta etapa, inclusive depois da documentação.
