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
9. **Temporada completa (09/11/2026):** além do que está abaixo, a base guarda TODOS os jogos oficiais da temporada dos
   times das Séries A e B (estaduais, Nordestão, Copa do Brasil, continentais), com escalações, para as páginas de time e
   jogador. Regras de fonte iguais (2 fontes no placar). Como fazer: `diretrizes/temporada.md`.
   **O que acompanhar:** em competição de pontos corridos (Série A, Série B, Paulistão A2/A3/A4) registre **todos** os jogos
   da rodada (a tabela depende disso). Em mata-mata, só os jogos com clube paulista. Em fase de grupos, todos os jogos
   dos grupos que têm clube paulista.
10. Commit em português: "resultado: Santos 1x2 Palmeiras (serie_a)", "calendário: rodada 34 da Série B", etc.
11. **Cotas diárias por bloco (12/11/2026):** Mirassol e Bragantino 2 matérias por dia cada (12h e 18h), Série B 2 por clube,
    feminino 8, A1 8, A2 8, A3 8, A4 8, sem divisão 8, base 4, contando redação + Máquina. **Clubes prioritários (14/11/2026):** Guarani, Ponte Preta, XV de Piracicaba, Portuguesa,
    Bragantino, Novorizontino, Mirassol, Botafogo-SP e Comercial (RP) têm no mínimo 2 matérias por dia cada, em qualquer divisão e de qualquer autor. Se a redação não fizer, a Máquina completa:
    `python3 ferramentas/maquina.py cotas` e `diretrizes/cotas.md`.
12. **Nota das matérias (14/11/2026):** todo dia às 23h59 o site dá nota de 0 a 10 a cada matéria de redator (veracidade, lide,
    clareza, profundidade, português, SEO, AEO, GEO), com ranking e relatório por redator. Roda no site, sem custo: `diretrizes/notas.md`.
    Os apontamentos do editor-chefe derrubam a nota da matéria: aponte com cuidado (só com 2 fontes).
12. **Texto do redator (14/11/2026):** quando a matéria de redator precisar, o Editor SEO corrige o texto no mesmo endereço
    e SEMPRE aponta ao redator os erros que ele cometeu (campo `erros`): a correção não tira a responsabilidade dele.
    Como fazer: `diretrizes/editor-seo.md`, seção "Correção do texto do redator".
13. **Mercado da Bola 2027 (14/11/2026):** contratações, saídas e renovações dos clubes paulistas, 1 vez por dia, com
    `python3 ferramentas/mercado.py` (`diretrizes/mercado.md`). Só negócio fechado (oficial ou acertado), 2 fontes (clube pequeno:
    1 matéria que relata o anúncio oficial). oGol e Transfermarkt: liberados pelo Thiago só como referência para descobrir e conferir;
    não valem como fonte e nada é copiado deles.
