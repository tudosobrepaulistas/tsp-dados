# Sugestões de pauta do TSP (8h, 12h e 18h)

Objetivo: entregar a cada redator ideias de matéria sobre os times que ele cobre, para ele apurar e escrever.
Pauta é sugestão, não matéria pronta: nada de copiar texto de ninguém.

1. add_repo (owner "tudosobrepaulistas", repo "tsp-dados", access "push"), clone, leia CLAUDE.md.
2. `python3 ferramentas/pautas.py clubes`. Sem clubes: termine sem commit.
3. Para cada clube da lista, faça 1 WebSearch (modo standard) com o nome do clube + "notícias" (ou o assunto do dia),
   olhando só o que saiu nas últimas ~12 horas em fontes jornalísticas aceitas (lista do CLAUDE.md: ge, UOL, ESPN notícias,
   Lance!, Gazeta Esportiva, CNN, Terra, Estadão, Folha, O Globo, Agência Brasil, sites e redes oficiais dos clubes, CBF, FPF).
   Clubes menores: inclua o site oficial do clube e jornais da cidade. Se precisar confirmar algo, WebFetch na matéria.
4. Monte de 1 a 3 pautas por clube (as melhores), sem repetir as "já sugeridas" da lista:
   - **titulo**: a ideia em uma linha ("Abel deve poupar titulares contra o Santos; veja quem pode entrar").
   - **resumo**: 1 a 3 frases com o fato (o que, quem, quando) e por que interessa ao torcedor.
   - **angulo** (opcional): como o TSP pode fazer diferente (dados da Base TSP, histórico do confronto, serviço "onde assistir").
   - **fontes**: 1 a 3 links das matérias onde o redator confere a informação.
   Tipos que funcionam: escalação/desfalques do próximo jogo, coletiva, mercado (contratação/saída com fonte), lesão,
   bastidores oficiais, base/feminino com destaque, serviço (ingressos, horário, onde assistir), marcos e curiosidades.
   Nada de boato sem fonte, nada de aposta, nada de bancos de estatística (Sofascore, oGol, Transfermarkt...).
   Clube sem notícia relevante: não invente pauta, pule.
5. Grave a lista em /tmp/pautas.json e rode `python3 ferramentas/pautas.py adicionar /tmp/pautas.json` (corrija se der ERRO).
6. Commit ("pautas: N sugestões para M clubes") e push no main. O site mostra no painel em até 15 minutos.
7. Resumo de 1 linha.
