# Etapa 2 — Bruno Mainardi

Repositório de entrega: [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS).
Sua conta: **`mainardikk`**. Execute esta etapa no seu PC, autenticado nessa conta.

Comece depois que Thales publicar a etapa 1 e o CI ficar verde.

Este pacote contém `02-dados.patch`, este tutorial, ajuda e um manifesto de integridade.
Os arquivos foram reaproveitados da base do grupo. Sua parte é revisar, executar,
validar e criar seu próprio commit. Mantenham a declaração de reaproveitamento e IA.

## 1. Abrir o pacote e conferir os programas

Extraia o ZIP recebido. No Explorador do Windows, abra a pasta que contém este
`LEIA-PRIMEIRO.md` e `02-dados.patch` e escolha **Abrir no Terminal**, usando PowerShell.
Os comandos abaixo usam Windows, Git e Python 3.11. Docker local é opcional.

Execute um bloco por vez, na mesma janela do PowerShell. Se um comando falhar,
pare e leia `AJUDA.md`. Na etapa 5, as falhas esperadas de CI/CT estão indicadas.
Não avance para o próximo integrante antes das conferências finais desta etapa.

```powershell
$ErrorActionPreference = "Stop"
$kit = (Get-Location).Path
if (-not (Test-Path -LiteralPath (Join-Path $kit "02-dados.patch"))) {
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
$repo = Join-Path $trabalho "MLOPS_BRUNO"
if (Test-Path -LiteralPath $repo) {
    throw "A pasta do clone ja existe. Escolha outra pasta antes de continuar."
}
```


```powershell
git clone https://github.com/thalescr77/Projeto_MLOPS.git "$repo"
if ($LASTEXITCODE -ne 0) { throw "O clone falhou; confira o acesso ao repositorio." }
Set-Location -LiteralPath $repo
```

Informe um email **verificado na sua conta `mainardikk`**, ou o endereço `noreply`
mostrado no GitHub em **Settings > Emails**. O nome/email abaixo definem a autoria;
a autenticação para publicar será feita separadamente pelo Git.

```powershell
$emailGit = Read-Host "Seu email verificado no GitHub (ou noreply)"
if ($emailGit -notmatch '^[^@\s]+@[^@\s]+\.[^@\s]+$') {
    throw "Email invalido. Confira em GitHub > Settings > Emails."
}
git config --local user.name "Bruno Mainardi"
git config --local user.email "$emailGit"
git config --local user.useConfigOnly true
git config --local core.autocrlf false
git config --local credential.https://github.com.username mainardikk
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
git apply --index --whitespace=nowarn (Join-Path $kit "02-dados.patch")
if ($LASTEXITCODE -ne 0) { throw "O patch falhou. Pare; nao reaplique parcialmente." }
```


```powershell
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente Python 3.11." }
.\.venv\Scripts\python.exe -m pip install -e ".[dev,ct]"
if ($LASTEXITCODE -ne 0) { throw "A instalacao falhou; nao continue." }
```


```powershell
.\.venv\Scripts\python.exe -m mlops_demo.spambase verificar
if ($LASTEXITCODE -ne 0) { throw "Os dados Spambase nao foram validados." }
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
git commit -m "feat: prepara Spambase reproduzivel sem vazamento de dados"
if ($LASTEXITCODE -ne 0) { throw "O commit falhou; nao execute o push." }
git log -1 --format="%h | %an | %ae | %s"
git push origin main
if ($LASTEXITCODE -ne 0) { throw "O push falhou. Confira a conta e o convite; nao use force." }
```

## 5. Conferir e liberar Jhonatan

Aguarde os três jobs verdes do CI em [Actions](https://github.com/thalescr77/Projeto_MLOPS/actions).
Confira que seu commit está associado a `mainardikk` e que há dois commits na main.
Envie ao grupo o SHA, a URL do CI e a confirmação para Jhonatan iniciar.
O modelo/API do domínio original ainda permanece ativo nesta etapa; isso é esperado.
