# Editor SEO do TSP (roda de 2 em 2 horas, das 7h às 23h)

Objetivo: toda matéria publicada no tudosobrepaulista.com.br, escrita por jornalista ou pela Máquina, sai com o mesmo padrão
de SEO, AEO e GEO, sem trabalho extra da redação. O site só completa o que estiver vazio e nunca reescreve o texto.

1. add_repo (owner "tudosobrepaulistas", repo "tsp-dados", access "push"), clone, leia CLAUDE.md.
2. `python3 ferramentas/materias.py pendentes --horas 3` (a 1ª execução do dia usa `--horas 10`). Sem pendentes: termine sem commit.
3. Para cada matéria, a partir SÓ do texto dela (nada de fora, nada inventado), monte um item:
   - **resumo**: 3 a 5 tópicos curtos com os fatos principais (quem, o quê, quando, número/placar), datas absolutas.
   - **faq**: 3 a 5 perguntas que o torcedor faria no Google sobre o assunto (intenção de busca: "quando é o próximo jogo do X",
     "onde assistir X x Y", "quanto o X pagou", "quem é ..."), cada uma terminando com "?", e resposta de 1 a 2 frases
     que esteja no texto. Se o texto não responde, não crie a pergunta.
   - **meta_title**: até 60 caracteres, palavra-chave no começo, sem caixa alta, sem caça-clique.
   - **meta_desc**: até 155 caracteres, responde à busca e cita o clube.
   - **foco**: a palavra-chave principal (ex.: "próximo jogo do Palmeiras", "Corinthians indenização").
   - **tags**: 3 a 6 (clube, adversário, competição, jogador ou técnico citados).
   - **intertitulos**: só se a matéria tiver 6 ou mais parágrafos e NÃO tiver intertítulos: 1 a 3 H2 em forma de pergunta
     ("O que disse o técnico?", "Quando é o próximo jogo?"), indicando o número do parágrafo ANTES do qual entram (p >= 3).
   Regras: português do Brasil; nada de apostas; opinião só atribuída; sem datas relativas sem a data ("sábado (31/10)").
4. Grave a lista em /tmp/itens.json e rode `python3 ferramentas/materias.py adicionar /tmp/itens.json` (corrija se der ERRO).
5. Commit ("editor seo: N matérias") e push no main. O site aplica em até 15 minutos.
6. Resumo de 1 linha (quantas matérias completadas).
