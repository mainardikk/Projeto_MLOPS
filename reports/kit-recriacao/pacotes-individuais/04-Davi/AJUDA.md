# Ajuda para esta entrega

## Conta, autoria e convite

Use sua própria conta no seu PC. Aceite o convite do Thales antes de publicar.
`git config user.name` e `user.email` definem a autoria do commit; não fazem login no GitHub.
O email precisa estar vinculado/verificado na sua conta para o GitHub associar o perfil.
No push, faça a autenticação solicitada pelo Git usando sua conta. Não compartilhe senhas ou tokens.
Se outra conta estiver salva no seu PC, confira a conta selecionada pelo Git Credential Manager.

## Um comando falhou

- Pare e compartilhe com o grupo a mensagem de erro, a etapa e a saída de `git status --short`.
- Patch falhou: confira se a etapa anterior terminou e se a main foi atualizada.
  Não use `--reject`, não reaplique parcialmente e não apague arquivos para tentar encaixar.
- Use `--whitespace=nowarn` como no tutorial. `--whitespace=fix` pode alterar dados UCI
  cujos hashes precisam ser preservados.
- Push rejeitado: confira a conta, o convite e se a main recebeu mudanças de outro colega.
  Não use `--force`. A execução em ordem evita conflitos.
- Nas etapas 1, 2, 3, 4 e 6, CI local reprovado impede a publicação. Na etapa 5, a reprovação
  de modelo/portão é esperada; falha de instalação/importação/DVC não é a evidência desejada.
- Se um commit já foi publicado e precisa de correção, pare e combine a solução com o grupo
  para não ultrapassar os seis commits nem reescrever trabalho de outra pessoa.

## Arquivos que ficam fora do novo repositório

Este tutorial, o manifesto e os ZIPs/patches ficam na pasta do pacote, fora do clone.
O tutorial usa caminhos separados para isso. `git apply --index` prepara as alterações,
e o `git commit` seguinte será seu. Não use `git am` ou cherry-pick com autoria antiga.
Ambiente `.venv`, candidato e relatórios gerados ficam ignorados; não force sua inclusão.

## Conferência opcional de integridade do pacote

Na pasta que contém este arquivo, execute:

```powershell
$manifesto = Get-Content -LiteralPath SHA256-ARQUIVOS.json -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($item in $manifesto.PSObject.Properties) {
    $hash = (Get-FileHash -LiteralPath $item.Name -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $item.Value) { throw "Arquivo alterado ou corrompido: $($item.Name)" }
    Write-Output "OK: $($item.Name)"
}
```
