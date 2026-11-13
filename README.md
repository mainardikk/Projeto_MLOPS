# Filtro de spam com CI/CD/CT

Adaptação do [projeto de Wesley Sobreira](https://github.com/wesleyasantos/ci_cd_ct_mlops)
para classificação binária de mensagens usando o **Spambase**. O modelo recebe **57 atributos
numéricos**, classifica a mensagem como `spam` ou `legitimo` e publica uma API FastAPI.
O repositório da equipe foi criado sem fork e sem o histórico Git do projeto original.

**Entrega técnica consolidada em seis commits**, contando a branch da falha fechada sem merge.
Spambase ativo, 75 testes, cinco cenários adaptados, evidências E1–E5 e imagem pública testada.
O [relatório ADAPTACAO.md](ADAPTACAO.md) apresenta as alterações, limites, uso de IA e a
distribuição das seis entregas entre os integrantes. A [versão PDF](ADAPTACAO.pdf) tem duas páginas A4.
Os links para envio estão em [ENTREGA.md](ENTREGA.md); o roteiro técnico, em
[docs/OPERACAO.md](docs/OPERACAO.md).

## Evidências da entrega

| Evidência | Execução e resultado |
|---|---|
| E1 | [CI na main](https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43355820648): três jobs verdes, incluindo Docker. |
| E2 | [CI com falha controlada](https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43358312788): testes de modelo vermelhos em Python 3.11/3.12. |
| E3 | [CT com drift aprovado](https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43355508124): cinco atributos com drift e portão aprovado. |
| E4 | [CT reprovado no portão](https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43358312669): precisão insuficiente e campeão preservado. |
| E5 | [CD com tag v1.0.0](https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43356110304): imagem testada, publicada e testada após download. |

O [PR #1](https://github.com/mainardikk/Projeto_MLOPS/pull/1) foi integrado por fast-forward.
O [PR #2](https://github.com/mainardikk/Projeto_MLOPS/pull/2), intencionalmente vermelho, foi
fechado sem merge. A falha está na branch `evidencia/05-portao-reprovado`; a main mantém a
configuração aprovada. O [CI mais recente da main](https://github.com/mainardikk/Projeto_MLOPS/actions/workflows/ci.yml?query=branch%3Amain)
também permite acompanhar a revisão final de documentação.

## Histórico das seis entregas

A base original teve [CI verde antes da adaptação](https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43346672807).
O histórico foi mantido sem commits adicionais de merge:

| Entrega | Referência | Conteúdo |
|---|---|---|
| 1 | [970867d](https://github.com/mainardikk/Projeto_MLOPS/commit/970867d) | Base original e ambiente |
| 2 | [0f1cb05](https://github.com/mainardikk/Projeto_MLOPS/commit/0f1cb05) | Preparação reproduzível do Spambase |
| 3 | [728be4e](https://github.com/mainardikk/Projeto_MLOPS/commit/728be4e) | Adaptação funcional para spam |
| 4 | [7041842](https://github.com/mainardikk/Projeto_MLOPS/commit/7041842) | Qualidade, operação, drift e publicação |
| 5 | [ac403ee](https://github.com/mainardikk/Projeto_MLOPS/commit/ac403ee) | Falha controlada, mantida fora da main |
| 6 | Esta revisão da main | Documentação, relatório e conferência final |

Assim, há cinco commits na main e um na branch de evidência, totalizando seis commits
distintos. A tag `v1.0.0` não cria outro commit e continua no código operacional da entrega 4.

## Problema, dados e contrato

O uso proposto é encaminhar mensagens suspeitas para uma pasta de spam. A classe positiva é
**spam (`1`)**; `0` representa mensagem legítima. O erro mais caro é o **falso positivo**, quando
uma mensagem legítima é marcada como spam. Por isso a métrica principal é a precisão de spam.

| Regra do portão | Limite |
|---|---:|
| Precisão de spam do candidato | >= 0,93 |
| Recall de spam do candidato | >= 0,85 |
| Precisão do candidato no mesmo conjunto do campeão | >= precisão do campeão |

O recall mínimo impede um filtro que identifica apenas poucos spams para obter alta precisão.
O teste de sanidade do campeão no holdout histórico exige precisão >= 0,90 e recall >= 0,80;
ele complementa o contrato medido na certificação. Há também um teste de falsos positivos
entre mensagens legítimas, com limite de 5% para o modelo treinado pelo CI.

O Spambase foi publicado por Mark Hopkins, Erik Reeber, George Forman e Jaap Suermondt (1999),
na [UCI](https://archive.ics.uci.edu/dataset/94/spambase), sob
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
DOI: [10.24432/C53G6X](https://doi.org/10.24432/C53G6X).

Das 4.601 linhas originais, removemos seis pertencentes a grupos com rótulos conflitantes e
391 repetições. A divisão estratificada com semente 42 contém:

| Conjunto | Linhas | Função |
|---|---:|---|
| Treino | 2.522 | Ajustar o modelo e fazer validação interna |
| Holdout | 841 | Avaliação fixa e regressão do CI |
| Reserva | 841 | Origem dos lotes do CT |

Não há sobreposição de atributos entre os conjuntos. Fonte, licença, esquema, limpeza e hashes
estão em [data/spambase/README.md](data/spambase/README.md).

## Modelo e resultado inicial

O pipeline usa **log1p + StandardScaler + regressão logística**. O logaritmo reduz a assimetria
das frequências e contagens. Os hiperparâmetros e a grade de seleção estão em `params.yaml`.
Cada fold de validação ajusta seu próprio scaler, usando somente o treino daquele fold.

| Medida | Validação interna, 5 folds | Holdout, 841 linhas |
|---|---:|---:|
| Precisão de spam | 94,28% | 94,70% |
| Recall de spam | 90,15% | 85,12% |
| Acurácia | 93,89% | 92,15% |

No holdout ocorreram 16 falsos positivos e 50 falsos negativos. O recall ficou próximo do
limite. Uma primeira configuração foi reprovada, e o critério de seleção foi revisto depois
dessa consulta ao holdout. Esse histórico e a limitação da avaliação estão registrados em
[docs/VALIDACAO.md](docs/VALIDACAO.md); não apresentamos o holdout como um teste final intocado.

## O que cada pipeline faz

| Pipeline | Arquivo | Gatilho e responsabilidade |
|---|---|---|
| CI | `.github/workflows/ci.yml` | Push na main e PRs; lint, testes em Python 3.11/3.12 e Docker no job 3.11 |
| CT | `.github/workflows/ct.yml` | Novos lotes ou params alterados verificam drift; agenda/manual sempre retreinam; DVC gera candidato e o portão decide |
| CD | `.github/workflows/cd.yml` | Tag `v*.*.*`; executa CI, constrói Docker, testa a API e publica no GHCR |

O monitor compara os 57 atributos por KS, com p < 0,01. O gatilho atual exige pelo menos quatro
atributos com drift. A simulação modifica seis frequências promocionais e mantém valores de
0 a 100. Mudança de distribuição não prova perda de qualidade; o portão avalia o candidato.

O CT **avalia sem promover por padrão**, tanto em PRs quanto na main. Uma promoção na main
requer execução manual com `promover=true` ou a variável `PERMITIR_PROMOCAO=true`. Só então
`PROMOCAO_AUTOMATICA=false` propõe o campeão por PR, ou `true` publica e cria uma tag.
Durante as seis entregas, mantenha `PERMITIR_PROMOCAO` ausente/false e `promover=false`.
O candidato aprovado fica nos artifacts; o campeão versionado continua sendo o inicial.

## Executar localmente no PowerShell

Use Python 3.11, também usado no Docker e no CI. O projeto mantém o pacote `mlops_demo`.
Se o ambiente `.venv` já existe nesta máquina, comece pela ativação, sem recriá-lo.

```powershell
# Criar o ambiente, caso ainda não exista.
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -c constraints.txt -e ".[dev,ct]"

# Código, dados, modelo e contrato da API.
python demo/local.py ci

# Drift, preparação/treino com DVC e portão, sem promover nem publicar.
python demo/local.py ct
```

No CT local, `demo/local.py` sempre executa o retreino, mesmo sem drift. No workflow do GitHub,
eventos de push/PR sem drift não retreinam. Mantenha o ambiente ativo: os comandos do `dvc repro`
usam o `python` disponível no PATH. O `dvc.lock` é versionado; candidatos e relatórios são locais.

Para conferir a origem e reproduzir as bases sem baixar novamente:

```powershell
python -m mlops_demo.spambase verificar
python -m mlops_demo.data base
python -m mlops_demo.data validar
```

Para reproduzir a seleção interna e a criação inicial do campeão:

```powershell
python -m mlops_demo.train --selecionar
python -m mlops_demo.train --validar
python -m mlops_demo.train --campeao
```

`--selecionar` apenas informa o resultado: não edita `params.yaml`. `--campeao` é destinado à
criação inicial; promoções posteriores devem passar pelo CT e pela revisão prevista no fluxo.
A reserva fica fora do treino inicial e não depende de download durante os testes.
O lote de demonstração utiliza 400 linhas da reserva: 200 para treino e 200 para avaliação.
O JSON ao lado do CSV registra índices de origem, fator e hashes. Outros lotes usam somente
linhas ainda disponíveis. O pipeline rejeita origem repetida, conteúdo alterado e vazamento.

## API e teste de fumaça

```powershell
uvicorn mlops_demo.api:app --host 127.0.0.1 --port 8000
# Em outro terminal, na raiz do projeto:
python demo/smoke_test.py http://localhost:8000
```

- `GET /health`: saúde, versão do código e métricas do campeão.
- `GET /schema`: nomes e ordem dos 57 atributos, alvo e rótulos.
- `POST /predict`: JSON com `atributos`, uma lista de exatamente 57 números.
- `GET /docs`: documentação interativa e esquema de entrada.

A resposta de `/predict` contém `classe` (`spam` ou `legitimo`), `probabilidade_spam` (classe 1)
e `versao_codigo`. A API valida frequências percentuais, sequências de maiúsculas, números
finitos e tamanho da lista. Textos, booleanos e campos extras são rejeitados com HTTP 422.
Não envie texto de emails: esta API espera os atributos numéricos já extraídos.

## Imagem pública e execução Docker

Imagem publicada: **`ghcr.io/mainardikk/projeto_mlops:1.0.0`**, no
[GitHub Packages](https://github.com/mainardikk/Projeto_MLOPS/pkgs/container/projeto_mlops).
O [download anônimo e teste HTTP](https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43356673814)
passaram em um runner com configuração Docker vazia.

Na raiz deste repositório, com Docker disponível:

```powershell
docker pull ghcr.io/mainardikk/projeto_mlops:1.0.0
docker run --rm -p 8000:8000 ghcr.io/mainardikk/projeto_mlops:1.0.0
# Em outro terminal, na raiz do repositório:
python demo/smoke_test.py http://localhost:8000 --aguardar 60
```

Para baixar exatamente o digest verificado, em vez da tag:

```powershell
docker pull ghcr.io/mainardikk/projeto_mlops@sha256:a1e1983804e44ff55f0e888b100131b93f8389a9f3649a47650cae2118579820
```

O teste HTTP usa exemplos versionados em `data/raw/base_holdout.csv`; execute o script a
partir de um checkout do projeto. A imagem contém código e campeão, sem os dados de treino.
A tag `v1.0.0` aponta para `7041842`, que contém o código operacional publicado. A última
entrega altera documentação; não houve nova promoção ou republicação da imagem.

Para construir uma imagem local:

```powershell
docker build -t projeto-mlops:local .
docker run --rm -p 8000:8000 projeto-mlops:local
python demo/smoke_test.py http://localhost:8000
```

## Configuração do GitHub e promoção

Para o CT propor um campeão, configure no GitHub **Settings > Actions > General** as permissões
**Read and write** e **Allow GitHub Actions to create and approve pull requests**. Em
**Settings > Secrets and variables > Actions > Variables**, use `PROMOCAO_AUTOMATICA=false`.
Nenhum token deve ser adicionado aos arquivos do projeto; o workflow usa o `GITHUB_TOKEN`.

Para repetir a verificação pública, execute o CD manualmente na tag `v1.0.0` com
`verificar_publica=true`. Esse modo somente baixa e testa a imagem, sem republicá-la nem criar
commits. O desafio opcional de promoção automática não foi realizado.

## Limitações e participação

O portão não garante generalização: há um corpus antigo, amostra finita, recall próximo do
limite e consulta prévia ao holdout durante o desenvolvimento. O drift é sintético, com
rótulos preservados; a detecção KS não usa correção para testes múltiplos. Em produção,
monitoraríamos falsos positivos, precisão/recall por segmento, prevalência, qualidade de
dados/rótulos, drift, latência e erros da API. Detalhes em [VALIDACAO.md](docs/VALIDACAO.md).

O projeto é uma entrega coletiva do grupo, com responsabilidades organizadas por etapa:

| Integrante | Commit / entrega | Responsabilidade |
|---|---:|---|
| Thales Serschon | 1 | Ambiente, projeto base e CI inicial |
| Bruno Mainardi | 2 | Preparação reproduzível do Spambase |
| Jhonatan Margraf | 3 | Adaptação funcional do modelo e da API |
| Davi Specia | 4 | Qualidade e operação dos pipelines |
| Kaique Geska | 5 | Falha controlada e proteção do campeão |
| Victor Ibarrola | 6 | Documentação e conferência da entrega |

O [relatório](ADAPTACAO.md#6-contribuições-e-declaração-de-ia) detalha essa distribuição e a
declaração de uso de IA pelo grupo.
