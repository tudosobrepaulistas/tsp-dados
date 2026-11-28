# Base de jogos do TSP (Tudo Sobre Paulista)

Esta é a base própria de jogos do tudosobrepaulista.com.br: calendário, resultados, gols, classificação e artilharia
das competições com clubes paulistas. O site lê `api/tsp.json` a cada 15 minutos (plugin TSP Jogos).
O dono é jornalista e leigo em programação: qualquer resumo para ele é curto, em português simples.

**Começo de conversa nova:** leia `diretrizes/estado-atual.md` (o que foi feito, versões, tarefas agendadas e pendências).

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
    1 matéria que relata o anúncio oficial). Transfermarkt: só referência. **oGol (15/11/2026, liberado pelo Thiago):** vale como fonte dos números do card
    (jogos, minutos, gols, assistências, clubes de 2026 e nascimento), lendo a página de cada jogador, sem raspagem em massa.
    Contratação e saída continuam exigindo as fontes de sempre. Escudos de clubes de fora do site: `dados/escudos_extra.json`.
14. **Pessoas (22/11/2026):** página e matéria de jogador, treinador, comissão e dirigente seguem `diretrizes/pessoas.md`
    (SEO com H1/H2/H3 e entidades ligadas; AEO com resposta de até 55 palavras logo abaixo de cada pergunta; GEO com datas,
    métricas e tabelas; dado que falta = "Em atualização"). Sofascore, oGol, Transfermarkt e Soccerway são só referência de formato.
15. **Confrontos (25/11/2026):** todo jogo futuro de competição com clube paulista (mesmo entre dois clubes de fora) tem a página
    /confronto/ completa **3 dias antes**, respondendo TODAS as intenções de busca (data, hora, local, onde assistir, árbitro,
    ingressos, tabela, momento, estatísticas, artilheiros, técnicos, escalações, desfalques, retrospecto geral com 2 fontes,
    maiores vitórias, jogos marcantes). Como fazer: `diretrizes/confrontos.md`. Nada de apostas.
16. **Recorte, não total (25/11/2026, regra do Thiago):** a base ainda está recebendo as rodadas anteriores. Todo número
    calculado pela base (campanha, artilheiros, últimos jogos, aproveitamento com/sem jogador, técnico, confronto) diz
    explicitamente que é um recorte: "nos últimos 12 jogos registrados pelo TSP (de 05/10 a 22/11)". Nunca "na temporada"
    nem "na carreira" para número da base. Vale para páginas (TSP Jogos 1.9.2 / tema 1.9.7), matérias da Máquina (raio-x,
    pré e pós-jogo) e cards do Mercado da Bola. Número oficial (tabela da CBF/FPF) ou de matéria com fonte não é recorte.
17. **Paulistas pelo mundo (28/11/2026, regra do Thiago):** monitorar 20 atletas por dia que saíram de clubes paulistas
    (todas as divisões) de 2023 a 2027 para o exterior; é a base para atualizar clube atual e liga. Só vai ao site quem
    tem figurinha E dados (clube com 2 fontes, números da temporada e carreira). Como fazer: `diretrizes/pelo-mundo.md`.
