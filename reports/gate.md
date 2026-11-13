## Portão de qualidade: APROVADO: o candidato pode virar campeão

| Modelo | Recall spam | Precisão spam | Amostras |
|---|---|---|---|
| campeao | 0.864 | 0.935 | 1041 |
| candidato | 0.864 | 0.944 | 1041 |

| Regra | Resultado | Valor |
|---|---|---|
| recall spam do candidato >= 0.85 | passou | 0.8644 |
| precisão spam do candidato >= 0.93 | passou | 0.9444 |
| precisão spam do candidato >= precisão do campeão (mesmo conjunto) | passou | 0.9444 x 0.9346 |

SHA-256 do campeão avaliado: `2f7f3e47d5528179a850fe686ed92017fa748190ff8b0d86f6b0020aa95e64e9`
