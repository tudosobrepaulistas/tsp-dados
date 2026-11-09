# "Neste dia" — jogos históricos em datas redondas (1 matéria por dia)

Pedido do Thiago (08/11/2026): todo dia, 1 matéria sobre um jogo de clube paulista que aconteceu **neste mesmo dia e mês**
há **5, 10, 15, 20, 25, 30... anos** (datas com final 0 ou 5). Vale qualquer divisão: Série A, A1, A2, A3, A4, Segunda
Divisão, clubes sem divisão, feminino. Ex.: em 09/11/2026, um jogo de 09/11/1996 (30 anos), 09/11/2006 (20 anos)...

## Passo a passo
1. Liste os anos possíveis (hoje menos 5, 10, 15... até 60 anos).
2. Procure com WebSearch jogos de clubes paulistas nessas datas exatas: decisões, acessos, títulos, goleadas, estreias de
   ídolos, clássicos. Bons lugares: páginas da Wikipédia das competições daquele ano (Campeonato Paulista, Série A2,
   Brasileirão, Copa do Brasil), sites oficiais dos clubes (área de história), FPF, CBF, matérias de jornais que relembram
   o jogo ("há 20 anos..."). **Proibido**: oGol, Sofascore, Flashscore, Transfermarkt, FotMob e afins.
3. Só escreva se **data, placar e adversário** estiverem confirmados (2 fontes de preferência; 1 fonte confiável no mínimo).
   Autor de gol, público e escalação só se a fonte trouxer. Nada de suposição.
4. Prefira jogos marcantes e varie: um dia time grande, outro do interior; não repita clube na mesma semana.
5. Título com a data redonda e o clube: "Há 30 anos, o Rio Branco vencia o Paulista e subia para a elite" (o nome do clube
   no título). Texto: o que estava em jogo, como foi, o que veio depois, onde estão os personagens hoje (só com fonte).
6. JSON como em `diretrizes/maquina.md`, com `"tipo": "historia"` e
   `"efemeride": {"data": "AAAA-MM-DD do jogo", "anos": 30}`. Foto: da época (Wikimedia/Commons livre, acervo do clube
   com crédito) ou do estádio/clube hoje (dizendo isso no `foto.mostra`). Fora da regra "só notícia" e do limite de evergreen.
7. `python3 ferramentas/maquina.py adicionar /tmp/neste-dia.json`, commit ("neste dia: <clube> - <assunto>") e push,
   depois `python3 ferramentas/maquina.py avisar-site`. Sem jogo confirmado: não publique e diga isso no resumo.
