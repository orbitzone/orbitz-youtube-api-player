# Preparação de beta

A fonte de versão é `VERSION`; os diagnósticos e o Flatpak instalado usam esse mesmo arquivo. As notas de cada versão ficam nesta pasta.

## Gerar pacote local

Requer Python 3, Node.js, make, Flatpak e GNOME Platform/SDK 49 instalados. Em uma sessão de desenvolvimento:

```sh
python3 scripts/prepare_beta.py --build-dir /tmp/orbitz-beta-build --repo /tmp/orbitz-beta-repo --output dist
```

O script executa `make test`, verifica a versão AppStream, prepara o diretório Flatpak, instala somente os arquivos definidos no Makefile, exporta o aplicativo e gera pacote, checksum, notas e inventário de hashes de fontes. Não inclui configurações pessoais nem publica, faz push ou cria tags.

## Validar antes de distribuir

```sh
cd dist
sha256sum -c SHA256SUMS
flatpak install --user ./orbitz-youtube-api-player-0.2.0-beta.1-x86_64.flatpak
flatpak run io.orbitz.YouTubeDesktop
```

Execute também os testes GTK/WebKit com perfis temporários: `gtk_games_home.py`, `gtk_three_rows.py`, `gtk_desktop_new_window.py`, `gtk_game_resize.py`, `gtk_maze.py` e `gtk_lander.py`. Eles exigem sessão gráfica, runtime e acesso ao diretório de fontes. Esses testes não substituem o roteiro manual das notas.

Antes da publicação: revisar o diff integral, confirmar os termos de marca/API para distribuição pública, executar o roteiro manual em outra máquina e anexar somente os artefatos necessários. O alto consumo de CPU e as demais limitações devem acompanhar a beta; não anunciar melhorias ainda não comprovadas.
