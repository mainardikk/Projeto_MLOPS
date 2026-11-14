# Etapa 3 — Jhonatan Margraf

Repositório de entrega: [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS).
Sua conta: **`Jhonatan-Margraf`**. Execute esta etapa no seu PC, autenticado nessa conta.

Comece depois que Bruno publicar a etapa 2 e o CI ficar verde.

Este pacote contém `03-adaptacao-spam.patch`, este tutorial, ajuda e um manifesto de integridade.
Os arquivos foram reaproveitados da base do grupo. Sua parte é revisar, executar,
validar e criar seu próprio commit. Mantenham a declaração de reaproveitamento e IA.

## 1. Abrir o pacote e conferir os programas

Extraia o ZIP recebido. No Explorador do Windows, abra a pasta que contém este
`LEIA-PRIMEIRO.md` e `03-adaptacao-spam.patch` e escolha **Abrir no Terminal**, usando PowerShell.
Os comandos abaixo usam Windows, Git e Python 3.11. Docker local é opcional.

Execute um bloco por vez, na mesma janela do PowerShell. Se um comando falhar,
pare e leia `AJUDA.md`. Na etapa 5, as falhas esperadas de CI/CT estão indicadas.
Não avance para o próximo integrante antes das conferências finais desta etapa.

```powershell
$ErrorActionPreference = "Stop"
$kit = (Get-Location).Path
if (-not (Test-Path -LiteralPath (Join-Path $kit "03-adaptacao-spam.patch"))) {
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
$repo = Join-Path $trabalho "MLOPS_JHONATAN"
if (Test-Path -LiteralPath $repo) {
    throw "A pasta do clone ja existe. Escolha outra pasta antes de continuar."
}
```


```powershell
git clone https://github.com/thalescr77/Projeto_MLOPS.git "$repo"
if ($LASTEXITCODE -ne 0) { throw "O clone falhou; confira o acesso ao repositorio." }
Set-Location -LiteralPath $repo
```

Informe um email **verificado na sua conta `Jhonatan-Margraf`**, ou o endereço `noreply`
mostrado no GitHub em **Settings > Emails**. O nome/email abaixo definem a autoria;
a autenticação para publicar será feita separadamente pelo Git.

```powershell
$emailGit = Read-Host "Seu email verificado no GitHub (ou noreply)"
if ($emailGit -notmatch '^[^@\s]+@[^@\s]+\.[^@\s]+$') {
    throw "Email invalido. Confira em GitHub > Settings > Emails."
}
git config --local user.name "Jhonatan Margraf"
git config --local user.email "$emailGit"
git config --local user.useConfigOnly true
git config --local core.autocrlf false
git config --local credential.https://github.com.username Jhonatan-Margraf
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
git apply --index --whitespace=nowarn (Join-Path $kit "03-adaptacao-spam.patch")
if ($LASTEXITCODE -ne 0) { throw "O patch falhou. Pare; nao reaplique parcialmente." }
```


```powershell
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente Python 3.11." }
.\.venv\Scripts\python.exe -m pip install -e ".[dev,ct]"
if ($LASTEXITCODE -ne 0) { throw "A instalacao falhou; nao continue." }
```


```powershell
.\.venv\Scripts\python.exe -m mlops_demo.data validar
if ($LASTEXITCODE -ne 0) { throw "Os dados ativos nao foram validados." }
```


```powershell
.\.venv\Scripts\python.exe demo/local.py ci
if ($LASTEXITCODE -ne 0) { throw "CI local reprovado. Resolva antes de commitar." }
```

O patch já traz o campeão e os CSVs da adaptação. Não execute `data base` nem
`train --campeao` só para copiá-los de novo. O CI treina o código atual para validar
o contrato; preserve os artefatos fornecidos.

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
git commit -m "feat: adapta modelo API e contrato para classificacao de spam"
if ($LASTEXITCODE -ne 0) { throw "O commit falhou; nao execute o push." }
git log -1 --format="%h | %an | %ae | %s"
git push origin main
if ($LASTEXITCODE -ne 0) { throw "O push falhou. Confira a conta e o convite; nao use force." }
```

## 5. Conferir e liberar Davi

Aguarde CI verde em [Actions](https://github.com/thalescr77/Projeto_MLOPS/actions), confira a autoria no seu perfil
e envie ao grupo o SHA e a URL desse CI de adaptação. Agora devem existir três
commits na main. Avise Davi que ele pode iniciar a etapa 4.
