# Desempenho de vídeo — 31/10/2026

## Gargalo identificado

O pacote instalado não concedia `--device=dri`. O log do aplicativo apresentava `amdgpu_get_auth failed`, `failed to create dri2 screen`, `failed to create dri3 screen` e `failed to load driver: radeonsi`. Uma leitura do consumo acumulado mostrava o WebKit em aproximadamente 261% de CPU. Essa leitura não é uma medição instantânea ou uma comparação controlada.

O host possui Radeon RX 460/560D (Baffin). Ao permitir DRI em um processo separado, o runtime acessou `/dev/dri` e registrou `vah264dec` e `vah265dec` de hardware. A consulta dos decodificadores VA de VP9 e AV1 não retornou fábricas disponíveis. Não foi identificado o codec do vídeo pessoal em reprodução.

A correção acrescenta somente `--device=dri` às permissões do pacote, conforme a [documentação do Flatpak](https://docs.flatpak.org/en/latest/sandbox-permissions.html). Não concede todos os dispositivos. O WebKitGTK 2.54.1 do runtime já usa aceleração por padrão; não há ganho em forçar a antiga política on-demand, conforme as [notas do WebKitGTK 2.54](https://www.webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html). A existência de um decoder de hardware não garante que todo vídeo o utilize: formato, driver e seleção do pipeline continuam relevantes; veja a [documentação do GStreamer](https://gstreamer.freedesktop.org/documentation/tutorials/playback/hardware-accelerated-video-decoding.html).

## Comparação controlada

`tests/gtk_video_performance.py` gera um vídeo local sintético H.264 1920×1080 a 30 fps, sem áudio, e o reproduz em loop no WebKit. Mede cinco segundos após aquecimento em cada dimensão, somando os ticks de CPU do processo de teste e seus descendentes vivos. 100% representa um núcleo ocupado. Os dois processos de benchmark foram executados sequencialmente, um sem DRI e outro com DRI. O aplicativo do usuário permaneceu aberto durante a comparação; nenhuma chave, histórico, consulta ou vídeo pessoal foi lido pelo harness.

| Área real da viewport | Sem acesso à GPU | Com acesso à GPU | Redução observada |
| --- | ---: | ---: | ---: |
| 640×360 | 97,0% CPU | 17,6% CPU | 81,9% |
| 1080×720 | 273,9% CPU | 19,4% CPU | 92,9% |

A segunda janela foi solicitada em 1280×720, mas limitada pelo ambiente a 1080×720 nas duas execuções. O elemento de vídeo permaneceu em reprodução, com readyState 4. O teste mede o caminho completo de renderização e reprodução, sem isolar os ganhos de composição e decodificação. São amostras curtas de um vídeo sintético, não uma garantia para vídeos do YouTube, codecs diferentes, 60 fps, 4K ou outros drivers. Não foram medidos quadros perdidos.

## Trabalho eliminado do aplicativo

- O observador de mouse continua consultando a posição nativa a cada 80 ms somente quando o modo automático está ligado, mas só envia JavaScript ao WebKit quando muda a amostra. Mouse parado e movimento fora da janela deixam de gerar 12,5 chamadas JavaScript por segundo. Novas épocas reenviam a amostra inicial; o frontend guarda a amostra recebida antes da confirmação HTTP para não perder a primeira posição.
- O runner oculto não mede layout, redimensiona buffers nem desenha o canvas. Dimensões e escala inalteradas também dispensam realocação/redesenho. Seu loop de animação já encerrava ao iniciar vídeo; não era um loop contínuo de jogo durante reprodução.
- A busca/recomendações são acionadas por ações de UI, não por um loop de reprodução. O retry de autoplay é limitado e interrompido quando o vídeo começa. Timers de restauração/ancoragem da janela são finitos. A gravação de geometria é agrupada e não acompanha os frames do vídeo.

Não foram desabilitados anúncios, scripts internos do player, isolamento do WebKit, segurança ou recursos de reprodução. Não foi reduzida à força a qualidade dos vídeos. Se o player escolher um codec sem decoder acelerado disponível, ou aumentar resolução/FPS numa janela maior, poderá continuar havendo CPU de decodificação significativa.

## Verificação

50 testes Python e 13 scripts JavaScript aprovados. Cobertura nova valida ausência de mensagens com mouse parado, agrupamento de posições fora da janela, reenvio em nova época, primeira amostra antes da confirmação HTTP e ausência de trabalho de canvas oculto. Sintaxe Python/JavaScript, paridade dos catálogos e `git diff --check` aprovados. Os logs completos dos benchmarks ficam em `/tmp/youtube-performance-without-gpu.log` e `/tmp/youtube-performance-with-gpu.log` nesta máquina.


## Segunda revisão — 31/10/2026

Confirmado que o pacote instalado mantém `devices=dri`. Foi realizada uma amostra de cinco segundos dos ticks de CPU por thread do aplicativo em reprodução, sem ler URL, título, conta ou conteúdo do vídeo. Apareceram três threads `vpx tile worker` somando aproximadamente 33% de um núcleo, além de threads do GStreamer, compositor e UI. Isso indica decodificação VPx por software durante essa amostra. O nome da thread não distingue sozinho VP8 de VP9. A inspeção anterior do runtime não disponibilizou decoders VA para VP9/AV1; a disponibilidade H.264 não implica aceleração para esses outros formatos. Não se presume que o mesmo pipeline seja usado por todos os vídeos.

Foi tentada amostragem de funções nativas com `perf`, mas o kernel bloqueia essa ferramenta para o usuário (`perf_event_paranoid=4`). Nenhuma configuração de segurança do sistema foi alterada. Portanto, esta revisão não atribui o custo interno da thread GTK a uma função específica.

Revisados: loop/resize/desenho do runner, integração do player e retry de autoplay, amostras/timers de controles automáticos, transições de geometria, listeners/i18n, HTTP local, buscas e caches, persistência, manifesto, launcher e CI. Não foi identificado outro loop contínuo próprio comparável à renderização/decodificação do player durante reprodução. A consulta nativa do mouse permanece em 80 ms somente no modo automático, preservando os prazos já validados. O runner continua sem trabalho de canvas durante vídeo. Consultas à API não são executadas periodicamente durante reprodução.

Melhorias adicionais aplicadas:

- A API JavaScript do iframe oficial é carregada somente na primeira seleção de vídeo; não é mais antecipada na tela inicial. O primeiro vídeo continua acionando o mesmo caminho de inicialização. Isso economiza trabalho/rede no início; não há estimativa de redução de CPU durante reprodução já iniciada.
- Geometria repetida mantém o timer de debounce já existente, sem removê-lo/recriá-lo. Geometria já persistida não agenda flush. Um teste com mil eventos idênticos preserva apenas o primeiro timer; após gravar, outros mil não criam nenhum. Mudanças reais e fechamento imediato continuam persistindo corretamente.

Verificação: 51 testes Python e 14 scripts JavaScript; sintaxe Python/JS, catálogos PT/EN, desktop/AppStream/schema e whitespace aprovados. Smoke GTK real de fechar/reabrir preservou x/y/largura/altura externos. Não se atribui uma nova redução percentual de CPU a essas mudanças menores. Os percentuais do benchmark acima pertencem à correção anterior de GPU.

O player incorporado não oferece mais controle funcional de qualidade via `setPlaybackQuality`, conforme o [histórico oficial da API](https://developers.google.com/youtube/iframe_api_reference). Não foi forçada seleção de codec, desabilitado decoder, reduzida qualidade nem alterada a taxa de quadros. Ganhos adicionais relevantes em vídeos pesados podem depender do formato entregue, resolução/FPS e capacidade de decodificação da GPU.
