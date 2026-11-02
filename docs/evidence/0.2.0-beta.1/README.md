# Validação da primeira beta — 0.2.0-beta.1

Preparação local em 02/11/2026. Pacote não publicado nem instalado sobre o perfil do usuário nesta etapa.

| Verificação | Resultado |
| --- | --- |
| Suíte Python/JavaScript | Aprovada; log em `unit-tests.log` |
| Versão única e notas presentes | `prepare_beta.py --check` aprovado |
| AppStream / desktop file | Validação aprovada |
| Build Flatpak novo | GNOME SDK/Platform 49, x86_64 |
| Módulos e versão no runtime do build | `0.2.0-beta.1`, imports aprovados |
| Integridade | Todos os itens de SHA256SUMS conferidos |
| Perfil novo / home | GTK/WebKit aprovado, `home.log` |
| Duas janelas / geometria recuperada | GTK/WebKit aprovado, `multiwindow.log` |
| Busca de dados pessoais no pacote | Nenhum banco de dados ou padrão de chave Google encontrado na árvore instalada |

Os testes usam dados sintéticos e perfis temporários; o prefixo do caminho de fontes foi normalizado para `<source>` nos logs. Não validam qualidade de rede, quotas reais nem reprodução de todos os vídeos. O roteiro manual em outra máquina e as limitações descritas nas notas permanecem relevantes.

## Artefatos locais

- `dist/orbitz-youtube-api-player-0.2.0-beta.1-x86_64.flatpak`
- `dist/SHA256SUMS`
- `dist/BUILDINFO.json` — hashes dos arquivos de fonte empacotáveis.
- `dist/RELEASE_NOTES.md`

O diretório dist é ignorado pelo Git. O checksum aqui registra o pacote gerado; reconstruções podem ter hash diferente por metadados/timestamps do Flatpak. O inventário de fontes identifica os inputs daquela construção.
