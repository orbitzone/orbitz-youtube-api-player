# Ponteiro e medição inicial — 02/11/2026

Baseline amostrado por 3 segundos em /proc, antes da atualização. CPU expressa como percentual de um núcleo. Processo WebKit encontrado pelo nome; essa amostra não identifica codec, qualidade do vídeo nem atribui uso exclusivamente ao wrapper. Não há comparação controlada de antes/depois e não se afirma ganho percentual.

Correções: saída completa da janela tem prioridade sobre painéis abertos; ações e curtidas em card único compacto. Observador nativo deduplica movimentos pela região (body/controles/fora), em vez de enviar todas as coordenadas enquanto o mouse se move. Teste unitário verifica 40 movimentos na mesma região sem novos despachos e notificações nas fronteiras.

Suíte Python/JS aprovada. GTK/WebKit confirmou saída com busca/menu/configurações abertos e preservou testes de reversão, recorte e pixels após transição.
