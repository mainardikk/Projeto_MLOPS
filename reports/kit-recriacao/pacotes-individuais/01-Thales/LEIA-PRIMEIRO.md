# Etapa 1 — Thales Serschon

Repositório de entrega: [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS).
Sua conta: **`thalescr77`**. Execute esta etapa no seu PC, autenticado nessa conta.

Comece com o repositório público e vazio, criado pelo Thales.

Este pacote contém `01-base-original.zip`, este tutorial, ajuda e um manifesto de integridade.
Os arquivos foram reaproveitados da base do grupo. Sua parte é revisar, executar,
validar e criar seu próprio commit. Mantenham a declaração de reaproveitamento e IA.

## 1. Abrir o pacote e conferir os programas

Extraia o ZIP recebido. No Explorador do Windows, abra a pasta que contém este
`LEIA-PRIMEIRO.md` e `01-base-original.zip` e escolha **Abrir no Terminal**, usando PowerShell.
Os comandos abaixo usam Windows, Git e Python 3.11. Docker local é opcional.

Execute um bloco por vez, na mesma janela do PowerShell. Se um comando falhar,
pare e leia `AJUDA.md`. Na etapa 5, as falhas esperadas de CI/CT estão indicadas.
Não avance para o próximo integrante antes das conferências finais desta etapa.

```powershell
$ErrorActionPreference = "Stop"
$kit = (Get-Location).Path
if (-not (Test-Path -LiteralPath (Join-Path $kit "01-base-original.zip"))) {
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
$repo = Join-Path $trabalho "MLOPS_THALES"
if (Test-Path -LiteralPath $repo) {
    throw "A pasta do clone ja existe. Escolha outra pasta antes de continuar."
}
```


```powershell
New-Item -ItemType Directory -Path $repo | Out-Null
Set-Location -LiteralPath $repo
git init -b main
if ($LASTEXITCODE -ne 0) { throw "Falha ao inicializar o repositorio." }
git remote add origin https://github.com/thalescr77/Projeto_MLOPS.git
if ($LASTEXITCODE -ne 0) { throw "Falha ao configurar origin." }
Expand-Archive -LiteralPath (Join-Path $kit "01-base-original.zip") -DestinationPath .
```

Informe um email **verificado na sua conta `thalescr77`**, ou o endereço `noreply`
mostrado no GitHub em **Settings > Emails**. O nome/email abaixo definem a autoria;
a autenticação para publicar será feita separadamente pelo Git.

O email informado pelo grupo para Thales é `thales.serschon17.10@gmail.com`; confirme que está vinculado à sua conta.

```powershell
$emailGit = Read-Host "Seu email verificado no GitHub (ou noreply)"
if ($emailGit -notmatch '^[^@\s]+@[^@\s]+\.[^@\s]+$') {
    throw "Email invalido. Confira em GitHub > Settings > Emails."
}
git config --local user.name "Thales Serschon"
git config --local user.email "$emailGit"
git config --local user.useConfigOnly true
git config --local core.autocrlf false
git config --local credential.https://github.com.username thalescr77
git config --local --get user.name
git config --local --get user.email
git remote -v
```


## 3. Aplicar e validar sua etapa


```powershell
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente Python 3.11." }
.\.venv\Scripts\python.exe -m pip install -e ".[dev,ct]"
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
git commit -m "chore: adiciona base original de CI/CD/CT para ML"
if ($LASTEXITCODE -ne 0) { throw "O commit falhou; nao execute o push." }
git log -1 --format="%h | %an | %ae | %s"
git push -u origin main
if ($LASTEXITCODE -ne 0) { throw "O push falhou. Confira a conta e o convite; nao use force." }
```

## 5. Conferir no GitHub e liberar Bruno

1. Se o Git pedir autenticação, entre na conta **`thalescr77`** no seu PC.
2. Abra [Actions](https://github.com/thalescr77/Projeto_MLOPS/actions) e aguarde o CI deste commit. Os três jobs
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
