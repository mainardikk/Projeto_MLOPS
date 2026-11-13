# Escolha do modelo e avaliação do campeão inicial

## Problema e contrato

O usuário considerado é uma pessoa ou equipe que precisa encaminhar mensagens suspeitas para
uma pasta de spam. O modelo recebe 57 atributos numéricos do Spambase, não o texto de emails.
A classe positiva é **spam (`1`)**. Um falso positivo oculta uma mensagem legítima e pode levar
à perda de uma comunicação importante; por isso, **precisão é a métrica principal**.

O contrato exige precisão de spam **>= 0,93** e recall **>= 0,85**. O primeiro limite busca
restringir mensagens legítimas entre as classificadas como spam; o segundo impede obter alta
precisão detectando apenas uma parcela pequena dos spams. São limites acadêmicos justificados
pelo uso proposto, não garantias universais de segurança de um filtro. O portão compara os
modelos no mesmo conjunto e também impede queda de precisão em relação ao campeão.

## Seleção no treino

Usamos somente as **2.522 linhas de treino** para comparar parâmetros, em cinco folds
estratificados, embaralhados com semente 42. Cada previsão de validação é obtida por um modelo
que não treinou naquela linha. O pipeline ajusta o scaler dentro de cada fold, evitando usar
estatísticas da avaliação. As 841 linhas da reserva ficaram fora da seleção inicial;
400 delas foram posteriormente usadas no lote de demonstração do CT, com origem registrada.

As frequências e os comprimentos apresentam escalas e caudas diferentes. A comparação interna
favoreceu `log1p`, seguido de `StandardScaler` e regressão logística, por melhorar o recall.
`log1p(0) = 0`, e todos os atributos do domínio são não negativos.

Na primeira escolha, `C=1.0`, pesos `{0: 1.5, 1: 1.0}` e `log1p` deram precisão de **94,35%** e
recall de **89,65%** nas predições fora dos folds. Entretanto, ao avaliar no holdout, a precisão
foi **95,32%** e o recall **84,82%** (285 de 336 spams detectados). O contrato bloqueou a gravação
desse candidato como campeão. Não alteramos o holdout nem reduzimos seus limiares.

Após essa reprovação, reforçamos o critério de seleção interna: além de precisão >= 0,93,
exigir recall >= **0,90** na validação, criando uma margem sobre o contrato de 0,85. A busca
usou `C` em `[0.1, 1.0, 10.0]` e pesos da classe legítima em `[1.0, 1.15, 1.25, 1.5]`, com peso
da classe spam fixo em `1.0`. Entre os elegíveis, escolhemos maior precisão, depois maior recall
e, em caso de empate, menor `C`. O resultado foi **C=10.0 e pesos {0: 1.5, 1: 1.0}**.

O resultado das 12 combinações está em [`selecao_modelo.json`](selecao_modelo.json). A grade e
os parâmetros escolhidos estão no `params.yaml`. Para reproduzir a busca e a validação atual:

```bash
python -m mlops_demo.train --selecionar
python -m mlops_demo.train --validar
```

Esses comandos não leem o holdout e não editam os parâmetros automaticamente.

## Campeão inicial aprovado

| Medida | Validação interna, fora dos folds | Holdout fixo |
|---|---:|---:|
| Amostras | 2.522 | 841 |
| Precisão de spam | 0,942768 | 0,947020 |
| Recall de spam | 0,901493 | 0,851190 |
| Acurácia | 0,938937 | 0,921522 |
| Falsos positivos | 55 | 16 |
| Falsos negativos | 99 | 50 |

No holdout há 505 mensagens legítimas e 336 spams. O modelo acertou 489 legítimas e 286 spams.
A taxa de falsos positivos entre as legítimas foi 16/505, aproximadamente **3,17%**. Há um teste
de comportamento que exige essa taxa <= 5%, complementando o contrato de precisão e recall.

As métricas exatas, os parâmetros, a validação interna e os hashes das bases usadas estão em
`models/champion/metrics.json`. O artefato é gerado por:

```bash
python -m mlops_demo.train --campeao
```

O comando verifica o contrato antes de salvar. O candidato do CT, por sua vez, é sempre salvo
para que o portão possa registrar uma eventual reprovação e preservar o campeão.

## Limites desta avaliação

O recall ficou próximo do limite: uma previsão correta a menos resultaria em 285/336, abaixo
de 0,85. A aprovação não demonstra margem estatística robusta nem garante desempenho futuro.

O critério de seleção foi revisto **depois de consultar o holdout na tentativa reprovada**.
Embora a segunda busca tenha lido somente o treino, a avaliação final já não é um teste
totalmente independente do desenvolvimento. Registramos ambas as tentativas para não ocultar
essa limitação. Uma validação externa futura exigiria novos dados não usados nesse processo.
O holdout é ainda reutilizado nos testes de regressão do CI, o que pode favorecer ajustes
indiretos ao longo do tempo. Não usamos a reserva para compensar esse problema.

O teste direcional verifica uma hipótese local: aumentar `free`, `money`, `$` e `!`, mantendo
os demais atributos, não reduz a probabilidade média de spam na amostra de treino examinada.
Essa hipótese não prova causalidade nem vale para toda mensagem possível.

O dataset de 1999 é limitado pelo contexto de coleta e não representa automaticamente o spam
atual. Em produção, seriam necessários dados recentes, métricas por segmento, monitoramento
de falsos positivos, recall, prevalência, drift e qualidade dos rótulos.
