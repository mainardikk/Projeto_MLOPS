# Etapa 5 — Kaique Geska

Repositório de entrega: [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS).
Sua conta: **`kaiquegeska`**. Execute esta etapa no seu PC, autenticado nessa conta.

Comece depois que Davi concluir a etapa 4, incluindo CI, CT, tag e publicação pública.

Este pacote contém `05-falha-controlada.patch`, este tutorial, ajuda e um manifesto de integridade.
Os arquivos foram reaproveitados da base do grupo. Sua parte é revisar, executar,
validar e criar seu próprio commit. Mantenham a declaração de reaproveitamento e IA.

## 1. Abrir o pacote e conferir os programas

Extraia o ZIP recebido. No Explorador do Windows, abra a pasta que contém este
`LEIA-PRIMEIRO.md` e `05-falha-controlada.patch` e escolha **Abrir no Terminal**, usando PowerShell.
Os comandos abaixo usam Windows, Git e Python 3.11. Docker local é opcional.

Execute um bloco por vez, na mesma janela do PowerShell. Se um comando falhar,
pare e leia `AJUDA.md`. Na etapa 5, as falhas esperadas de CI/CT estão indicadas.
Não avance para o próximo integrante antes das conferências finais desta etapa.

```powershell
$ErrorActionPreference = "Stop"
$kit = (Get-Location).Path
if (-not (Test-Path -LiteralPath (Join-Path $kit "05-falha-controlada.patch"))) {
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
$repo = Join-Path $trabalho "MLOPS_KAIQUE"
if (Test-Path -LiteralPath $repo) {
    throw "A pasta do clone ja existe. Escolha outra pasta antes de continuar."
}
```


```powershell
git clone https://github.com/thalescr77/Projeto_MLOPS.git "$repo"
if ($LASTEXITCODE -ne 0) { throw "O clone falhou; confira o acesso ao repositorio." }
Set-Location -LiteralPath $repo
```

Informe um email **verificado na sua conta `kaiquegeska`**, ou o endereço `noreply`
mostrado no GitHub em **Settings > Emails**. O nome/email abaixo definem a autoria;
a autenticação para publicar será feita separadamente pelo Git.

```powershell
$emailGit = Read-Host "Seu email verificado no GitHub (ou noreply)"
if ($emailGit -notmatch '^[^@\s]+@[^@\s]+\.[^@\s]+$') {
    throw "Email invalido. Confira em GitHub > Settings > Emails."
}
git config --local user.name "Kaique Geska"
git config --local user.email "$emailGit"
git config --local user.useConfigOnly true
git config --local core.autocrlf false
git config --local credential.https://github.com.username kaiquegeska
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
git switch -c evidencia/05-portao-reprovado
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar a branch da evidencia." }
$baseAprovada = git rev-parse origin/main
Write-Output "Commit aprovado de partida: $baseAprovada"
```


```powershell
git apply --index --whitespace=nowarn (Join-Path $kit "05-falha-controlada.patch")
if ($LASTEXITCODE -ne 0) { throw "O patch falhou. Pare; nao reaplique parcialmente." }
```


```powershell
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente Python 3.11." }
.\.venv\Scripts\python.exe -m pip install -c constraints.txt -e ".[dev,ct]"
if ($LASTEXITCODE -ne 0) { throw "A instalacao falhou; nao continue." }
```

Esta etapa deve reprovar o modelo e o portão. Execute os comandos abaixo e
confira o motivo de cada falha. Se falhar instalação, importação, dados ou DVC,
isso não comprova a falha controlada esperada.

```powershell
.\.venv\Scripts\python.exe demo/local.py ci
Write-Output "Saida do CI (esperado 1): $LASTEXITCODE"
.\.venv\Scripts\python.exe demo/local.py ct
Write-Output "Saida do CT (esperado 1, no portao): $LASTEXITCODE"
.\.venv\Scripts\python.exe -m mlops_demo.gate --verificar-campeao
if ($LASTEXITCODE -ne 0) { throw "O campeao nao foi preservado. Pare e revise." }
Get-FileHash -LiteralPath models/champion/model.joblib -Algorithm SHA256
```

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

```powershell
git diff -- dvc.lock
git restore --worktree -- dvc.lock
if ($LASTEXITCODE -ne 0) { throw "Revise dvc.lock antes de continuar." }
```


## 4. Revisar, criar seu commit e publicar

Confira os arquivos e a identidade antes de publicar. O nome/email devem ser os seus.

```powershell
git add -- params.yaml docs/FALHA_CONTROLADA.md
if ($LASTEXITCODE -ne 0) { throw "Falha ao preparar os arquivos." }
git diff --cached --stat
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "Revise os problemas indicados no diff." }
git config --local --get user.name
git config --local --get user.email
```

Depois de revisar a saída, execute:

```powershell
git commit -m "test: registra falha controlada e protecao do campeao"
if ($LASTEXITCODE -ne 0) { throw "O commit falhou; nao execute o push." }
git log -1 --format="%h | %an | %ae | %s"
git push -u origin evidencia/05-portao-reprovado
if ($LASTEXITCODE -ne 0) { throw "O push falhou. Confira a conta e o convite; nao use force." }
```

## 5. Abrir o PR vermelho e registrar E2/E4

Abra um PR de `evidencia/05-portao-reprovado` para `main` em [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS).
Aguarde as execuções e confirme:

- **E2 — CI:** vermelho nos testes de modelo; lint, código e dados aprovados.
- **E4 — CT:** drift detectado, DVC concluído, portão reprovado, confirmação de
  preservação do campeão aprovada. Promoção pulada e artifact
  `candidato-e-relatorios` disponível.

Salve as duas URLs dos runs e o número/URL do PR. **Feche o PR sem merge**.
Mantenha a branch remota de evidência, não crie tag e não publique essa branch na main.
Avise Victor que a main continua na etapa 4 e envie E2/E4 ao grupo.
