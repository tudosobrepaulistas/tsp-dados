# Base de jogos do TSP (Tudo Sobre Paulista)

Esta é a base própria de jogos do tudosobrepaulista.com.br: calendário, resultados, gols, classificação e artilharia
das competições com clubes paulistas. O site lê `api/tsp.json` a cada 15 minutos (plugin TSP Jogos).
O dono é jornalista e leigo em programação: qualquer resumo para ele é curto, em português simples.

## Como a base é mantida
- `dados/competicoes.json`: competições acompanhadas e o status (ativa, verificar, aguardando, encerrada).
- `dados/times.json`: times. `slug_tsp` = endereço do clube no site (só clubes paulistas; os outros ficam "").
- `dados/jogos/<competicao>.json`: os jogos. Nunca edite à mão: use `python3 ferramentas/tsp.py ...` (veja `--help` no topo do arquivo).
- `dados/base/<competicao>.json`: classificação de partida (foto oficial numa data de corte). Jogos encerrados depois do corte somam por cima.
- Depois de qualquer mudança: `python3 ferramentas/tsp.py calcular` e `python3 ferramentas/tsp.py validar`, depois commit e push no main.

## Regras do jornalista (valem sempre)
1. **Nunca inventar** placar, gol, data, horário ou estádio. Não confirmou? Não registra.
2. **Resultado só com 2 fontes independentes** que digam o mesmo placar (a ferramenta exige 2 URLs).
   Autores e minutos dos gols: só os que as fontes confirmam; na dúvida, registre só o placar.
3. **Fontes aceitas** (matérias jornalísticas e comunicados): ge, UOL Esporte, ESPN (notícias), Lance!, Gazeta Esportiva,
   CNN Brasil, Terra, Estadão, Folha, O Globo, Agência Brasil, sites e redes oficiais dos clubes,
   notícias da CBF, da FPF e da Conmebol, e os grandes jornais regionais (Diário do Nordeste, O Povo, O Popular,
   Estado de Minas, Gazeta do Povo, Zero Hora, Correio, Jornal do Commercio e equivalentes de cada estado).
   Placar de busca do Google e de agregadores não vale como fonte. Calendário e horários: comunicados oficiais e matérias que os citam.
4. **Proibido:** copiar ou raspar bancos de dados de estatística (Sofascore, Flashscore, oGol, Transfermarkt, FotMob,
   APIs da ESPN ou de qualquer site), contornar bloqueio, login ou antirrobô. Use só WebSearch e WebFetch em páginas de notícia.
5. **Horário de Brasília** sempre (UTC-3).
6. **Jogo atrasado ou ainda rolando:** `ocorrencia ID --status atrasado` (ou em_andamento) e nova conferência em 30 min.
7. **Suspenso, adiado ou cancelado:** `ocorrencia` com `--obs` dizendo o que aconteceu (ex.: "Suspenso aos 30 do 2º tempo
   por falta de luz; CBF decide a continuação") e, se houver, `--parcial 1x0 --minuto 75`. Não conta na tabela.
8. **Fontes discordam:** não registra; nova conferência em 30 min. Depois de 3 tentativas sem acordo, deixa como está e avisa no resumo.
9. **O que acompanhar:** em competição de pontos corridos (Série A, Série B, Paulistão A2/A3/A4) registre **todos** os jogos
   da rodada (a tabela depende disso). Em mata-mata, só os jogos com clube paulista. Em fase de grupos, todos os jogos
   dos grupos que têm clube paulista.
10. Commit em português: "resultado: Santos 1x2 Palmeiras (serie_a)", "calendário: rodada 34 da Série B", etc.
