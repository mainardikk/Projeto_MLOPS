# Etapa 6 — Victor Ibarrola

Repositório de entrega: [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS).
Sua conta: **`VictorOliveiraIbarrola`**. Execute esta etapa no seu PC, autenticado nessa conta.

Comece depois que Kaique conferir E2/E4 e fechar o PR de falha sem merge.

Este pacote contém `06-documentacao.patch`, este tutorial, ajuda e um manifesto de integridade.
Os arquivos foram reaproveitados da base do grupo. Sua parte é revisar, executar,
validar e criar seu próprio commit. Mantenham a declaração de reaproveitamento e IA.

## 1. Abrir o pacote e conferir os programas

Extraia o ZIP recebido. No Explorador do Windows, abra a pasta que contém este
`LEIA-PRIMEIRO.md` e `06-documentacao.patch` e escolha **Abrir no Terminal**, usando PowerShell.
Os comandos abaixo usam Windows, Git e Python 3.11. Docker local é opcional.

Execute um bloco por vez, na mesma janela do PowerShell. Se um comando falhar,
pare e leia `AJUDA.md`. Na etapa 5, as falhas esperadas de CI/CT estão indicadas.
Não avance para o próximo integrante antes das conferências finais desta etapa.

```powershell
$ErrorActionPreference = "Stop"
$kit = (Get-Location).Path
if (-not (Test-Path -LiteralPath (Join-Path $kit "06-documentacao.patch"))) {
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
$repo = Join-Path $trabalho "MLOPS_VICTOR"
if (Test-Path -LiteralPath $repo) {
    throw "A pasta do clone ja existe. Escolha outra pasta antes de continuar."
}
```


```powershell
git clone https://github.com/thalescr77/Projeto_MLOPS.git "$repo"
if ($LASTEXITCODE -ne 0) { throw "O clone falhou; confira o acesso ao repositorio." }
Set-Location -LiteralPath $repo
```

Informe um email **verificado na sua conta `VictorOliveiraIbarrola`**, ou o endereço `noreply`
mostrado no GitHub em **Settings > Emails**. O nome/email abaixo definem a autoria;
a autenticação para publicar será feita separadamente pelo Git.

```powershell
$emailGit = Read-Host "Seu email verificado no GitHub (ou noreply)"
if ($emailGit -notmatch '^[^@\s]+@[^@\s]+\.[^@\s]+$') {
    throw "Email invalido. Confira em GitHub > Settings > Emails."
}
git config --local user.name "Victor Ibarrola"
git config --local user.email "$emailGit"
git config --local user.useConfigOnly true
git config --local core.autocrlf false
git config --local credential.https://github.com.username VictorOliveiraIbarrola
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
git apply --index --whitespace=nowarn (Join-Path $kit "06-documentacao.patch")
if ($LASTEXITCODE -ne 0) { throw "O patch falhou. Pare; nao reaplique parcialmente." }
```


```powershell
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente Python 3.11." }
.\.venv\Scripts\python.exe -m pip install -c constraints.txt -e ".[dev,ct]"
if ($LASTEXITCODE -ne 0) { throw "A instalacao falhou; nao continue." }
```

## 4. Atualizar a documentação com evidências novas

Aplique esta etapa à main da entrega 4. O PR de Kaique deve estar fechado **sem merge**.
O patch contém documentação e um PDF antigos como base; eles precisam ser atualizados
antes do seu commit. Peça ao grupo a ficha `EVIDENCIAS-PARA-O-GRUPO.md` preenchida.

Revise `README.md`, `ADAPTACAO.md`, `ENTREGA.md`, `docs/OPERACAO.md` e
as referências em `docs/VALIDACAO.md`:

1. Use o repositório `https://github.com/thalescr77/Projeto_MLOPS` nos endereços do projeto.
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

```powershell
git fetch origin
if ($LASTEXITCODE -ne 0) { throw "Falha ao buscar o historico." }
git log --all --format="%h | %an | %ae | %s"
git status --short
```

## 5. Gerar o PDF novo e validar

O PC precisa ter Chrome ou Edge instalado. Execute a partir da raiz do clone,
depois de atualizar o Markdown. O script exige duas páginas A4 e links HTTPS.

```powershell
.\.venv\Scripts\python.exe -m pip install markdown-it-py pypdf
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as ferramentas do PDF." }
.\.venv\Scripts\python.exe (Join-Path $kit "gerar_relatorio.py") --repositorio https://github.com/thalescr77/Projeto_MLOPS
if ($LASTEXITCODE -ne 0) { throw "O PDF nao foi validado. Revise antes de commitar." }
```

Abra `ADAPTACAO.pdf` e confira visualmente as duas páginas e os links.

```powershell
.\.venv\Scripts\python.exe demo/local.py ci
if ($LASTEXITCODE -ne 0) { throw "CI local reprovado. Resolva antes de commitar." }
```


## 6. Revisar, criar seu commit e publicar

Confira os arquivos e a identidade antes de publicar. O nome/email devem ser os seus.

```powershell
git add -- README.md ADAPTACAO.md ADAPTACAO.pdf ENTREGA.md docs/OPERACAO.md docs/VALIDACAO.md
if ($LASTEXITCODE -ne 0) { throw "Falha ao preparar os arquivos." }
git diff --cached --stat
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "Revise os problemas indicados no diff." }
git config --local --get user.name
git config --local --get user.email
```

Depois de revisar a saída, execute:

```powershell
git commit -m "docs: finaliza relatorio evidencias e instrucoes de entrega"
if ($LASTEXITCODE -ne 0) { throw "O commit falhou; nao execute o push." }
git log -1 --format="%h | %an | %ae | %s"
git push origin main
if ($LASTEXITCODE -ne 0) { throw "O push falhou. Confira a conta e o convite; nao use force." }
```

## 7. Conferir a entrega completa

Aguarde CI final verde em [Actions](https://github.com/thalescr77/Projeto_MLOPS/actions). Faça a conferência:

```powershell
git fetch origin
git log --all --format="%h | %an | %ae | %s"
git rev-list --all --count
git rev-list --count origin/main
git status --short
git rev-parse 'v1.0.0^{commit}'
```

Espere seis commits distintos no total, cinco na main, um por integrante e pasta limpa.
Confira que a branch de Kaique permanece no remoto e que o PR foi fechado sem merge.
A tag `v1.0.0` aponta para o commit de Davi, etapa 4. Não mova a tag nem republique
a imagem para a mudança documental.

Para o D2L: URL do repositório público, E1–E5 e URL/print do pacote público.
O Markdown e o PDF devem apontar para essas mesmas evidências reais.
