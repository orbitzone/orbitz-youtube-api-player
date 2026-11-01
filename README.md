# YouTube API Player

### YouTube, em uma janela só. E um pequeno alien para fazer companhia.

Pesquise vídeos, Shorts, transmissões ao vivo e podcasts e assista pelo player oficial do YouTube. Quando não houver vídeo na tela, o Orbitz Runner espera por você: um jogo arcade espacial com um ET, obstáculos, tiros automáticos e recorde local.

**Leve, direto e independente do GNOME Shell.** Feito por Felipe Santiago / orbitzone como projeto comunitário, sem afiliação com Google ou YouTube.

> A versão atual é uma prévia para Linux x86_64. Ela ainda não está no Flathub e não recebe atualizações automáticas.

## O que você encontra

- **Busca do YouTube:** vídeos e recomendações recentes em português. A busca usa sua própria chave da YouTube Data API v3.
- **Shorts e lives:** filtros dedicados para encontrar vídeos curtos e transmissões ao vivo ativas.
- **Podcasts:** busca orientada a episódios de podcast.
- **Filtros compactos:** em janelas pequenas, os quatro filtros exibem apenas ícones; os nomes permanecem nos tooltips e na acessibilidade. Em janelas maiores, ícones e nomes aparecem juntos.
- **Player oficial:** reproduza vídeos incorporados, use tela cheia e copie o link do vídeo selecionado.
- **Sempre acima:** no menu da engrenagem, ative “Sempre acima das outras janelas” para manter o aplicativo em primeiro plano também após fechar e abrir o aplicativo.
- **Controles automáticos:** no menu da engrenagem, ative “Ocultar controles automaticamente”. Ao sair da área do vídeo/jogo ou da janela, os controles somem após 2 segundos; ao voltar, reaparecem após meio segundo. Entradas e saídas cancelam o prazo anterior. A opção e seus delays ficam salvos; Ctrl+H fica desabilitado enquanto ela estiver ativa. Menus, busca e configurações mantêm os controles disponíveis.
- **Só o vídeo:** na tela do jogo ou durante a reprodução, com o modo automático desativado, pressione **Ctrl+H** para ocultar a barra de título, a busca e o rodapé. Pressione **Ctrl+H** novamente para restaurar os controles. A área do jogo ou do vídeo mantém suas dimensões ao alternar; só a área das barras é retirada e restaurada. O mouse não altera esse modo; o menu da engrenagem mostra o atalho e abre **Configurações**.
- **Orbitz Runner:** um mini game que começa só quando você aperta Espaço ou clica. Pule obstáculos, veja os cactos explodirem e tente superar seu recorde.
- **Sua janela, do seu jeito:** o aplicativo lembra a última posição e o tamanho da janela ao fechar e os restaura ao abrir. Se um monitor for removido, a janela volta para uma área visível.
- **Português e inglês:** escolha Português (Brasil) ou English (United States) nas configurações.
- **Seus dados no seu computador:** chave, preferências, cache e recorde ficam no perfil local do aplicativo; não há sincronização nem telemetria própria.

## Instalar no Linux

O pacote disponível é um Flatpak x86_64. É necessário usar X11 ou uma sessão Wayland com XWayland, além de conexão à internet para os serviços do YouTube. O aplicativo usa o runtime GNOME 49 e não exige uma versão específica do GNOME Shell.

1. Instale o [Flatpak para sua distribuição](https://flatpak.org/setup/).
2. Baixe o arquivo `orbitz-youtube-desktop-x86_64.flatpak` na [prévia v0.1.0](https://github.com/orbitzone/orbitz-youtube-wrapper/releases/tag/v0.1.0). O nome do arquivo foi mantido desde a publicação inicial.
3. No terminal, entre na pasta do download e instale:

```sh
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user ./orbitz-youtube-desktop-x86_64.flatpak
flatpak run io.orbitz.YouTubeDesktop
```

Depois, você também pode abrir **YouTube API Player** pelo menu de aplicativos. Para atualizar, instale uma versão mais recente quando ela for publicada. O arquivo `SHA256SUMS` da release permite conferir a integridade do download.

## Começar a usar

No menu da engrenagem, abra **Configurações** e cole uma chave pessoal da YouTube Data API v3 para habilitar as buscas. A página de [credenciais do Google Cloud](https://console.cloud.google.com/apis/credentials) permite criar a chave; o projeto também precisa ter a YouTube Data API v3 habilitada e quota disponível.

A chave é guardada localmente no diretório privado do aplicativo, com permissão restrita. O app também consegue ler uma chave salva por uma instalação anterior do Orbitz YouTube Desktop; ao salvar uma nova, ela fica no local atual do aplicativo. Não compartilhe arquivos de configuração que contenham sua chave.

Para assistir a um vídeo sem configurar a API, cole um link do YouTube na busca. Você também pode iniciar o Orbitz Runner na tela inicial usando **Espaço** ou clicando na área do jogo.

## Biblioteca, fila e continuar assistindo

O botão **Biblioteca** (ícone de livros), no cabeçalho, abre um painel compacto com **Favoritos**, **Assistir depois** e **Fila**, sem escurecer a reprodução. Use a estrela do vídeo atual para favoritar/desfavoritar; o menu **⋮** reúne Assistir depois e outras ações. Miniaturas, contadores e títulos em até duas linhas mantêm as listas compactas. O botão **+** ao lado de cada resultado adiciona o vídeo à fila sem interromper a reprodução atual.

Na fila, abra o menu **⋮** de um item para movê-lo ou removê-lo e **Próximo vídeo** para avançar. Ao terminar o vídeo atual, o aplicativo reproduz o próximo item da fila. A fila também é preservada ao fechar; a abertura não inicia reprodução automaticamente.

Na próxima abertura, **Continuar assistindo** oferece retomar o último vídeo no ponto salvo. O progresso é registrado a cada 15 segundos durante reprodução, ao pausar/trocar de vídeo e ao fechar normalmente. O último vídeo é guardado desde a seleção e sempre é oferecido na próxima abertura, mesmo se foi pausado, interrompido com stop, concluído ou reproduzido por pouco tempo. Vídeos concluídos ou em stop voltam ao início. Lives, rádios e mídia sem posição válida são reabertas sem buscar um ponto antigo; o ponto disponível depende do YouTube. **Agora não** oculta a oferta apenas naquela abertura, sem apagar o último vídeo. A oferta fica protegida da ocultação automática até você escolher continuar ou dispensá-la.

No rodapé do painel, **Gerenciar → Importar biblioteca / Exportar biblioteca** usam o seletor de arquivos do sistema. O JSON contém apenas Favoritos e Assistir depois; não inclui chave da API, preferências, fila ou progresso. Importar mescla as listas e elimina duplicações por vídeo/lista. São permitidos até 1.000 itens por lista e 200 na fila.

As preferências **Sempre acima** e **Ocultar controles automaticamente** são lembradas entre aberturas. Em **Configurações**, ajuste os prazos de ocultar/mostrar entre 0,1 e 10 segundos; os valores iniciais são 2 e 0,5 segundo.

## Atalhos e controles de mídia

- **Ctrl+Espaço:** reproduzir/pausar.
- **Ctrl+Alt+← / Ctrl+Alt+→:** voltar/avançar dez segundos.
- **Ctrl+Alt+N:** próximo vídeo da fila.
- **Ctrl+M:** ativar/desativar som.
- **Ctrl+H:** mostrar/ocultar controles no modo manual.
- **F11 / Esc:** entrar/sair da tela cheia.

O menu da engrenagem também apresenta **Atalhos de teclado**. A integração MPRIS permite usar as teclas multimídia e os controles de reprodução do ambiente Linux, conforme o suporte/configuração do sistema.

## Diagnóstico

No menu da engrenagem, **Diagnóstico** mostra versões do aplicativo/runtime, acesso gráfico e disponibilidade de decodificadores acelerados. A consulta acontece apenas ao abrir o painel; um decoder disponível não significa que o vídeo atual esteja usando-o. Não exibe sua chave da API.

Preferências, listas, fila e último progresso ficam em `orbitz-youtube-wrapper/library.sqlite3` no diretório XDG de configuração privado do aplicativo. Não há login adicional, sincronização ou histórico completo de navegação.

## Como funcionam os filtros

O YouTube não disponibiliza um filtro oficial de pesquisa para todas essas categorias. Por isso, alguns resultados são aproximações:

- **Shorts:** usa o filtro oficial de vídeos com menos de quatro minutos. Isso pode incluir vídeos que não são classificados pelo YouTube como Shorts.
- **Ao vivo:** procura transmissões que estejam ativas.
- **Podcasts:** acrescenta o termo “podcast” à busca; os resultados podem incluir outros tipos de vídeo.

Com a busca vazia, as quatro abas mostram sugestões de até 20 vídeos. Elas combinam os interesses informados em **Configurações → Recomendações para você**, buscas recentes da própria categoria e, quando necessário, buscas de outras abas. Se ainda não houver interesses nem buscas, seus favoritos ajudam a iniciar as sugestões; sem esses sinais, são exibidas sugestões gerais da categoria. O idioma da interface orienta idioma/região das solicitações. Uma consulta digitada só é enviada quando você inicia a busca ou troca de filtro com o termo preenchido. Ao limpar o campo, as sugestões da aba voltam automaticamente. Interesses e temas de até 30 buscas dos últimos 30 dias são guardados localmente; os temas selecionados são enviados à API oficial para obter sugestões. Você pode desativar o uso de buscas recentes e limpá-las nas configurações, mantendo favoritos e interesses. Não há acesso ao histórico da sua conta do YouTube. As sugestões têm cache separado por categoria e perfil: até seis horas, ou cinco minutos para lives/listas vazias, renovado somente ao solicitar sugestões; não há atualização em segundo plano durante o vídeo. Os limites de uso e a quota seguem as regras do Google Cloud para a sua chave.

## Sobre o player e os vídeos

A YouTube Data API encontra vídeos e fornece seus identificadores. A reprodução acontece no player incorporado oficial, carregado pelo YouTube. Anúncios, disponibilidade, restrições, autenticação e reprodução são controlados pelo YouTube e pelos responsáveis pelos vídeos. A chave da API não remove anúncios nem dá acesso ao arquivo de vídeo.

## Privacidade e permissões

O aplicativo não envia telemetria própria nem sincroniza seus dados. Consultas e links são enviados ao YouTube/Google quando você usa esses serviços; a chave configurada é enviada à API oficial nas solicitações de busca. Cache, idioma, chave e recorde do jogo são armazenados localmente no perfil Flatpak do aplicativo.

O pacote solicita rede, X11, áudio e acesso gráfico à GPU (DRI) para reproduzir vídeos com aceleração quando disponível, sem acesso geral aos seus arquivos pessoais. Em Wayland, é necessário XWayland. A posição da janela, tela cheia, áudio e abertura de links externos também dependem do ambiente Linux instalado.

## Compilar a partir do código

Para gerar e instalar uma versão Flatpak localmente, instale Flatpak, `flatpak-builder`, Node.js e configure o remoto Flathub:

```sh
flatpak-builder --user --install-deps-from=flathub --assumeyes --repo=repo build-dir packaging/io.orbitz.YouTubeDesktop.json
flatpak build-bundle repo orbitz-youtube-wrapper-x86_64.flatpak io.orbitz.YouTubeDesktop --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo
```

Para executar diretamente numa sessão X11/XWayland, são necessários Python 3, GTK 3, WebKitGTK 4.1, PyGObject, SQLite e Node.js:

```sh
python3 app/youtube-wrapper.py
```

Os testes são executados sem chave real e sem chamadas à API:

```sh
make test
```

Consulte [origem e validação](docs/validation.md) para conhecer o histórico do pacote e as verificações disponíveis.

## Licença e independência

O projeto é distribuído sob a licença [GPL-3.0](LICENSE). Ícones dos filtros: Google Material Symbols (Apache-2.0) e Shorts via Simple Icons (CC0-1.0); veja [créditos de terceiros](THIRD_PARTY_NOTICES.md). YouTube e Google são marcas de seus respectivos titulares. Este aplicativo comunitário não é produzido, aprovado nem mantido pelo Google.

Para detalhes das medições de CPU e aceleração gráfica, consulte [desempenho de vídeo](docs/performance.md).
