# Completar as rodadas passadas das Séries A e B (15/11/2026)

Objetivo: a base do TSP com **todos os jogos** das Séries A e B 2026, para retrospecto, "último jogo", últimos 5,
mandante/visitante, previsões e artilharia certos. Sem API paga: só WebSearch e WebFetch em matérias aceitas (CLAUDE.md).
A classificação NÃO muda (ela vem da foto oficial de 27/10 + jogos depois do corte); só ganham as estatísticas.

## Cada execução (até 4 rodadas, economia de limite)
1. `python3 ferramentas/tsp.py rodadas-faltando` mostra as rodadas incompletas (a mais antiga primeiro). Pegue até 4.
2. Para cada rodada, **1 busca**: "resultados da Nª rodada da Série A 2026" (ou Série B). Procure 2 matérias de sites
   aceitos que tragam a **lista da rodada inteira** (Diário do Nordeste, O Povo, Gazeta Esportiva, Lance!, ge, UOL, Terra,
   Estadão, jornais regionais). 90min, netflu, sites de torcida, ESPN placar/"match", valorfinal e agregadores NÃO valem.
   Use o resumo da busca; só faça WebFetch quando o resumo não mostrar os 10 placares.
3. Jogo que só uma das matérias traz: busque aquele jogo (1 busca) e use uma matéria do jogo como 2ª fonte.
   Fontes discordam (ex.: 4x0 numa, 3x0 noutra): só grava com 2 que concordem; senão pule e anote no resumo.
4. Data: a que as matérias dizem (dia). Hora: só se uma matéria aceita disser; jogo com mais de 75 dias pode ficar sem
   hora (`"data": "2026-01-28"`). Estádio/cidade: só se a matéria disser.
5. Gols: só se as matérias trouxerem autor (`"gols": "casa|Danilo||normal; casa|Artur||normal"`). Na dúvida, só o placar.
6. Monte /tmp/rodada.json (formato no topo de `ferramentas/tsp.py`, comando `rodada-passada`; use as chaves de
   `dados/times.json` em "casa"/"fora") e rode `python3 ferramentas/tsp.py rodada-passada --json /tmp/rodada.json`.
   Se der ERRO, nada foi gravado: corrija e rode de novo.
7. Depois das rodadas: `python3 ferramentas/tsp.py calcular && python3 ferramentas/tsp.py validar`, commit
   ("temporada: Série A rodadas 2 a 5") e push no main. Resumo de 1 linha: rodadas completas e jogos pulados.

## Artilharia oficial (uma vez por competição, depois de cada rodada fechada se quiser atualizar)
A artilharia calculada só pelos jogos fica incompleta enquanto faltarem rodadas. Foto oficial, igual à classificação:
`dados/base/artilharia_serie_a.json` = `{"corte": "2026-11-10T23:59:00-03:00", "fonte": "URL1 | URL2",
"lista": [{"jogador": "Fulano", "time": "chave-do-time", "gols": 12}, ...]}` com a lista de 2 matérias aceitas que
concordem (ex.: "artilheiros do Brasileirão após a 36ª rodada"). Gols de jogos depois do corte somam por cima.
