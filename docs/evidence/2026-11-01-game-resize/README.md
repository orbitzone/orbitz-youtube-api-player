# Evidências: redimensionamento dos jogos no modo hide

Teste GTK/WebKit executado em 01/11/2026 com perfil temporário e vídeo sintético, sem acessar chave da API ou histórico do usuário.

Reprodução: executar `tests/gtk_game_resize.py` no runtime Flatpak, com `GAME_RESIZE_EVIDENCE` apontando para um diretório gravável para capturas.

O teste abre cada um dos seis jogos, oculta os controles, ativa Ctrl+T e solicita três redimensionamentos nativos: 620×380, 800×540 e 500×320. Confirma área preenchendo a janela, canvas desenhado, moldura acompanhando e pausa temporária. Depois encerra a edição, restaura os controles e retorna à home.

- `gtk-test.log`: resultado e medições dos 18 cenários.
- `results.json`: medições estruturadas dos cenários.
- `runner.png`, `maze.png`, `invaders.png`, `asteroids.png`, `breaker.png`, `lander.png`: capturas do WebKit no menor tamanho, durante a edição no modo hide.
- `final-home.png`: retorno à home ao final.
- `unit-tests.log`: resultado da suíte Python/JavaScript após a correção.

Limite: o teste redimensiona a janela GTK de verdade; não simula o gesto físico de arrastar com o mouse no gerenciador de janelas. Avisos de depreciação GTK/WebKit e ausência do módulo canberra são mantidos no log original.
