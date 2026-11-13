# Spambase: preparação reproduzível

Os dados desta pasta são a fonte reproduzível do pipeline de spam. Desde o commit 3,
`preparado/base_treino.csv` e `preparado/base_holdout.csv` estão copiados, byte a byte, para
`data/raw/`, alimentando o modelo e a API. A reserva permanece separada para os lotes do CT.

## Fonte e atribuição

- **Dataset:** Spambase, UCI Machine Learning Repository.
- **Autores:** Mark Hopkins, Erik Reeber, George Forman e Jaap Suermondt (1999).
- **Página:** <https://archive.ics.uci.edu/dataset/94/spambase>.
- **DOI:** <https://doi.org/10.24432/C53G6X>.
- **Licença dos dados originais e desta adaptação:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Download oficial:** <https://archive.ics.uci.edu/static/public/94/spambase.zip>.

Citação: Hopkins, M., Reeber, E., Forman, G., & Suermondt, J. (1999).
*Spambase [Dataset]*. UCI Machine Learning Repository. <https://doi.org/10.24432/C53G6X>.

A atribuição e a descrição das alterações acompanham os dados conforme a licença. A fonte não
endossa este projeto. Esta preparação usa somente atributos numéricos publicados; não inclui
textos dos emails, endereços de remetentes ou conteúdo de caixas de correio.

## Arquivos e esquema

```text
data/spambase/
  README.md
  original/
    spambase.data           # fonte sem cabeçalho, bytes originais da UCI
    spambase.names          # descrição original e ordem das colunas
  preparado/
    base_treino.csv
    base_holdout.csv
    base_reserva.csv
    manifesto.json          # procedência, políticas, contagens, classes e hashes
```

O original contém **4.601 linhas, 57 atributos numéricos e um alvo binário**. O alvo `spam` vale
`1` para spam e `0` para mensagem legítima. Não foram encontrados valores ausentes nos arquivos
obtidos. A página da UCI apresenta informações divergentes sobre valores ausentes; a conferência
é feita diretamente nos dados, sem imputação silenciosa.

Mantemos a ordem dos 48 atributos `word_freq_*`, seguidos pelos seis atributos `char_freq_*` e
pelos três `capital_run_length_*`. As frequências são percentuais de 0 a 100. Os comprimentos
de sequências de maiúsculas têm mínimo 1; maior sequência e total são inteiros, respeitando
`média <= maior sequência <= total`.

Somente os nomes dos seis atributos com símbolos são normalizados:

| Original UCI | Nome preparado |
|---|---|
| `char_freq_;` | `char_freq_semicolon` |
| `char_freq_(` | `char_freq_parenthesis` |
| `char_freq_[` | `char_freq_bracket` |
| `char_freq_!` | `char_freq_exclamation` |
| `char_freq_$` | `char_freq_dollar` |
| `char_freq_#` | `char_freq_hash` |

## Duplicatas e alterações realizadas

A análise considera igualdade dos **57 atributos**, sem usar o alvo para identificar o mesmo
registro. Isso impede que vetores iguais com rótulos distintos acabem em conjuntos diferentes.

| Medida no original | Quantidade |
|---|---:|
| Linhas originais | 4.601 |
| Duplicatas completas excedentes, incluindo o alvo | 391 |
| Duplicatas de atributos excedentes, ignorando o alvo | 394 |
| Grupos com atributos iguais e rótulos conflitantes | 3 |
| Linhas removidas por pertencerem a esses grupos | 6 |
| Repetições removidas após excluir os conflitos | 391 |
| Linhas disponíveis para divisão | **4.204** |

As duas medidas de duplicatas são diagnósticos alternativos, não devem ser somadas.
Primeiro excluímos **todas** as linhas dos grupos conflitantes, sem escolher um rótulo por
maioria ou pela ordem. Depois mantemos a primeira ocorrência de cada vetor restante.
A limpeza ocorre antes da divisão e não consulta resultados de modelos. Excluir conflitos
reduz a amostra e pode favorecer casos menos ambíguos; esse limite deve acompanhar a avaliação.

As demais alterações são cabeçalho, normalização dos seis nomes e conversão do alvo e das duas
contagens para inteiros. Não aplicamos escala, imputação, seleção de atributos nem balanceamento.

## Divisão fixa e sem sobreposição

Usamos `train_test_split` em duas etapas, com estratificação pelo alvo e **semente 42**:
60% para treino; os 40% restantes são divididos igualmente entre holdout e reserva.
O arredondamento resulta nas quantidades abaixo.

| Conjunto | Linhas | Legítimas (`0`) | Spam (`1`) | Uso |
|---|---:|---:|---:|---|
| Treino | 2.522 | 1.517 | 1.005 | Ajustar o modelo; validação interna para decisões |
| Holdout | 841 | 505 | 336 | Avaliação fixa; fora do treino e da seleção de parâmetros |
| Reserva | 841 | 506 | 335 | Origem dos futuros lotes do CT |

Não há vetores de atributos repetidos dentro dos conjuntos nem compartilhados entre eles.
A união cobre a base limpa. Desde o commit 4, o lote `data/raw/lotes/lote_demo_spam.csv`
usa 400 linhas da reserva, registradas no JSON ao lado do CSV. A reserva versionada continua
intacta; a geração de outro lote exclui os índices já utilizados, restando 441 disponíveis.
O manifesto registra a distribuição de classes e o SHA-256 de cada CSV.

## Como reproduzir e verificar

Na raiz do projeto, com as dependências instaladas e o ambiente virtual ativo:

```bash
# Opcional: obter novamente os dois originais da UCI (precisa de internet).
python -m mlops_demo.spambase baixar

# Recriar somente data/spambase/preparado/, usando os originais versionados.
python -m mlops_demo.spambase preparar

# Conferir a fonte e recalcular tudo em memória; não modifica arquivos nem usa rede.
python -m mlops_demo.spambase verificar

# Ativar novamente os mesmos CSVs em data/raw/ (não troca a divisão).
python -m mlops_demo.data base

# Executar os testes do pipeline de spam e da preparação reproduzível.
python demo/local.py ci
```

Os hashes esperados da fonte estão fixados em `src/mlops_demo/spambase.py` e no manifesto.
Um original divergente interrompe a preparação. O comando `verificar` exige igualdade byte a
byte dos três CSVs e do manifesto com a reconstrução. Assim, um CSV alterado não é corrigido
silenciosamente para fazer o teste passar.

Os originais têm normalização de texto desativada em `.gitattributes`, preservando os hashes
também em checkouts no Windows e no Linux. Os CSVs derivados usam UTF-8, finais de linha LF e
formatação numérica explícita. O manifesto não contém horário ou caminho absoluto da máquina.

## Limites dos dados

O corpus é de 1999 e contém indicadores associados ao contexto original de coleta, como
`word_freq_george` e `word_freq_650`. Não representa automaticamente os emails atuais.
Uma divisão aleatória evita sobreposição exata, mas não mede generalização temporal nem
garante ausência de mensagens semelhantes. Esta entrega prepara dados para fins acadêmicos;
a utilidade de um filtro em produção exige avaliação e monitoramento adicionais.
