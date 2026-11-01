# Origem e validação

Extração em 27/10/2026 de `orbitzone/orbitz-widgets-for-gnome`, commit de origem `a0bcb0302405d176aa3be5118a5b211caf90d1fd`. Foram copiados apenas os fontes próprios do app YouTube, ícone, traduções YouTube e testes dirigidos. Nenhuma chave real, configuração de usuário, credencial ou arquivo pessoal foi copiado.

A versão independente usa aplicação/schema/i18n próprios, API key e cache em `orbitz-youtube-wrapper`, caminho web local dentro de `app/` e launcher Flatpak sem o GNOME Shell. O app registra o esquema GSettings próprio. O runtime GNOME 49 fornece WebKitGTK 4.1; o código extraído foi atualizado da API introspectiva WebKit2 4.0 para 4.1, requerendo confirmação por CI.

Escopo: Linux x86_64/Flatpak/X11 ou XWayland; sem Windows/macOS, Flathub, importação automática de configurações/chave ou instalação da versão ativa do Orbitz. Não garante remoção de anúncios: Data API retorna resultados/IDs; player incorporado é servido pelo YouTube. Evidências de testes e build serão acrescentadas após execução no CI. Visual real, portais e reprodução com conta/quota própria não serão inferidos do build.

## Validação local pré-publicação (27/10/2026)

19 testes Python e quatro testes JavaScript passaram; `py_compile`, `desktop-file-validate`, `appstreamcli validate --no-net`, parse do manifesto Flatpak e `git diff --check` passaram. Esses testes usam dados sintéticos e não consultam YouTube/Google. O primeiro build Flatpak apontou que o SVG não era quadrado; o desenho foi centralizado numa tela 36×36. O [CI final 40608208765](https://github.com/orbitzone/orbitz-youtube-wrapper/actions/runs/40608208765) passou após a autenticação por token dos bridges, validou importação de WebKitGTK 4.1 e gerou o bundle x86_64. SHA-256 de `orbitz-youtube-desktop-x86_64.flatpak`: `917e785eeea8ea0a1b2dc02447b19c715ab8128702f4977888cbe01668b29de1`; a cópia publicada foi baixada e conferida com `SHA256SUMS`. O nome do arquivo corresponde à release v0.1.0 anterior ao rename. Execução gráfica em distribuições distintas e reprodução com chave/conta reais dependem de validação manual posterior.

## Renomeação do projeto (28/10/2026)

O repositório foi renomeado para `orbitzone/orbitz-youtube-wrapper` e a cópia local para `orbitz-youtube-wrapper`. O commit `6787a73` renomeia comando/entry point e atualiza as referências de build; preserva o ID Flatpak/GSettings `io.orbitz.YouTubeDesktop`. 21 testes Python, quatro scripts JavaScript, validadores desktop/AppStream/schema e instalação em stage passaram. O [CI 40642246818](https://github.com/orbitzone/orbitz-youtube-wrapper/actions/runs/40642246818) concluiu com sucesso e gerou `orbitz-youtube-wrapper-x86_64.flatpak` (SHA-256 `b39484a6fc57df8f652fa67a4a99712f2f726dd5aa04861e4cd53a532e0e8b9f`), instalado no escopo do usuário. A chave/cache continuam legíveis pelos caminhos legados; novas gravações usam o slug atual. O asset da release v0.1.0 conserva seu nome original.

## Mini game (28/10/2026)

O foco do canvas não desenha mais um contorno branco. Há apenas um OVNI ativo: a primeira nave chega após três segundos, cruza a tela em três fases de um segundo, dispara após dois segundos contra o cacto à frente mais próximo e sai ao completar o terceiro segundo. Depois de sair, aguarda cinco segundos antes de iniciar o próximo ciclo. O recorde é carregado e atualizado pelo endpoint local autenticado, em arquivo separado com escrita atômica e permissão privada. Na tela de Game Over, uma nova pontuação máxima recebe destaque dourado e anúncio acessível, com texto em português ou inglês conforme o idioma escolhido; empates não contam como novo recorde. O campo gramado recebe cactos e pedras no solo e pernilongos em trajetória reta aérea; a colisão e os tiros usam a altura real de cada obstáculo. A nave mantém a orientação horizontal com inclinação sutil. O desenho é pré-renderizado numa tela auxiliar e o loop limita a renderização a 60 quadros por segundo. A validação local inclui 24 testes Python e seis JavaScript via `make test`, cobrindo fases, persistência crescente do recorde, terrenos, colisão aérea, orientação e alvo. A validação gráfica em sessão real depende da instalação/build atualizado.

## Revisão geral e correções (28/10/2026)

A revisão no commit `cb35043` encontrou duas falhas reproduzíveis: uma resposta de recomendações podia pintar em outra aba após a troca de filtro; um JSON válido que não fosse objeto podia interromper a leitura da chave e impedir o fallback legado. A implementação agora invalida respostas antigas em todas as mudanças de aba, verifica novamente a aba e o termo antes de renderizar recomendações, e trata formatos inválidos como chave ausente para continuar a leitura do próximo arquivo. Cobertura inclui resposta assíncrona atrasada e JSON array/null/string com fallback legado.

A ponte JavaScript nativa do WebKit foi substituída por ações no servidor HTTP local autenticado por token imprevisível no caminho e validação exata do cabeçalho Origin. O corpo é limitado a 4096 bytes e precisa ser objeto JSON antes de despachar estado de janela, abertura de link ou cópia; os links externos e de clipboard continuam sujeitos a allowlist/formato. Operações GTK são encaminhadas para a thread principal. Trocas rápidas de filtro agora agrupam a busca por 180 ms, e a interface aborta fetches substituídos; uma solicitação de API já iniciada no servidor pode, porém, terminar seu timeout/requisição mesmo depois do cancelamento do navegador.

Verificação após as correções: `make test` executa 27 testes Python e oito scripts JavaScript, todos aprovados; `py_compile`, parse do manifesto Flatpak, `node --check` nos scripts e `git diff --check` também aprovados. A revisão independente confirmou que a troca para Comentários reabilita Buscar e não encontrou outro bloqueador na fronteira HTTP ou no despacho GTK. Uma ação enfileirada na thread GTK pode acontecer depois de o cliente receber timeout de cinco segundos se a interface estiver bloqueada. Reprodução em sessão gráfica, testes com YouTube real, medição de performance/FPS e build/execução do bundle ainda precisam de evidência separada. Esta mudança não instala nem publica uma nova versão; a release v0.1.0 continua antiga.


## Ocultação de controles e menu da engrenagem (30/10/2026)

A engrenagem abre um dropdown com Configurações e a preferência Ocultar controles ao sair com o mouse (Settings / Hide controls on mouseleave em inglês). A preferência inicia habilitada e fica em `orbitz-youtube-wrapper/controls.json` no diretório XDG de configuração, separada da chave e do recorde, com escrita atômica e permissão 0600.

Com vídeo selecionado e menus fechados, a saída real da janela GTK oculta cabeçalho e rodapé e remove a decoração nativa; o retorno restaura todos. O iframe permanece o mesmo: a aplicação não pausa, recria nem modifica os controles internos do YouTube. O player ocupa a área disponível; o tamanho da janela e as proporções internas continuam sujeitos ao GTK/gerenciador de janelas e ao YouTube. Durante menus/configurações/busca, a interface continua disponível; teclado também permite recuperar os controles. A presença do ponteiro é observada no GTK, evitando tratar a entrada no iframe como saída do app. Há uma verificação temporária de 120 ms apenas sobre a decoração do gerenciador de janelas, removida ao sair/voltar ao cliente ou ao ocultar/destruir a janela.

A ação de controles usa a fronteira HTTP local existente com token/Origin e limite de corpo, valida flag booleana e sequência inteira; solicitações atrasadas não podem sobrescrever um estado mais recente. A preferência usa o mesmo limite/autenticação e não escreve nos arquivos da chave ou do jogo.

Validação local: `make test` aprovou 35 testes Python e nove scripts Node; casos novos cobrem preferência persistente/erros/arquivos privados, fronteira HTTP, sequência de decoração, cruzamentos entre filhos/player, barra de título, menu/teclado, recuperação de falha e manutenção do iframe. `py_compile`, `node --check` do script completo e comparação de IDs/placeholders PT/EN aprovados. Sem chave, consulta à API, dados pessoais, instalação, build/publicação ou teste gráfico GTK/YouTube real. O bundle instalado precisa ser reconstruído/atualizado separadamente para carregar a mudança.


### Aplicação local após pedido do usuário (30/10/2026)

O Flatpak foi gerado localmente a partir das fontes testadas, mantendo as permissões já existentes (X11, áudio, rede e IPC), e instalado no escopo do usuário com `flatpak install --user --reinstall --assumeyes --noninteractive /tmp/orbitz-youtube-controls-20261030.flatpak`. Commit instalado: `8e68c100703fa2e1ed0cc44b3c4f2abba46be9d73f1f44fa953c24889c8c6f40`. SHA-256 do bundle: `dc6e838f808fd97ef58ec9b9cdaa8bcf6f2df964b4e5b81ef49a14232f0e6a66`. O código e os catálogos no deployment foram comparados byte a byte às fontes validadas. O aplicativo foi aberto e sua instância nova foi confirmada em `flatpak ps`; Sticky Notes permaneceu em execução. Nenhum arquivo pessoal de configuração/chave foi lido ou regravado por essa operação. Validação visual de menu, bordas e reprodução continua separada da confirmação de instalação/processo; não houve publicação.


## Controles somente por Ctrl+H (30/10/2026)

Por atualização do requisito, Ctrl+H passa a ser a única ação para alternar o modo só vídeo. Entrar/sair com o mouse e pressionar outras teclas não mudam os controles. A captura GTK ocorre antes do WebKit para funcionar com foco no iframe do player; key release/focus out reiniciam o controle de repetição, evitando alternância contínua ao manter as teclas pressionadas. F11 e Escape em fullscreen mantêm os handlers existentes.

A engrenagem continua abrindo Configurações e apresenta o atalho como informação. A antiga opção automática, os observadores de ponteiro e o endpoint de preferência foram removidos. Arquivos de preferência antigos eventualmente existentes no perfil são preservados e ignorados; chave, idioma e recorde continuam intactos. A janela inicia com os controles visíveis a cada abertura. Settings aberto impede ocultação para preservar sua interação; sem vídeo o atalho não faz nada.

Validação desta revisão: 33 testes Python e nove scripts Node passaram com `make test`. Regressões cobrem alternância Ctrl+H, Caps Lock, rejeição de outros modificadores, repetição de tecla, key release/focus out, ausência de sinais/timers de ponteiro, preservação de F11/Escape, configurações abertas, iframe preservado, falhas e ordem das ações nativas. Os testes do antigo armazenamento automático foram substituídos pela verificação de que seu endpoint foi removido. `py_compile`, `node --check` e paridade dos catálogos PT/EN aprovados. Sem validação gráfica do atalho em WebKitGTK real nesta etapa.

Aplicação local: instalado o bundle `/tmp/orbitz-youtube-shortcut-20261030.flatpak` no escopo do usuário, commit `2a3bedf5456d6e336a6a0d0c201bd47ea7a34fdba70ed53ac44da2dea984d19c`, SHA-256 `340dc1537689d260e028cb45a8119287040601dddfc3a2fe9d965502ab4d943a`. Fontes e catálogos do deployment conferidos byte a byte; módulo automático antigo ausente. O YouTube foi reaberto, sem modificar chave/idioma/recorde nem remover preferências antigas do perfil. Confirmação de processo instalado/aberto não substitui teste visual do atalho em sessão GTK. Sem publicação.


## Ctrl+H preserva o tamanho do vídeo (30/10/2026)

A revisão anterior expandia o player à altura inteira da janela ao esconder as barras. Agora o frontend captura o retângulo do vídeo antes da alternância e fixa sua largura/altura durante a transição, sem substituir o iframe. Em janela normal, o GTK salva tamanho/posição, retira apenas a área externa ao vídeo e restaura o tamanho/posição ao mostrar as barras. Conversão entre pixels CSS e coordenadas nativas considera a escala da viewport. O tamanho fixo é liberado somente depois que a viewport normal é restaurada; o dimensionamento automático não interfere durante a transição. Tela cheia/maximizado respeitam o estado imposto pelo gerenciador de janelas e não são desfeitos automaticamente.

Validação: `make test` aprovou 35 testes Python e nove scripts Node. Os testes novos verificam as dimensões capturadas, restauração após resize nativo, posição/tamanho da janela, escala de coordenadas e rejeição de retângulos inválidos. Um smoke GTK3/WebKitGTK 4.1 real, dentro do runtime instalado e com iframe sintético sem rede, mediu 524×230 px em janela 524×340 e 980×540 px em janela 980×650; em ambos os casos, antes/oculto/restaurado mantiveram exatamente a mesma largura e altura do vídeo. A janela nativa passou respectivamente a 524×230 e 980×540 enquanto oculta e voltou ao tamanho original. Harness reutilizável: `python3 tests/gtk_video_geometry.py [largura altura]`, requer sessão GTK e WebKitGTK 4.1. Não houve reprodução YouTube real nem acesso à chave/configuração pessoal nesse teste.

Aplicação local da correção de tamanho: bundle `/tmp/orbitz-youtube-fixed-video-20261030.flatpak` instalado para o usuário, commit `a24e86f7b878b35f7a5f8ea978fa75bae5a54fa569e424e0fa086d6b85b4e8ca`, SHA-256 `7adb44aa5f31000b7d4ecd2ef807beccabe34ef1c3bf726380699784e60f7977`. Código HTML/Python instalado comparado às fontes testadas; aplicativo reaberto. Chave, idioma e recorde não foram alterados. O smoke gráfico foi sintético; não reproduziu mídia real do YouTube. Sem publicação.


## Posição e tamanho persistentes da janela (30/10/2026)

A geometria fica em `orbitz-youtube-wrapper/window.json` no diretório XDG de configuração: limites externos da janela (incluindo decoração do gerenciador de janelas), posição e estado maximizado. Gravação privada 0600, temporário exclusivo e substituição atômica, sem usar ou alterar o arquivo da chave/recorde. Eventos de movimento/redimensionamento são agrupados por 250 ms; fechar a janela grava imediatamente a última geometria.

Com geometria salva, o app não centraliza a janela nem substitui o tamanho pelo ajuste automático de altura dos estados player/pesquisa/Settings. Ao mapear, mede a decoração do tema atual para restaurar os mesmos limites externos, sem assumir uma altura fixa para a barra de título. Posições negativas em outros monitores são válidas; somente uma janela totalmente fora das áreas conectadas é reposicionada para uma área visível. O estado maximizado é restaurado a partir da geometria normal; fullscreen temporário não substitui a preferência normal. Fechar no modo Ctrl+H salva os limites externos efetivamente presentes, e a próxima abertura apresenta a interface inicial dentro desses limites.

Teste real no runtime GTK3/XWayland: duas janelas sintéticas, arquivo temporário e nenhum acesso à chave/configuração pessoal; mover/redimensionar a primeira, gravar/fechar e abrir a segunda restaurou exatamente x, y, largura e altura externos (incluindo a decoração do tema). Harness reutilizável: `python3 tests/gtk_window_restore.py`. Os testes unitários cobrem persistência privada/atômica, arquivo inválido/link simbólico, erro de substituição, monitores com coordenadas negativas, monitor removido, decoração, eventos agrupados/fechamento imediato, maximizado/fullscreen e limpeza de timers.

`make test` nesta revisão: 44 testes Python e nove scripts JavaScript aprovados; `py_compile` aprovado. Posição/tamanho do app atual foram consultados somente por metadados XWayland para inicializar a primeira preferência durante a atualização local, sem ler mídia, chave ou consultas.

Aplicação local: instalado o bundle `/tmp/orbitz-youtube-window-position-20261030.flatpak`, commit `fb3a92e687ced16d492ae806cc1f9e946ada0ea51b868939cf7cb213525f406f`, SHA-256 `c7b6377fa2abbfbc1e7ba896d13c6de2348820719a00fb7bf0b30a10f570f65a`. Fontes instaladas comparadas às testadas. Inicializada a preferência privada de geometria com os limites da janela existente; após reabrir o app atualizado, x, y, largura, altura e estado maximizado foram comparados aos valores anteriores e coincidiram exatamente. A comparação usou somente metadados da janela XWayland, sem armazenar coordenadas pessoais no repositório ou acessar mídia/chave. A instância atualizada permaneceu aberta, Sticky Notes não foi controlado, e não houve publicação.


## Ctrl+H também na tela inicial e no Game Over (30/10/2026)

O atalho agora usa a área central ativa: jogo/runner na tela inicial ou Game Over, ou vídeo durante a reprodução. Oculta/restaura as barras e mantém largura/altura da área central; o runner perde apenas as margens externas enquanto oculto. Não reinicia o jogo nem zera pontuação/recorde. Settings aberto continua protegido contra ocultação. O handler nativo passa a aceitar geometria do estado idle além do player; mantém validações de tipo, limites e sequência.

Validação desta revisão: 44 testes Python e nove scripts Node passaram. O teste de UI cobre o Game Over sem vídeo selecionado, preserva o objeto de estado/pontuação do jogo e confirma alternância, dimensões e restauração. Smoke real GTK/WebKit sintético: runner 496×254 px antes/oculto/restaurado, com janela 524×340 reduzida a 496×254 e restaurada; vídeo 524×230 px nos três estados como regressão. O harness aceita `--runner`. Sem acesso à chave, API ou dados pessoais nesses testes.

Instalado localmente o bundle `/tmp/orbitz-youtube-runner-controls-20261030.flatpak`, commit `e02943dda522144a408470c7c6e73e57942857998411b04671630bce947ca670`, SHA-256 `604ca4d736e2e581d4042e3b542e70a9d45d408f4c56748956ca938d9f6dc32e`; código instalado conferido e app reaberto. Chave, idioma, recorde e geometria persistida foram preservados. Sem publicação.


## Filtros responsivos e remoção dos comentários (30/10/2026)

Restam quatro filtros: Vídeos, Shorts, Ao vivo e Podcasts. Até 640 px de largura, o rail tem 44 px e exibe só os SVGs de 24 px; nomes continuam em aria-label e tooltip, com estado selecionado e navegação por setas/Home/End. Em janelas maiores, os rótulos acompanham os ícones. O rail tem rolagem vertical quando a altura for insuficiente, evitando opções fora do dropdown.

O painel/filtro de comentários, handlers, chamadas, consulta backend e endpoint de comentários foram removidos. Abas inválidas são ignoradas. As expectativas dos testes de cancelamento e teclado foram adaptadas aos quatro filtros, sem desabilitar a verificação de requisições obsoletas/canceladas. Ícones Material Symbols oficiais Google (Vídeos, transmissão e podcast) e marca Shorts distribuída por Simple Icons, com licenças/créditos instalados no pacote; não depende de fonte/CDN externa.

Validação: `make test` aprovou 44 testes Python e dez scripts Node; `py_compile`, `node --check` e paridade PT/EN de IDs/placeholders aprovados. Smoke GTK/WebKit real com conteúdo sintético mediu o rail de 44 px e rótulos ocultos em 568×320 e 360×280, e rail de 112 px com rótulos em 980×500. Quatro ícones de 24 px, nomes/tooltips localizados e rail contido no painel nas três geometrias. O novo harness é `tests/gtk_filters_layout.py`; sem API/chave/reprodução real nesses testes.

Aplicação local: pacote final `/tmp/orbitz-youtube-filters-final-20261030.flatpak`, commit `c002bef47016f28c79c1050a00799ebc80dd9debd27583b2a5323778ca54e2d4`, SHA-256 `9645c0bfbbb1a879229227d7b6f4d10d5094543710e4753fef82dbcfeea75a34`. Código, catálogos e licenças instalados conferidos; app reaberto, sem modificar chave/idioma/recorde/geometria do perfil. `git diff --check` limpo após normalizar apenas a nova linha final do módulo de API. Sem publicação.


## Menu e estabilidade visual (30/10/2026)

O menu da engrenagem oferece “Sempre acima das outras janelas”, com estado marcado, navegação por teclado e traduções PT/EN. A opção vale para a sessão atual e passa pela fronteira HTTP autenticada, com validação booleana e despacho GTK para `set_keep_above`.

Copiar link fica disponível desde a seleção do vídeo, inclusive em pausa, buffering, término ou erro; seu espaço no cabeçalho é reservado desde a abertura. O rodapé mantém a dica alinhada à direita quando o link externo muda de visibilidade. Respostas antigas de ações de controles são ignoradas pelo frontend.

Ctrl+H usa gravidade STATIC e coordenadas da área cliente para compensar a decoração assíncrona do gerenciador de janelas. Mantém o mesmo iframe. Em maximizado/fullscreen, a área central fica fixa nas coordenadas originais da viewport e a decoração nativa não é alterada ao ocultar os controles.

Validação: 46 testes Python e 11 scripts Node; o novo teste de estabilidade simula estados sucessivos do player. Smoke GTK/WebKit real com conteúdo sintético confirmou igualdade de x/y/largura/altura antes, oculto e restaurado em vídeo 524×230 e 980×540, além do runner 496×252. O harness `tests/gtk_video_geometry.py` agora verifica coordenadas na tela, além do tamanho. Sem API/chave/reprodução YouTube real, instalação ou publicação nesta revisão.


Aplicação local autorizada: gerado e instalado no escopo do usuário o bundle `/tmp/orbitz-youtube-stability-20261030.flatpak`, commit Flatpak `f2b82ee0fe99b25d420ce613c60630a55417b50224bceb3d8d6b1759d137611f`, SHA-256 `c5c0c1ad95f9d9ac23c030a7ef2798f840c9081dd92c769c426b2db5901aa4ab`. Os dez arquivos Python/HTML/catálogos instalados foram comparados byte a byte às fontes testadas. Aplicativo reaberto após a instalação. Nenhuma chave, idioma, recorde ou geometria do perfil foi editada pelo procedimento de atualização. Sem publicação.


## Controles automáticos com prazos canceláveis

Incluída a opção de sessão “Ocultar controles automaticamente” / “Auto hide controls” no menu da engrenagem. Enquanto ativa, Ctrl+H é consumido sem alternar e a indicação do atalho fica desabilitada. O usuário sai da área central (vídeo/runner) ou da janela: aguarda 2000 ms. Retorna à área central: aguarda 500 ms. Cada mudança de região cancela o prazo anterior; amostras repetidas na mesma região não adiam o prazo. Menus, busca e configurações bloqueiam ocultação e cancelam timers; ao fechar, começa um prazo novo.

`window_pointer.py` observa a posição nativa em intervalos de 80 ms somente durante o modo automático, inclusive sobre o iframe de outra origem, e envia coordenadas normalizadas para a viewport. Épocas crescentes rejeitam reconfigurações/amostras antigas. Desativação, reload e destruição removem o observador; os timers do frontend usam geração para rejeitar callbacks já enfileirados. O modo automático usa a mesma transição sequenciada/ancorada do Ctrl+H, preservando iframe e dimensões. A fronteira HTTP mantém token, Origin, limite de corpo e validação de tipos; operações GTK continuam na thread principal, com remoção de ações ainda enfileiradas em caso de timeout.

Validação: 49 testes Python e 12 scripts JavaScript, incluindo relógio controlado para 1999/2000 ms, 499/500 ms, retorno antes da ocultação, saída antes da revelação, reinício do prazo, modal, desativação, falha, callbacks obsoletos e Ctrl+H. Testes nativos cobrem coordenadas, minimização, épocas, validação, reload e limpeza. Smoke GTK/WebKit real com iframe sintético e `--auto` confirmou x/y/largura/altura idênticos antes/oculto/restaurado. Sem chave/API/reprodução YouTube real nesses testes.

Aplicação local (31/10/2026): instalado `/tmp/orbitz-youtube-auto-delay.flatpak`, commit `cf9d6abb0dfd51e4c7edfa52cd71740cd0cd18a5f9bf47b70e2d963845fd59ba`, SHA-256 `cc470276670bc7a5db1c9929056e2662031b2cdfa1868f9a302e7a98faee655c`. Onze arquivos instalados conferidos byte a byte com as fontes testadas. App reaberto; configurações pessoais não foram editadas pelo procedimento. Sem publicação.


## Correção de desempenho de vídeo (31/10/2026)

Identificada ausência de acesso DRI no pacote, com falhas de inicialização amdgpu/EGL/GLX no log. Acrescentado `--device=dri` ao manifesto. Eliminadas chamadas repetidas ao WebKit quando o mouse não muda e trabalho do canvas oculto. 50 testes Python e 13 scripts JavaScript aprovados. Benchmark sintético H.264 1080p/30: CPU 97,0%→17,6% em viewport 640×360 e 273,9%→19,4% em 1080×720. Evidências, método e limites em [desempenho](performance.md). Esses percentuais não são promessa de redução para vídeos reais do YouTube.

Aplicação local: instalado o bundle `/tmp/orbitz-youtube-performance.flatpak`, commit `4ce8dfaa709459321f21479052e722347658b4d1334424497782dca368cb7bd7`, SHA-256 `419339a19f69c0d9dca9b28680d4949a15bf0c8ab4f25760c589ea8babeaaad9`. Os onze arquivos de código/catálogos foram conferidos byte a byte; metadata instalada confirma `devices=dri`. App reaberto; nenhuma configuração pessoal foi editada pelo procedimento. Sem publicação.


## Segunda revisão de desempenho (31/10/2026)

51 testes Python e 14 scripts JavaScript aprovados; validação sintática, paridade PT/EN, desktop/AppStream/schema e whitespace aprovados. Reduzidos timers redundantes de geometria e carregamento antecipado do iframe API na tela inicial. Smoke GTK de fechar/reabrir preserva os limites externos. Medição de threads detectou trabalho VPx de decodificação durante a reprodução atual; não foi identificado outro ganho equivalente à correção de DRI. Método e limites em [desempenho](performance.md). Sem nova promessa percentual de economia.

Aplicação local da segunda revisão: bundle `/tmp/orbitz-youtube-performance-review2.flatpak`, commit `ca9f60adb244e5ac42b585ab6b5657435342809824129b66006dfc63c26fa0c9`, SHA-256 `ea874f9315f205a6bc07f3eb9b0fea68cc616b546d5e212206dd0f9325a5b7ba`. Onze arquivos instalados comparados às fontes testadas; aplicativo reaberto. Mantido acesso DRI. Nenhuma configuração pessoal editada pelo procedimento; sem publicação.


## Biblioteca e recursos de uso diário (31/10/2026)

Implementadas as seis recomendações: persistência de Sempre acima/Auto hide com delays ajustáveis; oferta de continuar o último vídeo; Favoritos/Assistir depois e transferência JSON; fila ordenável e avanço ao término; atalhos nativos e integração MPRIS; diagnóstico sob demanda.

Armazenamento transacional SQLite, arquivo privado 0600 com recusa de symlink, listas limitadas a 1000 itens cada e fila a 200. Importação valida todas as entradas antes de mesclar, com rollback transacional e limite de arquivo de 4 MiB. Exportação exclui chave, preferências, progresso e fila. O seletor nativo/portal autoriza somente os arquivos escolhidos; nenhuma permissão geral de arquivos foi acrescentada. A nova permissão D-Bus restringe-se ao nome MPRIS próprio.

Progresso utiliza um único timer de 15 s somente durante reprodução, captura identidade antes de trocar de vídeo e agrupa gravações pendentes. Pausa/troca/fechamento geram salvamento; encerramento abrupto pode perder até o intervalo desde a última gravação. A abertura oferece retomada sem autoplay. Eventos atrasados de um vídeo anterior não consomem a fila do novo vídeo. Consultas de diagnóstico e registro de mídia são acionados por eventos; não existe monitor contínuo de CPU/GPU.

Testes unitários/contratos abrangem concorrência SQLite, importação inválida/oversized/cancelada, exportação via arquivo de portal, ordenação/consumo da fila, persistência, números não finitos, MPRIS/atalhos e regressões dos controles. Testes GTK/WebKit com perfil temporário validaram biblioteca, botões de fila sem interromper seleção, retomada, delays, tradução PT/EN, diagnóstico e modal contido em 980×650 e 360×340. Um smoke do aplicativo completo validou restauração nativa das opções e gravação de progresso ao fechar. O smoke MPRIS usou D-Bus real com nome temporário e confirmou descoberta, propriedades, PlayPause e SetPosition. Não houve reprodução de YouTube real nem leitura da chave/conta nos testes.

Verificação final deste conjunto: 68 testes Python e 15 scripts JavaScript aprovados; sintaxe de todos os módulos e scripts, paridade PT/EN, desktop/AppStream/schema e whitespace aprovados. Captura visual sintética revisada em 360×340, com biblioteca rolável contida na janela. A retomada por MPRIS mantém um próximo vídeo pausado por cue, sem iniciar autoplay; eventos de término duplicados não consomem dois itens.

Aplicação local do conjunto: instalado `/tmp/orbitz-youtube-library-final.flatpak`, commit `9934fc63a1c1246a4f0c27cae69514bf24857cf794903d680d97aeb67b118eb5`, SHA-256 `dbb5444c0ed7959a4e8deddbd18f8e9bd9778d824492e270ca18f86174b37816`. Os quinze arquivos de código/catálogos instalados foram comparados byte a byte às fontes testadas. Mantida a permissão DRI e confirmado o nome D-Bus MPRIS restrito. Aplicativo reaberto; chave/idioma/recorde não foram editados pelo procedimento de atualização. Sem publicação.


## Correção de oscilações após selecionar vídeo (31/10/2026)

O link externo dependia de estados transitórios do player (buffering, ended, metadados antigos). Agora depende apenas da seleção ativa e permanece disponível inclusive em carregamento, pausa, término, bloqueio de autoplay ou erro; o href sempre corresponde ao vídeo selecionado. O rodapé reserva o espaço do link antes da primeira seleção, evitando mudança de altura/alinhamento.

Ao tocar um vídeo pela biblioteca/fila, o fechamento do modal não restaura foco na busca anterior. Isso evita reabrir o painel de pesquisa ao selecionar ou avançar. Fechar explicitamente o modal continua restaurando foco. Fechamentos de menus/painéis já fechados são no-ops, e modais são marcados abertos antes de fechar o menu, evitando transações intermediárias dos controles. Links colados fecham a descoberta antes de reproduzir.

O modo automático não reinterpreta uma amostra antiga do mouse após a alteração de layout causada por ocultar/restaurar barras. A classificação vem das novas amostras nativas; uma troca real de conteúdo pode atualizar a região uma vez enquanto a geometria está visível/estável. Assim, o próprio esconder das barras não simula reentrada do ponteiro nem agenda uma revelação indevida.

Verificação: 68 testes Python e 16 scripts JavaScript aprovados. Regressões incluem sequência de buffering/reprodução/pausa/término/erro, metadados antigos, foco anterior na busca, encerramentos redundantes, mudança artificial do retângulo durante a ocultação e troca real de conteúdo. Smoke GTK/WebKit com perfil temporário confirmou que selecionar vídeo com busca anteriormente focada não reabre a descoberta. Testes usam player/dados sintéticos, sem chave, conta ou reprodução YouTube real.

Aplicação local: instalado `/tmp/orbitz-youtube-flicker.flatpak`, commit `2d64ad1f6081619556e34da479d63b209292fd49921f4acc1c9c2bea41b1d68d`, SHA-256 `0503f6210959457324bcbe9f8b6845ab369bbace9fe44451b00d9a98461fb20d`. Quinze arquivos instalados comparados às fontes testadas. A instância anterior recebeu Quit via MPRIS para fechar normalmente e preservar o progresso, e o aplicativo foi reaberto. Chave, idioma, recorde e biblioteca não foram editados pelo procedimento de instalação. Sem publicação.


## Último vídeo sempre disponível (31/10/2026)

Atualizado o requisito: guardar e oferecer o último vídeo independentemente de pausa, duração curta, stop, conclusão ou transmissão ao vivo. Removidos o descarte antes de cinco segundos e a eliminação do registro perto do fim. A seleção já grava o identificador e título antes de o player ficar pronto; não depende do primeiro checkpoint de 15 s. Retomada válida mantém o ponto; stop/término, lives e duração desconhecida ou de transmissão longa ficam com posição inicial zero, sem apagar o identificador. O limite numérico aceito para mídia foi ampliado, mantendo validação de tipo e valores finitos, para aceitar os contadores grandes de rádios/lives.

O fechamento nativo preserva o último registro e ignora os metadados antigos de outro vídeo quando uma seleção nova ainda está carregando. Stop via MPRIS atualiza imediatamente o estado nativo e a gravação de progresso. Abrir e fechar sem reproduzir nada não remove a oferta. Agora não é apenas uma dispensa em memória naquela abertura; a seleção armazenada permanece para a próxima. O modo automático não oculta a oferta de retorno.

Verificação: 73 testes Python e 16 scripts JavaScript aprovados. Novos casos cobrem seleção antes de ready, vídeo curto/pausado/tocando/stop/ended, rádio com duração de 1,7 bilhão de segundos, duração desconhecida, reabertura sem playback e proteção contra metadados da seleção anterior. Smoke GTK/WebKit com perfil temporário confirma oferta inicial, proteção do auto hide e persistência após Agora não. Sem reprodução de YouTube real nem acesso à chave/conta nos testes. Registros já apagados pela regra antiga não podem ser reconstruídos automaticamente: uma nova seleção passa a registrá-los sob a regra atual.

Aplicação local: instalado `/tmp/orbitz-youtube-always-resume.flatpak`, commit `edeaa095fa8bb2cdba96a45339000e6486c76354d7ba29b9f77e1c323c8b9be0`, SHA-256 `4d97f87db8276778ebef73f58e74cc852bd462ffe5710f87d48cecab51233dc4`. Quinze arquivos instalados comparados às fontes testadas. Instância anterior fechada via Quit e aplicativo reaberto. Chave, idioma, recorde e biblioteca não foram editados pelo procedimento de instalação; sem publicação.


## Biblioteca compacta e menus contextuais (31/10/2026)

A biblioteca deixou de ser um modal largo centralizado com fundo escurecido. Agora abre como painel ancorado ao botão de livros no cabeçalho, à direita, com largura de até 460 px e adaptação à altura/largura disponíveis. Vídeo atual compacto, estrela com estado salvo, menu de três pontos, abas com contadores e itens com miniaturas/títulos de duas linhas. Miniaturas têm dimensões fixas, carregamento lazy e decode assíncrono; ícones são SVGs locais, sem fontes/CDNs adicionais.

Ações de lista foram agrupadas em menus ⋮; importação/exportação em Gerenciar. Os menus ficam contidos na viewport, suportam setas/Home/End, Tab e Escape; Escape fecha primeiro o menu e depois o painel. Favoritar/desfavoritar conserva foco após reconstruir a lista. Estados vazios têm orientação localizada. Não foram alterados o player/iframe, a persistência, o andamento da fila nem as permissões do pacote. Não foram adicionados loops de animação, monitoramento contínuo ou blur sobre o vídeo; a entrada usa animação curta respeitando movimento reduzido.

Validação: 73 testes Python e 16 scripts JavaScript aprovados. Smoke GTK/WebKit com dados e miniaturas sintéticos confirmou layout em 980×650 e 360×340, estrela com toggle, foco preservado, menus contextuais, navegação por teclado, agrupamento de importação/exportação e contenção do painel. Capturas visuais das duas geometrias revisadas. Sem chave, conta ou reprodução YouTube real nos testes.

Aplicação local: instalado `/tmp/orbitz-youtube-modern-library.flatpak`, commit `379dc311996f236508d0e6c1e2cf0d1d03f9ada69e0af5f9bc4347df11d24f1b`, SHA-256 `4e8859d2853adf931093a7d0bd23a2a31d81912f1004168ea0fdbffa2b42a818`. Quinze arquivos instalados comparados às fontes testadas. Instância anterior fechada via Quit para preservar progresso e aplicativo reaberto; biblioteca, chave e preferências não foram editadas pelo procedimento de atualização. Sem publicação.


## Vinte resultados por consulta (31/10/2026)

Busca e recomendações solicitam e preservam até 20 vídeos nos quatro filtros. Removidos os limites anteriores de oito resultados e o corte de leitura em dezesseis itens. O cache de recomendações passa a identificar o limite usado; caches antigos são renovados uma vez, inclusive se o YouTube retornar legitimamente menos de vinte resultados. Interface continua rolável e sem corte adicional. Verificação com respostas sintéticas cobre vinte itens, os quatro filtros, resposta vazia e renovação do cache. Sem chave/API real nos testes.

Validação final: 76 testes Python e 16 scripts JavaScript aprovados. Instalado `/tmp/orbitz-youtube-twenty-results.flatpak`, commit `0ddad1b3bf11a77d277f10ee909bd4be16afbed005d783ebf44727b13e094332`, SHA-256 `a3350eb296afdf4aca083d0091b73d919ff4a28753bf56dec5a982bc00ba906d`. Fontes instaladas conferidas; app fechado normalmente via Quit e reaberto. Preferências e biblioteca preservadas; sem publicação.


## Sugestões personalizadas nas quatro abas (31/10/2026)

Com busca vazia, Vídeos, Shorts, Ao vivo e Podcasts carregam até 20 sugestões por categoria. Planejamento local combina interesses explícitos, buscas da própria aba e buscas globais recentes, com deduplicação. Favoritos servem de fallback inicial quando ainda não há interesses ou buscas; a ausência de sinais usa sugestões gerais. Até três temas são combinados em uma consulta OR suportada pela API. O filtro Shorts e eventType=live passam a valer também sem termo; lives não têm corte de data que eliminaria rádios antigas ainda ativas. Podcasts mantêm a aproximação textual, inclusive nas alternativas OR.

Interesses (até dez) e opção de usar buscas recentes ficam em Configurações. Apenas buscas bem-sucedidas e não URLs entram no histórico local, limitado a 30 entradas/30 dias; a limpeza remove entradas expiradas. Revisionamento impede que uma busca em andamento restaure o histórico após limpar/desativar a preferência. A transferência de biblioteca continua excluindo buscas e preferências. Nenhum histórico da conta Google é consultado.

Cache privado 0600, limitado a um arquivo por categoria, com chave de perfil/idioma/termos/limite. Prazo de seis horas, cinco minutos para lives ou respostas vazias. Locks por categoria agrupam solicitações simultâneas iguais. Não existe polling de recomendações. Frontend agrupa trocas rápidas por 180 ms, aborta solicitações substituídas e valida sequência, aba e campo de busca antes de renderizar. Abrir a descoberta/limpar o campo recupera as sugestões atuais; listas antigas são removidas antes de trocar de aba.

Verificação: testes sintéticos cobrem os quatro filtros, fontes de preferências, favoritos iniciais, expiração/deduplicação/limite de histórico, exclusão durante requisição pendente, opt out, caches por perfil, arquivos privados, concorrência e respostas vazias. Teste GTK/WebKit com HTTP e SQLite reais, perfil temporário e provedor sintético confirmou vinte itens nas quatro abas, influência de uma nova busca, edição dos interesses, opt out e limpeza. Sem chave/conta/API real nos testes. Referência dos operadores/filtros: [YouTube search.list](https://developers.google.com/youtube/data/reference/rest/v3/search/list).

Verificação final: 86 testes Python e 16 scripts JavaScript aprovados; sintaxe Python/JS, paridade PT/EN e whitespace aprovados. O teste integrado GTK confirmou as quatro categorias, vinte resultados, uso de nova busca e preferências/limpeza sem uso de API real.

Aplicação local: instalado `/tmp/orbitz-youtube-personal-recommendations.flatpak`, commit `6766d2cab6cc114f08174cd9176fe1ee5d4f2634148f95842cb4ceacdc69bf17`, SHA-256 `18505407b526885dfe69dbd5459dd17081934138af3b1557b10906e259f51c4d`. Dezesseis arquivos instalados comparados às fontes testadas; instância anterior fechada via Quit e aplicativo reaberto. Chave, biblioteca e preferências existentes não foram editadas pelo procedimento de instalação. Sem publicação.


## Nome de exibição YouTube API Player (31/10/2026)

Atualizados título da janela e do documento, traduções PT/EN, entrada desktop, nome AppStream, identidade MPRIS, diagnóstico, launcher e README para o nome solicitado YouTube API Player. IDs técnicos, executável e caminhos de dados foram preservados para manter instalação e preferências. Nenhuma funcionalidade OAuth ou barra de engajamento foi adicionada. A integração com o YouTube continua restrita à Data API e ao player IFrame oficial.

Observação de distribuição: as [diretrizes oficiais de marca](https://developers.google.com/youtube/terms/branding-guidelines) vedam YouTube/YT e derivados no nome de aplicativos de terceiros. O nome solicitado foi aplicado localmente, sem publicação; esta observação deve ser considerada ao escolher o nome para distribuição.

Verificação da renomeação: 86 testes Python e 16 scripts JavaScript aprovados; desktop-file-validate, AppStream e git diff --check aprovados. Instalado `/tmp/youtube-api-player-rename.flatpak`, commit `5dbb02928bbaca14ff23c2bb5098144a21061b4c6882fb061400d34f6b6bd3ee`, SHA-256 `a122c6198009283bef1f81ce494bbb974c6b8907f8983055c687991080d26246`. Dezesseis arquivos instalados conferidos byte a byte; aplicativo fechado normalmente e reaberto, sem alterar os dados existentes.

## Assinatura nos títulos principais (31/10/2026)

Nome de exibição atualizado para `YouTube API Player - By Orbitz` na janela, documento, entrada desktop, AppStream, MPRIS e diagnósticos. Cabeçalho compacto preservado. 86 testes Python e 16 scripts JavaScript aprovados, desktop/AppStream e whitespace validados. Atualização local instalada (commit `c6ff28b406cd213a550d8461a338e4c779a73b1898b6c9c2645ce50ce5e7f159`) e aplicativo reaberto, preservando IDs e dados.

## Título e canal do vídeo (31/10/2026)

Aviso de retomada mostra título em strong e canal entre parênteses em peso normal, quando disponível. Resultados de busca/recomendação usam a mesma apresentação. Nome do canal passa da resposta de pesquisa para a seleção e é preservado no snapshot de retomada; player pode complementar os metadados durante reprodução. Campo opcional validado (string, até 200 caracteres), compatível com snapshots anteriores. Texto do provedor continua tratado como texto, sem HTML. 86 testes Python e 16 scripts JavaScript aprovados; whitespace validado. Flatpak local atualizado, commit `9aa5cf44f417debee706fece01e29ee2fc09c02e2cca102135c6467dca01201f`; três arquivos alterados conferidos na instalação. Aplicativo fechado normalmente e reaberto.

## Canal ausente e aviso responsivo (31/10/2026)

Adicionada consulta pública videos.list(part=snippet) para preencher canal ausente no último vídeo, inclusive snapshots anteriores, sem exigir reprodução. Consulta agrupada por ID na sessão; sem polling. Atualização transacional de metadados só afeta o ID ainda salvo e preserva posição/duração/live. Falhas de rede/chave não bloqueiam retomada. Título em negrito e canal normal; acima de 40 pontos Unicode, fonte 12px e quebra natural entre palavras conforme espaço disponível, botões podem passar à próxima linha. 87 testes Python e 16 scripts JavaScript aprovados, incluindo preservação de posição e resposta obsoleta. Fontes alteradas conferidas no Flatpak instalado, commit `a8025ecc74d7d42cc05157a9eb3d621dc0827f89007b1d1acc3392957792816c`; aplicativo reaberto. Consulta real depende da chave e conectividade; testes não acessam dados pessoais.

## Contagem pública de curtidas (31/10/2026)

Resultados de busca e recomendações mostram coração e contagem no canto inferior direito do cartão. Consulta oficial videos.list(part=statistics), IDs em lote (até 50), cache em memória por cinco minutos limitado a 200 vídeos e lock de agrupamento. Sem polling, OAuth ou ação de curtir. Ausência/erro exibe traço, nunca zero inventado. Renderização reserva espaço e ignora nós removidos após troca de busca/aba. Formatação inteira com BigInt, PT/EN e rótulos acessíveis. 89 testes Python e 16 scripts JS aprovados; novos testes cobrem lote, zero, ausência, cache, expiração e validação sem rede. Instalado commit `cad49a1f4324af39c25b0e573ad804bf54d30381436866158ed8a20d35de316a`, cinco arquivos conferidos, aplicativo reaberto. Referência: https://developers.google.com/youtube/v3/docs/videos#statistics.likeCount .

## Alinhamento do indicador de curtidas (31/10/2026)

Indicador separado do texto do título e centralizado verticalmente como coluna à direita do cartão, com coração vermelho preenchido de 26px e contagem embaixo. Título/canal permanecem centralizados independentemente do indicador. Atualização assíncrona altera apenas o número. 89 testes Python e 16 scripts JS aprovados; whitespace e HTML instalado conferidos. Commit local `ea504c3f3bf552785ff50568dcdfa2137ebb8ef505081622bf7015ac3799a387`, aplicativo reaberto.

## Vídeos similares na biblioteca (01/11/2026)

Ação localizada no menu de favoritos, assistir depois, fila e vídeo atual. Fecha biblioteca, abre descoberta na categoria Vídeos e consulta search.list usando título, removendo o vídeo de origem dos resultados. Trata-se de busca por relevância temática, sem scraping nem acesso às recomendações privadas da conta. Reutiliza cancelamento/sequência existentes; reprodução não é alterada ao abrir a busca. 89 testes Python e 16 scripts JavaScript aprovados; verificação sintética adicional confirmou consulta, categoria e exclusão da origem. Atualização instalada, commit `001dac6b13598afa80cdf3d1a205b2fef1c2411630de2432b827bae8505f9aef`; quatro arquivos conferidos e aplicativo reaberto.

## Traço para contagem desconhecida (01/11/2026)

Mantido — no carregamento ou indisponibilidade das curtidas, conforme confirmação do usuário. Zero somente quando retornado pela API. Coração sem preenchimento e em cor neutra preservado. HTML instalado conferido byte a byte e whitespace validado. Commit `8e22dca7c3a44401e742b87c8678390a2423c871eb53d14f82fd3d5bb4941fd5`, aplicativo reaberto.

## Múltiplas janelas (01/11/2026)

Nova janela no menu da engrenagem, ação desktop New Window/Nova janela e Ctrl+N. Argumento --new-window encaminhado à instância GTK; ativação normal apresenta uma janela existente. Cada janela possui servidor/token, WebView, pesquisa, timers e player próprios. Biblioteca/preferências compartilhadas; fechamento libera apenas os recursos daquela janela. MPRIS adicional usa conexão privada e nome próprio, evitando colisões de objeto/controles. Permissão adicional restrita aos nomes MPRIS do aplicativo. 89 testes Python e 16 scripts JS aprovados; validação desktop e whitespace aprovados. Teste GTK real com perfil temporário e recomendações sintéticas confirmou duas janelas, URLs diferentes, fechamento da primeira e criação de terceira mantendo a segunda, sem erros de registro MPRIS. Flatpak instalado, commit `abb4b960ba1785da8a538bd61f6688855f2b9a1f766ca559c76a4e2346446ee0`; fontes instaladas conferidas e aplicativo reaberto.

## Alvos do minigame (01/11/2026)

Nave seleciona cacto, pedra ou mosquito mais próximo à frente do personagem. Disparos do personagem e laser da nave miram no centro vertical real do obstáculo; mosquito considera altitude de voo. Corrigida mira anterior que apontava para o chão sob o mosquito. 89 testes Python e 16 scripts JS aprovados; testes incluem seleção de pedra/mosquito e altura da mira. HTML instalado conferido, commit `9ea4ff18c09af11883a71f3c2084f83e930c26ab3341b0f38b0925e39a553b0e`; janela principal fechada normalmente e aplicativo reaberto.

## Segundo minigame de labirinto (01/11/2026)

Jogo original inspirado no clássico de perseguição, desenhado em canvas sem imagens externas. Labirinto conectado, pontos, quatro pastilhas de força, três fantasmas com navegação por distância, três vidas, pontuação, vitória e reinício. Shift+↑/↓ alterna com o runner preservando os estados; setas movem e Espaço inicia/reinicia. Atalhos ignoram campos de texto, modais, busca e player visível. Jogo oculto pausa, RAF é cancelado e relógio reiniciado ao voltar, evitando saltos de simulação. Dados limitados a cada janela; sem solicitações de rede para jogar. Novo script servido apenas sob token do documento.

89 testes Python e 17 scripts JS aprovados. Testes novos verificam conectividade de todos os pontos, paredes, coleta/poderes, colisões, vidas e vitória. Teste GTK/WebKit real com perfil temporário confirmou alternância, início, retorno e exclusão de campos editáveis; captura de tela inspecionada. Fontes instaladas conferidas, commit `0a0360b3f983d703bbfd577819f35668e9a49c7d4ba4c1a3e5b0bdce9d89a0cf`; janela principal fechada normalmente e aplicativo reaberto.

## Movimentação contínua do labirinto (01/11/2026)

Substituídos saltos de célula por coordenadas contínuas com velocidade constante, simulação em passos de 1/120s e desenho independente em até 60fps. Não há tween com atraso: entrada muda intenção diretamente, reversão inverte o segmento atual imediatamente e curvas são guardadas até o próximo centro com passagem válida. Fantasmas passam a velocidades contínuas em vez de pular frames; colisões verificadas em subpassos contra posições reais. Boca acompanha distância percorrida, fantasmas têm olhos direcionais e animação dos pés, pastilhas pulsam. Paredes conectadas e cenário/pontos em camada cacheada; navegação recalculada somente quando muda a célula de referência. Ocultar/pausar cancela RAF e zera relógio, sem recuperar tempo em rajada.

89 testes Python e 17 scripts JS aprovados. Novas verificações cobrem posição fracionária, reversão no meio do corredor, curva guardada até o centro, rejeição de curva bloqueada mantendo movimento, equivalência temporal, vida final e regras anteriores. Teste GTK/WebKit real confirmou vários desenhos entre células, limite de frames e ausência de desenho com jogo oculto; captura visual inspecionada. Flatpak instalado, commit `cfcb6d2655267ae253973781642d5bc8a352eb9e657dbafb83ad5065c3dbe728`, script instalado conferido e aplicativo reaberto.

## Efeitos sonoros do runner (01/11/2026)

Cinco efeitos Kenney Digital Audio CC0 locais para salto, tiro, laser da nave, impacto e fim de partida. Botão acessível no canto inferior direito, com estado aria-pressed e rótulos PT/EN. Preferência game_sound booleana persiste no SQLite, padrão desativado; salvamentos serializados e inicialização não sobrescreve interação recente. Web Audio criado após gesto/opt-in, buffers decodificados uma vez, sem espera nos controles nem reprodução atrasada após decode. Até seis vozes simultâneas com intervalo mínimo por efeito. Silenciar, ocultar jogo, abrir painéis ou perder foco interrompe vozes; labirinto não emite sons e oculta o botão. Assets servidos por caminhos exatos sob token, sem acesso arbitrário ao filesystem. Cinco OGG e licença CC0 incluídos no pacote.

91 testes Python e 17 scripts JS aprovados, incluindo preferência e limites dos recursos HTTP. Teste GTK/WebKit confirmou inicialização e troca de jogos sem regressão com o módulo de áudio carregado. Flatpak instalado, commit `e99da86072bf5ef932b59f2ce3ef4464161b861058e0acfdad682b8f2eafb896`; scripts e cinco áudios instalados conferidos byte a byte. Aplicativo reaberto.

## Remoção do som de impacto da bala (01/11/2026)

Removida a chamada de áudio no acerto dos projéteis do personagem, preservando efeito visual e som do disparo. Whitespace validado e HTML instalado conferido, incluindo ausência do evento hit e presença de shot. Atualização local `068e93ef234fad7b10d57512d1823b14f567aa6b0073ce625a58c595234a331b`, aplicativo reaberto.

## Sons próprios do labirinto (01/11/2026)

Sete efeitos sintetizados localmente: duas variações alternadas de coleta de pontos, pastilha, captura de fantasma, perda de vida, vitória e início. Timbres retrô originais, sem amostras ou melodias extraídas do jogo de referência. Buffers gerados uma vez por contexto, envelopes curtos evitando cliques e amplitude com margem contra saturação. Eventos emitidos pela simulação e consumidos no mesmo frame, fila limitada, sem alterar movimento/controles. Botão e preferência compartilhados pelos dois jogos; troca interrompe vozes e somente eventos do jogo ativo são aceitos. Gesto de teclado do labirinto também desbloqueia o contexto para preferências já ativadas.

91 testes Python e 18 scripts JS aprovados. Síntese validada em 44,1/48 kHz, amostras finitas, ausência de saturação, envelopes e variações; eventos testados para coleta, poderes, captura, morte e vitória. Teste GTK/WebKit confirmou botão liga/desliga e presença no labirinto, troca de jogos e pausa de desenho sem regressão. Fontes instaladas conferidas, commit `7bf9f8e995deea5e6d4a6d8173efd8a286ba40619ff8aa08aadee8eb04140b6b`; aplicativo reaberto.

## Volume e Orbitron (01/11/2026)

Barra de volume 0–100 ao lado do ícone sem fundo/borda e link orbit.zone, todos alinhados pelo centro de uma única faixa flex. Link com Orbitron variável local (Google Fonts, SIL OFL 1.1 incluída). Slider acessível com teclado e leitura percentual; ícone mantém atalho de silenciar/restaurar último volume. Ganho Web Audio atualizado sem reiniciar sons, pequeno ramp para evitar cliques. Preferência inteira validada/persistida e gravação agrupada durante arraste; zero silencia. Migração respeita preferência anterior de som. Em janelas estreitas, instruções sobem para evitar sobreposição com o controle.

92 testes Python e 18 scripts JS aprovados. Teste GTK/WebKit real verificou 35%, silenciar/restaurar, alinhamento vertical com erro inferior a 1px, borda removida e família Orbitron; captura visual inspecionada. Fontes instaladas conferidas, commit `fbd3a52fd4341db21cf158174a6b00212706d83346b3fccbdeccf93313c6cd93`; aplicativo reaberto.

## Volume vertical (01/11/2026)

Link e volume transferidos do rodapé ao canto superior direito abaixo da pontuação/recorde. Slider vertical com mínimo embaixo e máximo em cima, aria-orientation vertical, mantendo preferências e controles. Teste GTK/WebKit confirmou proporção vertical, alinhamento e operação; captura visual inspecionada. Whitespace validado e script instalado conferido. Commit `4eb6544835e21b6e72b1aacbbe3bb5a6c724ad5f4f7bbf6e3329fb932c6eba15`, aplicativo reaberto.

## Posição independente do link (01/11/2026)

Conforme esclarecimento, orbit.zone permanece no canto inferior direito, em Orbitron, no runner e labirinto; somente volume vertical fica no topo. Link removido do grupo de controles. Teste GTK/WebKit passou com link abaixo do slider e alinhado à borda direita; script instalado conferido. Commit `5cf5a2cb7daa36957060f52683b1f8541a4f71e1f571a040e74db55621aea13b`; aplicativo reaberto.

## Link centralizado na grama (01/11/2026)

Link orbit.zone ocupa faixa inferior de 34px, igual à altura do chão desenhado pelo runner, com alinhamento flex ao centro vertical e borda inferior em zero. Whitespace validado e script instalado conferido. Commit `af98355c425772fc6ab9a2d455ed8d63eb35eeee0dc94cf6466cf636b0d88c81`; aplicativo reaberto.

## Correção do New Window pelo menu do sistema (01/11/2026)

Causa reproduzida: app.run(None) descartava --new-window, fazendo a ação desktop apenas apresentar janela existente. Corrigido para app.run(sys.argv). Novo teste GTK lança a Desktop Action via Gio.DesktopAppInfo e passa argumentos por um segundo processo à instância existente; falhou antes da correção e passou depois. 92 testes Python e 18 scripts JS aprovados. Atualização instalada, commit `e3eaf57487adbb5613153d8515a8b5a8d8b0a8d1365f395f4a38fa4e93afe1a8`, fonte instalada conferida. Verificação final da ação desktop efetivamente exportada pelo Flatpak: xwininfo confirmou uma janela antes e duas após launch_action(new-window). As duas janelas foram mantidas abertas para o usuário.

## Pausa dos jogos por Esc (01/11/2026)

Esc alterna pausa manual nos dois jogos, com estado individual preservado na troca de jogo, aviso visual e áudio interrompido. Repetição de tecla não alterna várias vezes; campos de texto, player, busca e modais são excluídos. RAF/timers de simulação são reiniciados sem recuperar tempo de pausa; entradas de salto/movimento não modificam jogo pausado. Em tela cheia de jogo, Esc pausa em vez de sair da tela cheia; comportamento de vídeo preservado. 92 testes Python e 18 scripts JS aprovados. Teste GTK/WebKit verificou pausa/retomada nos dois jogos, overlay e exclusão de repeat. Atualização instalada, commit `cc3108e4f22be5f21112021f168a7123a438409105c2a369b74d250d4f434cca`; fontes conferidas, janelas anteriores fechadas normalmente e aplicativo reaberto.

## Link sem sombra e sublinhado (01/11/2026)

orbit.zone com text-shadow:none e text-decoration:none também em hover/foco. Whitespace validado e HTML instalado conferido. Commit `9047ab568dd0dc3f135ad19c3c9eaae7624abd95f45edbb107d5784452d01358`; aplicativo reaberto.

## Retorno de foco do volume (01/11/2026)

Slider sem outline/box-shadow no foco. Arraste captura ponteiro; pointerup/pointercancel, inclusive fora do slider, salva volume e devolve foco ao canvas do jogo ativo quando disponível. Foco por teclado permanece até navegação normal. Teste GTK/WebKit confirmou ausência de outline e retorno ao runner em evento de soltura sintético. Script instalado conferido e whitespace aprovado. Commit `98273125139cda98236aa1875d49968014321a26752b7cecb02f9bdbd7838b3f`; aplicativo reaberto.

## Orbit Invaders, terceiro minigame (01/11/2026)

Jogo original de defesa espacial, 45 alienígenas por onda, movimento/descida contínuos, tiros com cooldown, inimigos atirando, abrigos destrutíveis, nave bônus, poderes de tiro duplo e escudo, três vidas, invulnerabilidade temporária, ondas progressivas e reinício. Recorde privado separado em invaders.json com escrita atômica. Setas/A-D movem; Espaço dispara; arraste/touch também move e dispara. Shift+↑/↓ percorre os três jogos em ordem/inversa, preservando partidas. Esc pausa por jogo; volume e sons reutilizados com exclusão por jogo ativo. Recursos gráficos originais cacheados, simulação 120Hz e desenho limitado a 60fps somente quando ativo.

Suíte Python/JS aprovada, incluindo testes de movimento, limites, cooldown, colisões, ondas, abrigos, poderes, invasão, nave bônus e recordes isolados. Teste GTK/WebKit real confirmou ciclo de três jogos, tiro/movimento, pausa/retomada, retorno do foco do volume e ausência de desenho oculto; captura visual inspecionada. Após interrupção, instalação retomada e concluída, commit `343b1f9451c7f0c433ee69fefcbfad888d982144234920656a7c2855288f94fe`; fontes instaladas conferidas byte a byte. Janelas anteriores fechadas normalmente e aplicativo reaberto.

## Campo responsivo do Orbit Invaders (01/11/2026)

Removida a moldura retangular interna e a reserva lateral fixa. Campo cobre largura/altura disponíveis com margens de HUD/rodapé; escala uniforme mantém proporção dos sprites e mundo adapta largura/altura à janela. Redimensionamento preserva pontuação, vidas, danos dos abrigos e posições relativas. Limite de invasão reescalado evitando derrota artificial ao reduzir a altura. Reinício e ondas seguintes respeitam dimensões atuais, ponteiro usa a transformação atual.

Suíte Python/JS aprovada. Casos de layout: 360×220, 700×450, 1920×1080, 2560×480 e 480×1000, verificando cobertura da área, limites, preservação da partida e aproximação segura. Teste GTK/WebKit de controles, pausa, ciclo e foco aprovado. Fonte instalada conferida; commit `f2e010c9844b1353072f5949663dfb788dc0950880a91f64944857ec5bbd5522`; aplicativo reaberto.

## Orbit Asteroids, quarto minigame (01/11/2026)

Jogo vetorial original de nave livre: rotação, aceleração/inércia com velocidade limitada, mundo toroidal, tiros com cooldown, asteroides divididos em duas partes até tamanho mínimo, disco voador com tiros direcionados, partículas limitadas, três vidas, invulnerabilidade e ondas progressivas. Campo responsivo sem moldura; recorde independente em asteroids.json. Shift+↑/↓ percorre quatro jogos, Esc pausa por jogo e volume compartilhado; eventos sonoros aceitos apenas do jogo ativo. Simulação 120Hz e desenho até 60fps, sem processamento contínuo oculto.

Suíte Python/JS aprovada; novos testes cobrem inércia, rotação, wrap/distância toroidal, divisão, cooldown, vidas, ondas, resize e isolamento do recorde. Teste GTK/WebKit real confirmou ciclo de quatro jogos, movimento/disparo, pausa, retorno de foco do volume e ausência de desenho oculto; captura visual inspecionada. Fontes instaladas conferidas, commit `e02c8c01b003cd7c74ea850b0fe7e6b49f1a4ccd3f71dc9cc95582391e268fe2`; janelas antigas fechadas normalmente e aplicativo reaberto.

## Início com cards e miniatura de retomada (01/11/2026)

Tela inicial com quatro cards em grade 2×2, uma coluna com rolagem abaixo de 480px. Miniaturas vetoriais estáticas desenhadas pela aplicação, sem screenshots, canvas, controles, animações ou áudio. Todas as simulações/desenho/áudio bloqueados no início. Clique abre jogo selecionado, botão Jogos retorna à seleção; acesso Minigames no menu permite sair do vídeo pausando o player. Estado individual dos jogos preservado.

Aviso do último vídeo inclui imagem obtida pelo mesmo mecanismo de miniaturas da biblioteca, com fallback oculto em erro; título em negrito, canal e botões mantidos. Na home, aviso integra o fluxo acima da grade para não encobrir cards; fora dela mantém posição anterior.

Suíte Python/JS aprovada, teste GTK dos quatro jogos após seleção aprovado. Novo teste GTK/WebKit confirmou quatro SVGs sem elementos ativos, seleção/retorno de cada jogo, miniatura correspondente ao último ID e ausência de sobreposição entre retomada e cards. Casos largo e estreito aprovados, capturas visuais inspecionadas. Fontes instaladas conferidas, commit `3c2fb2745c86474e1dca1112a818e0828a26900628fb90652adc39e05b42745d`; aplicativo reaberto.

## Mini telas com renderizadores reais (01/11/2026)

Substituídas as ilustrações SVG independentes. Cada jogo agora compartilha sua função de desenho entre a partida e o card: personagem/grama/céu/obstáculos do runner, labirinto/personagens, sprites/nave/abrigos do Invaders e nave/rochas vetoriais do Asteroids. Cards usam canvas e estados iniciais independentes, sem executar física, controles, áudio ou RAF. Mini tela redesenhada apenas na criação e mudança de dimensões pelo ResizeObserver; tempo fixo. Sem cópia de screenshots ou alteração da partida atual. HUD e mensagens de início são omitidos nas mini telas. Cache do labirinto separado por destino.

Suíte Python/JS aprovada. GTK/WebKit verificou quatro canvases com cenas desenhadas, seleção/retorno, retomada e ausência de sobreposição; captura visual inspecionada. Testes reais de labirinto, Invaders e Asteroids aprovaram animação, controles, pausa, troca e desenho oculto após refatoração. Fontes instaladas conferidas, commit `27334b8ebcd3ab59907ae306d13222e5c62d1dfda154988d0b91578f0a078ba3`; aplicativo reaberto.

## Cards com cena integral e título central (01/11/2026)

Removidas faixa inferior azul e chamada Jogar. Mini tela ocupa 100% da largura e altura do card, com resolução ajustada à proporção disponível. Título sobreposto ao centro nos dois eixos, em Orbitron local. Card inteiro continua clicável e acessível por teclado. Grade responsiva e miniatura do último vídeo preservadas. Suíte Python/JS aprovada; teste GTK verificou preenchimento, título central com erro inferior a 1px, Orbitron e ausência do rótulo Jogar; captura visual inspecionada. Fontes instaladas conferidas, commit `3587212cdc62e038bea3304b83d0ee582caea9c3e2163c75644d88771be5c1b1`; aplicativo reaberto.

## Clareira atrás do título do Invaders (01/11/2026)

Apenas a cena independente do card remove inimigos que interceptam a faixa central do título, com margem para tamanho dos sprites e posição transformada. Formação da partida preservada. Whitespace validado e arquivo instalado conferido. Commit `da91560bca556d1f5e077872bc0e0601e6ccd0fa7ff6027c8d001e70232bbf6f`; aplicativo reaberto.

## Títulos maiores sem sombra (01/11/2026)

Fonte Orbitron dos cards ampliada de clamp(13px,1.8vw,22px) para clamp(18px,2.4vw,30px), mantendo centro e responsividade. text-shadow:none. Whitespace validado e fonte instalada conferida. Commit `ce478ba00889440eadf479b0a9f3b8cc3d27f8c24be1d2693fc9bbdbcbbf6570`; aplicativo reaberto.

## Redesenho no retorno à seleção (01/11/2026)

Ao exibir a home, as quatro mini telas são renderizadas explicitamente, independente de alterações de tamanho. ResizeObserver invalida o tamanho salvo quando oculto. Teste GTK abre cada jogo, limpa propositalmente os buffers dos cards enquanto ocultos e volta sem redimensionar; verifica pixels redesenhados nos quatro cards após cada retorno. Teste passou, whitespace validado e script instalado conferido. Commit `fc722a47e6654e156682ba0bb7c1142307fdd36c4c28f2aff33a8110be8a2182`; aplicativo reaberto.

## Keep Watching permanente (01/11/2026)

Seção própria Keep Watching acima do cabeçalho Minigames, com última miniatura/título/canal e único botão Continue assistindo (PT). Removida a opção Agora não e o rótulo condicional Voltar ao vídeo. Seção permanece no início, inclusive sem histórico (mensagem vazia); não aparece sobre partidas. Ao voltar do vídeo à home, progresso é salvo e estado atualizado. Suíte Python/JS aprovada; GTK/WebKit confirmou título da seção, botão único, texto uniforme, miniatura e ausência de sobreposição. Captura visual inspecionada. Fontes instaladas conferidas, commit `878b5e73414a54112f8a282883440997e2242f397508eb5e50ffe3392599f279`; aplicativo reaberto.

## Orbit Breaker, Orbit Lander e sons do Asteroids (01/11/2026)

Dois jogos originais adicionados à grade (duas colunas/três linhas, uma coluna estreita), com mini telas usando o mesmo renderizador da partida. Breaker: plataforma por setas/A-D ou mouse, lançamento por Espaço, blocos com resistência, três vidas, ondas, poderes de plataforma maior, multiball e laser. Lander: gravidade/inércia, combustível, motor por ↑/W e rotação por setas/A-D, pouso condicionado a velocidade e inclinação, plataforma menor por missão, vento e obstáculos de teto a partir da terceira missão. Recordes privados independentes. Ambos usam volume, Esc e ciclo Shift+↑/↓, cancelam desenho/input ocultos e mantêm simulação em passos fixos.

Asteroids deixa de reutilizar os samples do Invaders: síntese original com quatro disparos e três impactos alternados, além de início, nave especial, perda de vida e vitória exclusivos. Sons próprios para os dois novos jogos; envelopes e limitação de vozes preservados.

Suíte Python/JS aprovada, incluindo física e poderes do Breaker, missões/pouso seguro e inseguro/combustível/teto do Lander, isolamento dos recordes e validação das formas de onda. Testes GTK reais de Breaker e Lander aprovaram animação, pausa, foco e alternância; teste da home aprovou seleção/retorno dos seis cards e preservação de mini telas. Uma execução do teste de frames do Lander falhou no limite de tempo inicial; repetição com captura de erros passou sem erro JavaScript. Fontes instaladas conferidas, commit `0072b65daf8d919f48900e8640fb358944a4fa8c45292de321845d945c77e0f9`; janelas anteriores fechadas normalmente e aplicativo reaberto.

## Faixa translúcida nos títulos (01/11/2026)

Fundo preto a 55% de opacidade na faixa central dos títulos dos seis cards, cobrindo toda largura interna. Orbitron, centro e ausência de sombra preservados. Whitespace validado e script instalado conferido. Commit `0c54ea13bfafc4b299f03f921dd4c2ad8c09fb1a83b9db5323fc5d7cf1cced58`; aplicativo reaberto.

## Retomar pelos controles (01/11/2026)

Qualquer tecla efetiva de controle do jogo ativo retoma pausa manual. Comando é encaminhado uma única vez após a retomada, incluindo o labirinto cujo listener precede o controlador. Esc continua alternando pausa. Repetições automáticas, campos editáveis, modificadores, home e painéis são excluídos. Aviso de pausa PT/EN atualizado. Suíte Python/JS aprovada; novo teste cobre cada tecla real nos seis jogos, encaminhamento único e exclusões. Script instalado conferido, commit `d75ece80bd49ea24a5e23e8cbf16e68dffa3bd2c7bd34f87b9b36cf9aaf42f27`; aplicativo reaberto.

## Fases, recorde, cereja e passagens do labirinto (01/11/2026)

Fases avançam automaticamente após dois segundos, preservando pontuação e vidas. Três variantes conectadas de layout; velocidades crescem com limite e duração de pastilha diminui até três segundos. Recorde independente em maze.json, leitura no início e gravação agrupada ao ultrapassar recorde, ao concluir fase, pausar ou sair do jogo. HUD inclui recorde e fase. Cereja central aparece após 16 segundos ativos, permanece oito segundos e reaparece 22 segundos após coleta/expiração; bônus 100×fase limitado a 500 e efeito próprio. Pausa congela os prazos.

Quatro entradas nos cantos das linhas 1/15, emparelhadas horizontalmente. Caminhos/BFS dos fantasmas consideram túneis; movimento mantém segmentos curtos com wrap somente no limite e reversão imediata preservada. Desenho duplica a parte que cruza a borda, com clipping; colisão considera distância periódica horizontal.

Suíte Python/JS aprovada, cobrindo quatro entradas nos dois sentidos, passagem fracionária e reversão, cereja/coleta/expiração, progressão sem perder vidas/pontos, conectividade de fases e isolamento do recorde. Teste GTK/WebKit de renderização, controles e pausa aprovado. Fontes instaladas conferidas, commit `7f3f23e9e9e2bf0a4b7fa530758c512caae864194b0a6a2fcc0d0e72942ae6e1`; aplicativo reaberto.

## Grade larga 3×2 (01/11/2026)

A partir de 1200px, seis cards em três colunas e duas linhas. Janelas médias mantêm duas colunas e estreitas até 480px uma coluna. Whitespace validado, teste de colunas atualizado e script instalado conferido. Commit `a945062912f6578583861bd1a421e48511ee8e3237e579fddbaf701a2f2e70f2`; aplicativo reaberto.

## Nome Orbit Games (01/11/2026)

Nome da seção e item de menu atualizado para Orbit Games em PT/EN. Whitespace validado e catálogos instalados conferidos. Commit `69b804196e00bcedac9a7900b335a1b3f5960847195b10434156f2c7bb5946e6`; aplicativo reaberto.

## Recomendações específicas por categoria (01/11/2026)

search.list solicita até 50 candidatos e devolve até 20 válidos/deduplicados. Ao vivo mantém eventType=live e exige liveBroadcastContent=live. Demais abas rejeitam live/upcoming. Podcasts usa consulta temática, videoDuration=long (>20min), evidência podcast/videocast no título/canal/descrição e rejeita títulos de cortes/shorts/clips. API não possui classificação nativa de podcasts; hint explica a limitação. Podcasts genéricos deixam de ter janela de publicação de sete dias. Shorts mantém o filtro oficial short (<4min), sem alegar classificação nativa Shorts.

Personalização vazia tenta uma única busca geral na mesma categoria, com rótulo genérico e termos vazios, sem trocar de modo. Cache por categoria/perfil passa a versão 3 para invalidar resultados antigos e guarda apenas marcador de fallback, sem inserir termos explícitos adicionais no arquivo.

Suíte Python/JS aprovada. Novos testes sintéticos cobrem transmissão ativa/agendada em cada categoria, evidência de podcast, rejeição de cortes, fallback restrito ao modo e metadados do fallback no cache; fixtures de vinte resultados atualizadas para incluir tipos de transmissão. Não houve consulta à chave pessoal nem validação de resultados reais da conta. Fontes instaladas conferidas, commit `8cb48e08bbf90e06c3cc660667f77c8087e902a0f086cdb882cad51958b15286`; aplicativo reaberto. Fontes oficiais: https://developers.google.com/youtube/v3/docs/search/list e https://developers.google.com/youtube/v3/docs/search .
