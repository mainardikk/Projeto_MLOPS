# Links para entrega no D2L

Copie os links abaixo para o envio único da equipe. E2 e E4 são falhas intencionais;
o PR correspondente está fechado sem merge e a main mantém o modelo aprovado.

```text
Repositório público:
https://github.com/mainardikk/Projeto_MLOPS

E1 — CI verde na main:
https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43355820648

E2 — CI vermelho por falha controlada no modelo:
https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43358312788

E3 — CT com drift e portão aprovado:
https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43355508124

E4 — CT reprovado no portão, campeão preservado:
https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43358312669

E5 — CD verde com a tag v1.0.0:
https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43356110304

Pacote público no GitHub Packages:
https://github.com/mainardikk/Projeto_MLOPS/pkgs/container/projeto_mlops

Verificação adicional — download sem autenticação e teste HTTP:
https://github.com/mainardikk/Projeto_MLOPS/actions/runs/43356673814
```

Relatório: [ADAPTACAO.md](ADAPTACAO.md), com [versão PDF de duas páginas](ADAPTACAO.pdf).
Imagem: `ghcr.io/mainardikk/projeto_mlops:1.0.0`.

O [PR #1](https://github.com/mainardikk/Projeto_MLOPS/pull/1) foi integrado por fast-forward;
o [PR #2](https://github.com/mainardikk/Projeto_MLOPS/pull/2) foi fechado sem merge.
São seis commits no total considerando a branch de falha, cinco na main e uma tag de versão.
A distribuição de responsabilidades entre os seis integrantes e a declaração de uso de IA
pelo grupo estão na seção 6 do relatório.
