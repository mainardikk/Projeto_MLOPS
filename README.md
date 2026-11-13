# Filtro de spam com CI/CD/CT

Adaptação do [projeto de Wesley Sobreira](https://github.com/wesleyasantos/ci_cd_ct_mlops)
para classificação binária de mensagens usando o **Spambase**. O modelo recebe **57 atributos
numéricos**, classifica a mensagem como `spam` ou `legitimo` e publica uma API FastAPI.
O repositório da equipe foi criado sem fork e sem o histórico Git do projeto original.

**Etapa atual: commit 4 de 6.** Spambase ativo, 75 testes locais, cinco cenários adaptados e
lote de demonstração com proveniência. CI, CT e CD têm controles de qualidade e teste de
fumaça; os links das execuções e a entrega final serão consolidados em `ADAPTACAO.md`.
O roteiro de operação está em [docs/OPERACAO.md](docs/OPERACAO.md).

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

## Docker e GitHub

```powershell
docker build -t projeto-mlops:local .
docker run --rm -p 8000:8000 projeto-mlops:local
python demo/smoke_test.py http://localhost:8000
```

Para o CT propor um campeão, configure no GitHub **Settings > Actions > General** as permissões
**Read and write** e **Allow GitHub Actions to create and approve pull requests**. Em
**Settings > Secrets and variables > Actions > Variables**, use `PROMOCAO_AUTOMATICA=false`.
Nenhum token deve ser adicionado aos arquivos do projeto; o workflow usa o `GITHUB_TOKEN`.

O teste Docker e a primeira publicação com tag serão registrados na etapa de CD. Após publicar,
o pacote deverá ficar público e ser validado com o teste de fumaça sobre a imagem baixada.
Para testar a imagem pública sem credenciais, execute o CD manualmente na tag `v1.0.0` com
`verificar_publica=true`, após alterar a visibilidade do pacote para Public. Esse modo somente
baixa e testa a imagem, sem republicá-la nem criar commits.

As cinco URLs de evidências e a declaração de contribuição/uso de IA entrarão no `ADAPTACAO.md`
na entrega final. A aprovação do CI inicial e o histórico anterior continuam disponíveis no Git.
