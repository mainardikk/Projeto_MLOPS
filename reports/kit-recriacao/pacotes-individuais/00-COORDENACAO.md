# Coordenação da recriação — um pacote por integrante

Novo repositório público: [https://github.com/thalescr77/Projeto_MLOPS](https://github.com/thalescr77/Projeto_MLOPS). Dono: `thalescr77`.
Envie a cada integrante somente o ZIP com o nome dele. Cada pessoa extrai o ZIP,
abre `LEIA-PRIMEIRO.md` e executa sua etapa no próprio PC e na própria conta GitHub.
Os tutoriais usam Windows/PowerShell, Git e Python 3.11; Docker local é opcional.

## Ordem obrigatória

| Ordem | ZIP | Quem executa | Condição para passar ao próximo |
|---|---|---|---|
| 1 | `01-Thales.zip` | Thales (`thalescr77`) | Primeiro commit e CI verde; convites/configurações feitos. |
| 2 | `02-Bruno.zip` | Bruno (`mainardikk`) | Dados validados, segundo commit e CI verde. |
| 3 | `03-Jhonatan.zip` | Jhonatan (`Jhonatan-Margraf`) | Adaptação validada, terceiro commit e CI verde. |
| 4 | `04-Davi.zip` | Davi (`davispecia`) | PR integrado por fast-forward; E1/E3/E5 e pacote público conferidos. |
| 5 | `05-Kaique.zip` | Kaique (`kaiquegeska`) | E2/E4 conferidos; PR vermelho fechado sem merge. |
| 6 | `06-Victor.zip` | Victor (`VictorOliveiraIbarrola`) | Documentação/PDF com evidências novas e CI final verde. |

A divisão de responsabilidades é a mesma do kit original. Confirmem se os usuários estão
corretos antes de convidar. Cada integrante informa no próprio PC seu email verificado ou
`noreply`; não precisa enviar senha, token ou conta para o coordenador.

## O que Thales configura

Convide os outros cinco integrantes com acesso de escrita e peça que aceitem o convite.
Depois do primeiro push, em Settings > Actions > General habilite Read and write permissions
e, quando disponível, Allow GitHub Actions to create and approve pull requests.
Em Settings > Secrets and variables > Actions > Variables, defina
`PROMOCAO_AUTOMATICA=false` e `PERMITIR_PROMOCAO=false`.

Antes da etapa 4, não execute CT manualmente. Se o processo atravessar segunda-feira às
03h de Brasília, desative temporariamente só o CT; Davi precisa reativá-lo antes de abrir o PR.
Se Davi não puder alterar a visibilidade do pacote, Thales deixa o pacote GHCR público.

## Histórico e evidências

```text
1 -- 2 -- 3 -- 4 -- 6    main (5 commits)
               \
                5       branch de falha, PR fechado sem merge
```

São seis commits distintos no total. A tag `v1.0.0` aponta para a etapa 4 e não adiciona
um commit. Não usar squash, rebase de commits publicados, merge com commit adicional,
importação do histórico antigo ou commits automáticos de promoção.

| Evidência | Execução nova a guardar | Responsável |
|---|---|---|
| E1 | CI verde da main após integrar etapa 4 | Davi |
| E2 | CI vermelho nos testes de modelo do PR 5 | Kaique |
| E3 | CT aprovado no PR 4 | Davi |
| E4 | CT reprovado no portão, campeão preservado, no PR 5 | Kaique |
| E5 | CD verde da tag `v1.0.0` | Davi |

Preencham `EVIDENCIAS-PARA-O-GRUPO.md` e enviem os valores a Victor antes do último commit.
Guardem também o CI inicial e o CI da adaptação. A imagem nova será
`ghcr.io/thalescr77/projeto_mlops:1.0.0`, com digest e verificação anônima próprios.
Links de Actions precisam ser copiados das novas execuções; trocar apenas o dono/repo de
um link antigo não cria evidência.

## O que já foi conferido na preparação dos pacotes

Os arquivos de cada etapa foram conferidos por SHA-256. Os patches foram aplicados em
repositórios locais de validação, sem criar commits, comparando as seis árvores Git com
as etapas da base original. Isso verifica a montagem e a preservação dos arquivos.
Cada integrante ainda executará os testes locais e os novos runs do GitHub Actions.
O relatório `VALIDACAO-DOS-PACOTES.json` registra a conferência de montagem.
