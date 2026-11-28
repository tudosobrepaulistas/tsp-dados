# Estado atual do TSP (passa-bastão de 28/11/2026, 1h)

Leia isto no começo de uma conversa nova, junto com CLAUDE.md. Atualize ao fim de cada conversa longa.

## Versões no ar
- Tema tsp-nova-era 1.14.0 · plugin tsp-jogos 1.9.6 (ver atualizacoes/versoes.json; outra sessão também publica: sempre confira a versão antes e trabalhe em cima do zip mais novo).
- Instalação quando o atualizador demora: wp-admin → enviar o zip (Chrome do Thiago, já logado) → "Substituir instalado pelo enviado".
- Dados do feminino: depois de mudar dados/painel_feminino.json, `tsp.py calcular` e, se tiver pressa, Ferramentas → TSP · Jogos → "Ler a base agora".

## O que foi feito nesta conversa (27-28/11)
- Home: cobertura especial (api/especial.json, inc/especial.php): 6 matérias (2 grandes + 4) alternando clube e rival, só o jogo da fase atual (CSS mostra só "Final"). Ativa até 29/11 6h. Para outro jogo: editar api/especial.json.
- Clubes de fora acompanhados (página /times/<slug>/, fora dos blocos paulistas): tsp_clubes_fora() em inc/especial.php. Hoje: Estudiantes (escudo em api/escudos/estudiantes.png). Matéria com o nome no título ganha a marcação sozinha.
- Menu "Internacional" por continente (inc/internacional.php e diretrizes/internacional.md): 7 ligas + "Outras ligas" por continente; matérias internacionais fora da home.
- Menu do computador em duas linhas; simulador entre os grandes e Mirassol/Bragantino; faixa discreta de grupos de WhatsApp em cada bloco da home.
- Feminino com abas (Copa Paulista Feminina, Paulistão Feminino com chave completa, Copinha F com grupos e jogos).
- Tanabi: elenco 2027 com 19 nomes (dados/mercado.json). Figurinhas NÃO feitas: fotos de referência em ~/Downloads/tsp-figurinhas/tanabi/ no Mac do Thiago (precisa do Mac ligado e ChatGPT logado no Chrome). Petterson Martins sem figurinha (arte do clube marcada como "Conteúdo de IA").

## Conversa de 28/11 (madrugada): Radar Paulistas pelo mundo
- Tema 1.14.0 publicado em atualizacoes/ (versoes.json já aponta). Em 28/11 1h20 ainda NÃO estava instalado: o
  wp-admin e o ChatGPT estavam deslogados no Chrome do Thiago (e no navegador do app). Depois que ele entrar:
  wp-admin/update-core.php?force-check=1 → atualizar TSP Nova Era (ou enviar o zip). Conferir /paulistas-pelo-mundo/.
- Base: dados/pelo_mundo.json (7 jogadores, 6 países), ferramentas/pelo_mundo.py, diretrizes/pelo-mundo.md.
- As 2 tarefas agendadas do Radar (diária 7h37 e semanal domingo 15h43) foram BLOQUEADAS pela checagem automática ao
  criar: os textos estão em diretrizes/pelo-mundo.md; criar quando o Thiago autorizar.
- Figurinhas do Tanabi: não feitas (ChatGPT deslogado; pasta ~/Downloads/tsp-figurinhas/tanabi/ ainda sem acesso).

## Tarefas agendadas criadas nesta conversa
- trig_01A2VcAh3xFuCWVEwEviRxAB: 3 matérias do Estudiantes ("duelo de narrativas"), 28/11 0h37 (única).
- trig_011QJw23FB2uXr1KTa2MC59v: dia da final, 2 Palmeiras + 1 Estudiantes, 28/11 5h41 (única).
- trig_016n5CESaHbBetteoRBpEdmR: pós-jogo da final (placar com 2 fontes + 6 de repercussão), 28/11 19h41 (única).
- trig_01EL4G7n4SH5X3wao1wP1NaM: Copinha F, resultados nos grupos, todo dia 23h53 até 12/12 (apagar depois).
- Anteriores e que seguem: Confrontos 72h, Guia da Copinha 2027, Mercado da Bola, 4 grandes, temporada, intenções, ranking de clubes etc. (list_triggers).

## Pendências (em ordem)
1. Radar "Paulistas pelo mundo": FEITO em 28/11 (tema 1.14.0, diretrizes/pelo-mundo.md, 7 jogadores). Falta crescer a base (rotina agendada) e conferir no ar.
2. Máquina escrever matéria internacional (hoje exige clube paulista): só depois do Radar.
3. Figurinhas do Tanabi (18) no ChatGPT do Chrome do Thiago (precisa: Thiago logado no ChatGPT e liberar a pasta ~/Downloads/tsp-figurinhas/tanabi/).
4. Desligar o especial depois da final (ate já é 29/11 6h; nada a fazer) e voltar a manchete normal.
5. Antigas: 21 matérias em espera sem foto; 2 rascunhos velhos da estreia da Copinha feminina (m0a93e83ce0a8, m394d142fe7fd) não devem sair; divergência Sub-17 fem SP (virada x empate) antes de liberar ma020dad7e5f8 e md1dc3306767e; páginas /sobre/ e /expediente/ (faltam foto, bio e redatores); futebol brasileiro de outros estados no início dos estaduais.
