# YouTube API Player — By Orbitz

### Seu vídeo no lugar certo do desktop.

Uma live ao lado do trabalho. Um podcast enquanto você organiza o dia. Um vídeo em uma janela que cabe no seu espaço.

O **YouTube API Player** leva a busca e a reprodução do YouTube para um aplicativo de desktop com janela ajustável, biblioteca pessoal e seis jogos no **Orbit Games**. Escolha o conteúdo, posicione o player e deixe os controles saírem de cena quando quiser apenas assistir.

**Linux · Flatpak · Português e inglês · Integração com as APIs oficiais do YouTube**

[Conheça a beta](docs/releases/0.2.0-beta.1.md) · [Como instalar](#instale-e-comece-a-assistir) · [Relate um problema](https://github.com/orbitzone/orbitz-youtube-api-player/issues)

> **Beta 0.2.0-beta.1:** pacote local disponível para testes, ainda sem publicação no GitHub ou Flathub. As [notas da versão](docs/releases/0.2.0-beta.1.md) descrevem os recursos e as limitações atuais.

## Transforme o player em um widget para o desktop

Use uma janela compacta para acompanhar o que interessa enquanto continua usando o computador. Uma transmissão de notícias, sua rádio favorita ou um vídeo de referência pode ficar ao alcance dos olhos, no canto que você escolher.

- **Mantenha à vista:** ative **Sempre acima das outras janelas** no menu da engrenagem.
- **Encontre o tamanho ideal:** arraste qualquer uma das quatro bordas ou dos quatro cantos. O tamanho mínimo protege a área de uso.
- **Ajuste com precisão:** pressione **Ctrl+T** para mostrar uma moldura com alças de redimensionamento; use **Esc** ou **Concluir** para encerrar.
- **Deixe o vídeo em destaque:** ao entrar na área de conteúdo, cabeçalho e rodapé aparecem juntos em uma animação de meio segundo. Eles se recolhem quando você sai do aplicativo ou deixa o mouse parado por cinco segundos.
- **Aproveite seu espaço:** as faixas recolhidas ficam transparentes, e o conteúdo permanece no mesmo lugar durante a animação.

O resultado é uma experiência de widget usando a própria janela do aplicativo. Posicione, redimensione e mantenha o player sobre suas outras atividades. Você também pode abrir **Nova janela** pelo menu para separar pesquisas e conteúdos.

## Encontre algo que combine com o seu momento

Pesquise **Vídeos**, **Shorts**, **Ao vivo** e **Podcasts** em abas próprias. Os resultados mostram miniatura, título, canal e contagem pública de curtidas quando disponível. Encontrou algo para depois? O botão **+** coloca o vídeo na fila sem interromper o que está tocando.

As recomendações aproveitam os interesses que você informa e suas buscas recentes. Ajuste esses sinais em **Configurações → Recomendações para você**, desative o uso das buscas recentes ou limpe-as quando quiser. O aplicativo não acessa o histórico da sua conta do YouTube.

Os filtros seguem o que a API disponibiliza: a aba Shorts pode incluir outros vídeos curtos, e a busca de podcasts usa termos e critérios de relevância. A disponibilidade dos resultados depende do YouTube.

## Sua biblioteca, pronta para a próxima sessão

Abra o ícone de livros e organize o que vale guardar:

| Recurso | Para usar no dia a dia |
| --- | --- |
| **Favoritos** | Guarde os vídeos aos quais você sempre volta. |
| **Assistir depois** | Separe descobertas para outro momento. |
| **Fila** | Escolha a sequência, reorganize os itens e deixe o próximo vídeo começar ao terminar o atual. |
| **Vídeos similares** | Explore novos resultados a partir de um vídeo salvo. |
| **Importar e exportar** | Leve Favoritos e Assistir depois em um arquivo de biblioteca. |

Na tela inicial, **Keep Watching** mantém o último vídeo ao alcance de um clique. Use **Continue assistindo** para retomar o ponto salvo. Vídeos encerrados ou interrompidos com stop podem voltar ao começo; lives são reabertas no ponto disponível pelo YouTube.

Suas listas, fila e progresso ficam salvos localmente. O arquivo exportado da biblioteca inclui apenas Favoritos e Assistir depois, sem a chave da API.

## Uma pausa com Orbit Games

Entre uma sessão e outra, escolha um dos seis cards da tela inicial:

| Jogo | Sua próxima tentativa |
| --- | --- |
| **Orbit Runner** | Pule obstáculos e enfrente ameaças em uma corrida com um alien armado. |
| **Orbit Maze** | Percorra seis labirintos coloridos, coma fantasmas e colete cerejas para ganhar vidas. |
| **Orbit Invaders** | Proteja sua nave contra ondas de invasores espaciais. |
| **Orbit Asteroids** | Pilote, desvie e abra caminho entre asteroides. |
| **Orbit Breaker** | Acerte os blocos e aproveite os poderes especiais. |
| **Orbit Lander** | Guie um foguete até a plataforma; use o mouse para direcionar e segure o clique para acionar os motores. |

Os jogos têm recordes locais e volume ajustável. Pressione **Esc** para pausar, use uma tecla de controle para continuar e alterne entre jogos com **Shift+↑ / Shift+↓**. As miniaturas da home são estáticas, sem som ou partida rodando dentro dos cards.

## Conectado ao YouTube pelas APIs oficiais

A integração usa dois recursos do próprio YouTube: a **YouTube Data API v3** para encontrar vídeos e consultar informações públicas, e a **IFrame Player API** para controlar a reprodução no player incorporado oficial. [Conheça a API do player](https://developers.google.com/youtube/iframe_api_reference).

**Você pode começar com um link.** Cole a URL de um vídeo para assistir sem configurar uma chave. Para liberar buscas e recomendações, adicione sua chave pessoal da YouTube Data API v3 nas configurações.

O aplicativo não exige um login adicional por OAuth. As curtidas exibidas são informações públicas; ações na sua conta, como curtir um vídeo em seu nome, não estão disponíveis.

### E os anúncios?

**Nos testes de uso relatados nesta beta, os vídeos foram reproduzidos sem anúncios do YouTube.** Essa experiência pode mudar conforme o vídeo, a região e as decisões da plataforma.

A API não garante reprodução sem publicidade, e o aplicativo não bloqueia nem remove anúncios. O próprio YouTube informa que vídeos incorporados podem exibi-los. Por isso, a ausência observada nesta beta não é uma promessa de funcionamento permanente. [Como funcionam os anúncios em vídeos incorporados](https://support.google.com/youtube/answer/132596?hl=pt-BR).

## Instale e comece a assistir

A beta é destinada a **Linux x86_64**, com **X11 ou Wayland com XWayland**. O pacote usa Flatpak e o runtime GNOME 49; não exige uma versão específica do GNOME Shell.

1. Instale o [Flatpak para sua distribuição](https://flatpak.org/setup/).
2. Obtenha o pacote local `orbitz-youtube-api-player-0.2.0-beta.1-x86_64.flatpak`. Nesta fase, ele é gerado pelo procedimento de [preparação da beta](docs/releases/README.md); ainda não há download público desta versão.
3. Na pasta do pacote, execute:

```sh
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user ./orbitz-youtube-api-player-0.2.0-beta.1-x86_64.flatpak
flatpak run io.orbitz.YouTubeDesktop
```

Depois, abra pelo menu de aplicativos do Linux. Cole um link para assistir ou abra a engrenagem para configurar a busca.

**Para pesquisar:** no seu projeto do Google Cloud, habilite a YouTube Data API v3, crie uma chave em [Credenciais](https://console.cloud.google.com/apis/credentials) e cole-a em **Configurações**. As consultas usam a quota da sua chave. Guarde-a com cuidado e não a inclua em capturas ou relatos de problemas.

As atualizações desta beta são manuais. Ao receber um novo pacote, instale-o pelo Flatpak. O arquivo `SHA256SUMS` permite conferir sua integridade.

## Controles à mão

| Atalho | Ação |
| --- | --- |
| **Ctrl+Espaço** | Reproduzir ou pausar o vídeo. |
| **Ctrl+M** | Ativar ou desativar o som do vídeo. |
| **Ctrl+Alt+← / →** | Voltar ou avançar dez segundos. |
| **Ctrl+Alt+N** | Avançar para o próximo vídeo da fila. |
| **Ctrl+T** | Abrir ou fechar a moldura de redimensionamento. |
| **F11** | Alternar a tela cheia. |
| **Esc** | Sair da tela cheia, fechar painéis ou pausar um jogo, conforme o contexto. |

As teclas multimídia e os controles de reprodução do Linux também podem controlar o aplicativo, conforme o suporte do ambiente.

## Seus dados ficam com você

O aplicativo guarda preferências, biblioteca, buscas recentes e progresso no perfil local. Não há sincronização nem telemetria própria. A chave é armazenada com permissões restritas e enviada ao Google somente nas solicitações que precisam dela.

Ao buscar ou assistir, você se conecta aos serviços do YouTube/Google. A reprodução e seus dados de uso nesses serviços seguem as condições da plataforma. O pacote solicita rede, áudio, X11 e acesso gráfico à GPU, sem acesso geral aos seus arquivos pessoais; importar e exportar usa o seletor de arquivos do sistema.

## Ajude a construir a primeira beta

Experimente no seu desktop e conte o que funcionou — e o que atrapalhou. No menu da engrenagem, **Diagnóstico** mostra informações úteis sem exibir sua chave da API. Para [relatar um problema](https://github.com/orbitzone/orbitz-youtube-api-player/issues), informe sua distribuição, versão do app e os passos para reproduzi-lo.

O consumo de CPU durante vídeos ainda está sendo investigado. Os limites de reprodução, anúncios e disponibilidade de conteúdo dependem do YouTube. Consulte as [notas da beta](docs/releases/0.2.0-beta.1.md) e as [medições de desempenho](docs/performance.md) para acompanhar o estado atual.

Para compilar, testar ou contribuir com código, veja o [procedimento de preparação](docs/releases/README.md) e as [evidências de validação](docs/validation.md).

---

Desenvolvido por **Felipe Santiago / Orbitz**, como projeto comunitário independente. YouTube e Google são marcas de seus respectivos titulares; o aplicativo não é produzido nem aprovado por essas empresas.

Código sob [GPL-3.0](LICENSE). Veja também os [créditos e licenças de terceiros](THIRD_PARTY_NOTICES.md).
