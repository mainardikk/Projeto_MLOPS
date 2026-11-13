# Operação, cenários e evidências

## Controles comuns

O contrato permanece precisão de spam >= 0,93 e recall >= 0,85, sem regressão de precisão
em relação ao campeão no mesmo conjunto. As dependências diretas de execução e das
ferramentas de CI/CT estão fixadas em `constraints.txt`, também usado pelo Docker.
As dependências transitivas ainda são resolvidas pelo pip; este arquivo não é um lock completo.

O CI mantém três jobs: lint, Python 3.11 e Python 3.12. O job 3.11 constrói a imagem e
testa a API em container. O CI reutilizado pelo CD valida os testes; o próprio CD executa
a construção e os testes Docker. O teste de fumaça consulta `/health` e `/schema`, envia
os primeiros exemplos fixos de cada classe do holdout e exige as duas respostas. Também
confere versão, probabilidade e rejeição de frequência acima de 100% com HTTP 422.

Esse teste de fumaça é um teste de integração, não uma estimativa de qualidade do modelo.
As métricas do contrato são verificadas pelos testes de modelo e pelo portão.

## Lote de demonstração e E3

O cenário 4 gera 400 linhas da reserva com semente 1 e multiplica por 3 seis frequências:
`word_freq_free`, `word_freq_money`, `char_freq_dollar`, `char_freq_exclamation`,
`word_freq_you` e `word_freq_your`. Os percentuais são limitados a 100; rótulos e outras
colunas são preservados. O JSON registra índices da reserva, seu hash, fator e hash do CSV.

O gerador não sobrescreve lotes nem reutiliza suas linhas em outros lotes. O carregamento
verifica os hashes e reconstrói os valores esperados a partir da origem declarada. Isso
impede que a mesma mensagem de origem apareça em treino e avaliação sob fatores diferentes.
O esquema foi feito para estes lotes acadêmicos derivados da reserva; dados de produção
exigiriam outro processo de ingestão e atribuição de identidade.

Cada lote é dividido por regra fixa: metade treina, metade avalia, com estratificação e
semente 42. O lote fornecido acrescenta 200 linhas em cada lado, resultando em **2.722 linhas
de treino e 1.041 de avaliação**. O preparo rejeita vetores repetidos internos e compartilhados
entre os conjuntos.

Na calibração, com n=400 e semente 1 fixos, o fator 2 alterou significativamente três
atributos e não disparou o limiar de quatro. O fator 3 foi o primeiro da grade `[2,3,4,5]`
que disparou: cinco atributos, com p < 0,01. Os resultados completos estão em
[`calibracao_drift.json`](calibracao_drift.json).

| Modelo no mesmo conjunto de 1.041 linhas | Precisão de spam | Recall de spam |
|---|---:|---:|
| Campeão inicial | 0,934555 | 0,864407 |
| Candidato retreinado | 0,944444 | 0,864407 |

O portão aprovou o candidato sem alterar o campeão. O lote é uma simulação calibrada para
demonstrar a operação: seus rótulos foram mantidos após transformar os atributos. A aprovação
neste cenário não demonstra adaptação bem-sucedida a emails reais novos. O KS é aplicado a
57 atributos sem correção de testes múltiplos; o limiar de quatro atributos reduz alarmes
isolados, mas não garante controle formal da taxa de falsos alarmes.

## Promoção explícita e preservação do campeão

Em PRs e nas execuções usuais da main, o CT valida, detecta drift, retreina com DVC e aplica
o portão. Candidato e relatórios ficam nos artifacts. **Nenhum commit é criado por padrão.**

Para habilitar uma promoção futura na main, fora do orçamento das seis entregas, use
`workflow_dispatch` com `promover=true` ou a variável `PERMITIR_PROMOCAO=true`.
A variável `PROMOCAO_AUTOMATICA` escolhe então entre PR de promoção (`false`) e publicação
direta/tag/CD (`true`). Os dois controles são independentes; um PR de promoção também cria
um commit. Mantenha a permissão de promoção desativada durante as evidências atuais.

O relatório do portão registra hashes do candidato, campeão, métricas do campeão, avaliação,
contrato e parâmetros. Uma promoção é bloqueada se algum desses arquivos mudou após a
avaliação. Uma reprovação também impede a cópia do candidato.

Após o portão, mesmo quando ele reprova, o workflow verifica que os hashes do modelo e das
métricas do campeão continuam iguais e grava `reports/champion_preservation.json`. O Summary
registra essa confirmação. Isso fornece a prova de preservação exigida na E4.

## Cinco cenários, sem commits de ensaio

Os testes de `tests/test_cenarios.py` executam as cinco alterações em cópias temporárias.
O projeto ativo não é corrompido por esses testes. Para aplicar manualmente, use uma branch
própria e revise o diff antes de publicar:

```powershell
python demo/cenarios.py listar
python demo/cenarios.py aplicar N
```

| N | Alteração | Resultado esperado |
|---|---|---|
| 1 | Remove `capital_run_length_total` das entradas | CI vermelho na camada de código |
| 2 | Nulos em `word_freq_free` e `char_freq_dollar` negativo | Validação de dados vermelha |
| 3 | `C=0.0000001` | Testes de modelo vermelhos por recall baixo |
| 4 | Lote de 400 linhas com drift | CI verde e CT com drift/portão aprovado |
| 5 | Lote com drift e peso `{0:1, 1:10000}` | Recall alto e precisão baixa; CI e portão vermelhos |

O cenário 4 é idempotente: valida o lote existente e não o sobrescreve. O cenário 5 garante
que esse lote existe antes de alterar os parâmetros; isso faz o CT chegar ao portão.
E2 e E4 podem ser obtidas no mesmo PR do cenário 5, economizando um commit. Esse PR deve
ser fechado sem merge. Não aplique cenários 1, 2, 3 ou 5 na main.

## Publicação com tag e E5

Após o CI e CT do PR aprovarem, avance a main para o mesmo commit por fast-forward, evitando
um commit de merge. Aguarde o CI na main e crie a tag `v1.0.0` apontando para esse commit.
A tag não aumenta a quantidade de commits.

O CD constrói uma imagem, testa-a e publica **essa mesma imagem**, sem segunda construção.
Depois baixa a referência do GHCR, compara o ID com o da imagem testada e repete o teste HTTP.
O Summary registra imagem, digest e commit. Essa primeira verificação usa autenticação de
publicação; a visibilidade pública é uma etapa adicional.

Na página do pacote, abra **Package settings > Change visibility > Public**. O GitHub
documenta esse controle em [visibilidade de pacotes](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).
O pacote esperado é [projeto_mlops](https://github.com/users/mainardikk/packages/container/package/projeto_mlops).

Em Actions, execute **CD** manualmente na tag `v1.0.0`, marcando `verificar_publica=true`.
Esse modo usa um runner com configuração Docker vazia: baixa sem autenticação e testa a
imagem, sem republicar. O job de publicação fica pulado por desenho.

Para reproduzir em uma máquina com Docker:

```powershell
docker run --rm -p 8000:8000 ghcr.io/mainardikk/projeto_mlops:1.0.0
python demo/smoke_test.py http://localhost:8000 --aguardar 60
```

Os links finais de E1–E5 e do pacote serão consolidados no relatório da sexta entrega.
