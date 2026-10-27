# tsp-dados

Base própria de jogos do [Tudo Sobre Paulista](https://tudosobrepaulista.com.br): calendário, resultados, gols,
classificação e artilharia das competições com clubes paulistas.

- `api/tsp.json` — arquivo que o site lê (gerado por `ferramentas/tsp.py calcular`).
- `dados/` — a base (jogos, times, competições, classificação de partida).
- `diretrizes/` — como a Máquina de Resultados trabalha (planejamento às 2h e conferências 2h10 após cada jogo).

Cada resultado é conferido em pelo menos duas fontes jornalísticas, registradas junto com o jogo.
