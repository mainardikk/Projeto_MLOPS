# Recriar o projeto em outro repositório com seis commits reais

Este kit reaproveita os arquivos preparados no projeto anterior. Cada integrante deve revisar,
executar e validar sua etapa, criar o commit com sua própria identidade e fazer push usando
sua própria conta. O histórico novo será criado do zero, sem fork e sem importar os commits antigos.
Mantenham a declaração de uso de IA e de reaproveitamento da base no relatório.

## O que pode ser reaproveitado

Código, testes, CSVs, modelos, configuração Docker, workflows e documentação podem ser copiados.
Os modelos e dados já estão incluídos: não é necessário baixar novamente nem refazer a seleção
de parâmetros para começar. Os testes continuam verificando o treino com o código e os parâmetros.

As execuções do Actions, PRs, permissões, variáveis, publicação no GHCR e seus links precisam
ser gerados/configurados no novo repositório. Trocar apenas o nome do repositório nos links
antigos de Actions não cria evidências novas.

## Divisão e sequência

| Etapa | Integrante | Arquivo do kit | Destino |
|---|---|---|---|
| 1 | Thales Serschon | `01-base-original.zip` | main |
| 2 | Bruno Mainardi | `02-dados.patch` | main |
| 3 | Jhonatan Margraf | `03-adaptacao-spam.patch` | main |
| 4 | Davi Specia | `04-pipelines-drift.patch` | PR, depois main por fast-forward |
| 5 | Kaique Geska | `05-falha-controlada.patch` | PR fechado sem merge |
| 6 | Victor Ibarrola | `06-documentacao.patch` | main, partindo da etapa 4 |

```text
1 -- 2 -- 3 -- 4 -- 6    main
               \
                5       branch de falha, sem merge
```

O patch 6 NÃO é aplicado sobre a etapa 5. A configuração ruim da etapa 5 fica somente na
branch de evidência. A tag `v1.0.0` aponta para a etapa 4 e não adiciona um commit.

## Antes de começar: o responsável pelo novo repositório

1. Criar no GitHub um repositório **público e vazio**, sem fork, README, licença ou .gitignore.
2. Convidar os outros cinco integrantes com permissão de escrita; cada um aceita o convite.
3. Cada integrante trabalha em seu próprio clone e autentica o GitHub com sua própria conta.
4. Fazer as etapas em ordem; aguardar o CI da etapa anterior antes de continuar.
5. Para estas seis entregas, não usar squash, rebase de commits publicados ou o botão de merge
   que crie um commit adicional. A etapa 4 será integrada por fast-forward.

Substituam `DONO/NOVO_REPO` pela conta/organização e nome reais. Extraiam o kit fora da pasta
do novo clone, por exemplo em `C:\MLOPS_KIT`. Não adicionem o ZIP nem os patches ao Git.
Os exemplos abaixo usam PowerShell, Git e Python 3.11. Docker local é opcional: o Actions o testa.

## Configuração pessoal: cada integrante, no próprio clone

Depois de entrar na pasta do novo repositório:

```powershell
git config --local user.name "SEU NOME"
git config --local user.email "EMAIL VERIFICADO NA SUA CONTA GITHUB"
git config --local core.autocrlf false
git config --local --get user.name
git config --local --get user.email
```

Pode ser usado o email `noreply` exibido em GitHub > Settings > Emails. O nome/email acima
são os da pessoa que está fazendo a etapa. Não compartilhem tokens ou contas.

Os patches são aplicados com `git apply --index`: isso copia as alterações e as coloca no
stage, sem criar commit e sem trazer a autoria Git antiga. Não usar `git am` ou cherry-pick
com commit automático. O `git commit` seguinte é criado por quem configurou a identidade local.

## 1. Thales — base original e primeiro CI

O responsável já deve ter criado o repositório vazio e dado acesso ao Thales.

```powershell
New-Item -ItemType Directory -Path .\MLOPS_NOVO
Set-Location .\MLOPS_NOVO
$kit = "C:\MLOPS_KIT"

git init -b main
git config --local user.name "Thales Serschon"
git config --local user.email "EMAIL DO THALES VINCULADO AO GITHUB"
git config --local core.autocrlf false
git remote add origin https://github.com/DONO/NOVO_REPO.git

Expand-Archive -LiteralPath "$kit\01-base-original.zip" -DestinationPath .
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,ct]"
python demo/local.py ci

git add --all
git diff --cached --stat
git commit -m "chore: adiciona base original de CI/CD/CT para ML"
git push -u origin main
```

Primeiro confirmar os três jobs verdes em Actions. Guardar a URL desse CI inicial.
Conferir também se o commit aparece associado ao perfil do Thales antes de seguir.

Depois do primeiro push, o administrador configura:

- Settings > Actions > General: **Read and write permissions**.
- **Allow GitHub Actions to create and approve pull requests**, quando disponível.
- Settings > Secrets and variables > Actions > Variables:
  `PROMOCAO_AUTOMATICA=false` e `PERMITIR_PROMOCAO=false`.

Não disparar manualmente a promoção. Antes da etapa 4, não executar CT manual no GitHub:
o workflow antigo ainda pode propor um commit de campeão. Se a montagem atravessar o horário
da agenda semanal, desativar temporariamente apenas o workflow CT e reativá-lo antes do PR 4.

## 2. Bruno — dados reproduzíveis

Cada pessoa usa um clone novo do REPOSITÓRIO NOVO. Exemplo para Bruno:

```powershell
git clone https://github.com/DONO/NOVO_REPO.git MLOPS_BRUNO
Set-Location MLOPS_BRUNO
$kit = "C:\MLOPS_KIT"
git config --local user.name "Bruno Mainardi"
git config --local user.email "EMAIL DO BRUNO VINCULADO AO GITHUB"
git config --local core.autocrlf false
git pull --ff-only origin main

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,ct]"
git apply --index --whitespace=nowarn "$kit\02-dados.patch"
python -m mlops_demo.spambase verificar
python demo/local.py ci

git diff --cached --stat
git commit -m "feat: prepara Spambase reproduzivel sem vazamento de dados"
git push origin main
```

Esperar o CI verde. O domínio original permanece ativo nesta etapa.

## 3. Jhonatan — adaptação funcional

Clonar o novo repositório, configurar o nome/email próprios e preparar `.venv` como na etapa 2.
Trocar o nome da pasta para evitar conflito com outros clones. Com o ambiente ativo:

```powershell
$kit = "C:\MLOPS_KIT"
git config --local user.name "Jhonatan Margraf"
git config --local user.email "EMAIL DO JHONATAN VINCULADO AO GITHUB"
git config --local core.autocrlf false
git pull --ff-only origin main
git apply --index --whitespace=nowarn "$kit\03-adaptacao-spam.patch"
pip install -e ".[dev,ct]"
python -m mlops_demo.data validar
python demo/local.py ci

git diff --cached --stat
git commit -m "feat: adapta modelo API e contrato para classificacao de spam"
git push origin main
```

O patch já inclui o campeão inicial e os CSVs corretos. Não executar `data base` ou
`train --campeao` apenas para copiá-los de novo; o CI já treina o modelo atual para validar o
contrato. Reproduzir treino/seleção manualmente é possível, mas deve ser uma decisão revisada.
Guardar o CI verde após a adaptação. O Python/pacotes devem ser compatíveis com o artefato.

## 4. Davi — pipelines, PR do lote, E1, E3 e E5

Clonar o novo repositório, configurar identidade própria e criar/ativar o ambiente.

```powershell
$kit = "C:\MLOPS_KIT"
git config --local user.name "Davi Specia"
git config --local user.email "EMAIL DO DAVI VINCULADO AO GITHUB"
git config --local core.autocrlf false
git pull --ff-only origin main
git switch -c entrega/04-qualidade-operacao
git apply --index --whitespace=nowarn "$kit\04-pipelines-drift.patch"
pip install -c constraints.txt -e ".[dev,ct]"
python demo/local.py ci

git diff --cached --stat
git commit -m "feat: reforca pipelines e demonstra CT com drift por PR"
git push -u origin entrega/04-qualidade-operacao
```

Abrir no GitHub um PR dessa branch para main. Se o CT foi desativado antes, reativá-lo ANTES
de abrir o PR. Confirmar CI verde e CT com cinco atributos com drift, portão aprovado e
campeão preservado. Guardar a URL do **CT do PR como E3**.

Depois dos checks, integrar no terminal de Davi, sem botão de merge:

```powershell
git switch main
git pull --ff-only origin main
git merge --ff-only entrega/04-qualidade-operacao
git push origin main
```

O GitHub deve reconhecer o PR como integrado. Esperar o CI da main verde e guardar sua URL
como **E1**. Não habilitar a promoção; o novo workflow já avalia sem criar commits por padrão.

Ainda em main, criar a tag e disparar o CD:

```powershell
git tag -a v1.0.0 -m "Primeira publicacao da API de spam"
git push origin v1.0.0
```

Guardar o CD verde como **E5**. O nome da imagem é calculado pelo workflow a partir do novo
repositório, em letras minúsculas: `ghcr.io/dono/novo_repo:1.0.0`. Não reutilizar a imagem
`ghcr.io/mainardikk/projeto_mlops:1.0.0` como evidência de publicação do repositório novo.

Em Packages, conferir a visibilidade Public; se necessário, mudar em Package settings.
Executar CD manualmente selecionando a tag `v1.0.0` e `verificar_publica=true`. Guardar a
URL da verificação anônima, a URL do pacote e o digest exibido no Summary do CD.

## 5. Kaique — PR vermelho para E2 e E4

Clonar a main atual, configurar identidade própria e instalar com `constraints.txt`.

```powershell
$kit = "C:\MLOPS_KIT"
git config --local user.name "Kaique Geska"
git config --local user.email "EMAIL DO KAIQUE VINCULADO AO GITHUB"
git config --local core.autocrlf false
git pull --ff-only origin main
git switch -c evidencia/05-portao-reprovado
$baseAprovada = git rev-parse origin/main
git apply --index --whitespace=nowarn "$kit\05-falha-controlada.patch"
python demo/local.py ci
python demo/local.py ct
python -m mlops_demo.gate --verificar-campeao
```

Nesta etapa, os comandos CI e CT devem retornar falha: modelo inadequado e portão reprovado.
Não corrigir a precisão e não remover testes para tornar esse PR verde.

Antes de publicar, atualizar `docs/FALHA_CONTROLADA.md`: trocar a referência do commit
operacional antigo (`7041842...`) por `$baseAprovada` e conferir métricas/hash com os relatórios
locais. O SHA-256 do campeão pode ser consultado com:

```powershell
Get-FileHash -LiteralPath models/champion/model.joblib -Algorithm SHA256
```

O ensaio CT regrava `dvc.lock`. Rever o diff e restaurar SOMENTE essa alteração gerada pelo
ensaio antes de criar o commit; não adicionar candidato ou relatórios ao Git:

```powershell
git diff -- dvc.lock
git restore --worktree -- dvc.lock
git add -- params.yaml docs/FALHA_CONTROLADA.md
git diff --cached --stat
git commit -m "test: registra falha controlada e protecao do campeao"
git push -u origin evidencia/05-portao-reprovado
```

Abrir PR para main. Esperar e verificar:

- **E2:** CI vermelho especificamente nos testes de modelo; lint/código/dados aprovados.
- **E4:** CT detecta drift, DVC conclui, portão reprova e confirmação de campeão passa.
- Promoção pulada e artifact `candidato-e-relatorios` disponível.

Guardar as duas URLs e fechar o PR **sem merge**. Manter a branch remota para a evidência.
Não criar tag dessa branch. A main e a imagem publicada continuam aprovadas.

## 6. Victor — documentação do novo repositório

Clonar a main aprovada, configurar identidade própria e instalar com `constraints.txt`.
O PR de Kaique não deve estar integrado na main.

```powershell
$kit = "C:\MLOPS_KIT"
git config --local user.name "Victor Ibarrola"
git config --local user.email "EMAIL DO VICTOR VINCULADO AO GITHUB"
git config --local core.autocrlf false
git switch main
git pull --ff-only origin main
git apply --index --whitespace=nowarn "$kit\06-documentacao.patch"
git log --all --oneline
```

ANTES de fazer o sexto commit, revisar `README.md`, `ADAPTACAO.md`, `ENTREGA.md`,
`docs/OPERACAO.md` e referências em `docs/VALIDACAO.md`:

1. Trocar o endereço do projeto anterior pelo novo repositório.
2. Colocar as CINCO URLs reais de Actions obtidas agora. IDs antigos não servem no novo repo.
3. Colocar as URLs e números reais dos novos PRs, do pacote e da verificação pública.
4. Trocar imagem, digest e referências aos commits pelos valores do NOVO repositório.
5. Manter fonte/licença UCI, declaração de IA e a distribuição de integrantes correta.
6. Descrever os resultados efetivamente vistos nos novos runs, sem assumir resultados antigos.

`mainardikk` continua sendo o usuário de Bruno na tabela: não substituir o nome de usuário
isoladamente em todos os lugares. As substituições de dono/repo e imagem devem ser específicas.
Os hashes dos originais UCI e das bases não devem ser alterados para trocar o nome do repo.

Gerar o PDF a partir do Markdown atualizado, com o script auxiliar deste kit:

```powershell
python -m pip install markdown-it-py pypdf
python "$kit\gerar_relatorio.py" --repositorio https://github.com/DONO/NOVO_REPO
python demo/local.py ci
```

O script usa Chrome ou Edge em modo headless, gera `ADAPTACAO.pdf`, exige duas páginas e
confere que os links do PDF são HTTPS. Código de impressão e cache ficam em pastas ignoradas.

Após revisar todos os dados e o PDF:

```powershell
git add -- README.md ADAPTACAO.md ADAPTACAO.pdf ENTREGA.md docs/OPERACAO.md docs/VALIDACAO.md
git diff --cached --stat
git diff --cached --check
git commit -m "docs: finaliza relatorio evidencias e instrucoes de entrega"
git push origin main
```

Esperar o CI final verde. A tag v1.0.0 permanece na etapa 4, com código operacional igual;
o sexto commit finaliza documentação, sem republicar a imagem.

## Conferência final, sem criar commits extras

```powershell
git fetch origin
git log --all --format="%h | %an | %ae | %s"
git rev-list --all --count
git rev-list --count origin/main
git status --short
```

Em um clone que tenha buscado as branches do novo repo, esperar **6 commits distintos**,
**5 na main**, um commit por integrante conforme a divisão, branch de falha preservada,
PR vermelho fechado sem merge e pasta limpa. Não adicionar o repositório antigo como remoto
neste clone de entrega: isso confundiria a contagem com o histórico anterior.

Para o D2L: URL do novo repositório público, URLs E1–E5 e URL/print do novo pacote público.
O relatório Markdown e seu PDF devem apontar para essas mesmas evidências.

## Se algo falhar

- `git apply` falhou: confirmar que a etapa anterior terminou, a branch está correta e a pasta
  estava limpa antes do patch. Não usar `--reject`, não reaplicar parcialmente e não apagar
  arquivos aleatórios. Guardar a mensagem de erro e revisar a base antes de continuar.
- Não usar `--whitespace=fix`: os arquivos originais UCI têm hashes fixados. Os comandos do
  tutorial usam `nowarn`, que apenas evita avisos e preserva os bytes.
- O CI da etapa 5 deve falhar. Nas demais etapas, ler o log e resolver o problema antes de
  criar/publicar o commit, sempre que ele puder ser reproduzido localmente.
- Se um push for rejeitado, não usar force para sobrescrever o trabalho de outro integrante.
  Parar e verificar o que mudou; a execução sequencial evita esse conflito.

## Referências de configuração

- [Permissões do GitHub Actions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository).
- [Visibilidade de pacotes](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).
- [Container registry e acesso público](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).
