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
   - **dicas** (só quando a saída marcar `REDATOR`, regra de 08/11/2026): 1 a 4 dicas curtas e educadas para o redator
     melhorar o SEO desta e das próximas matérias, cada uma dizendo **o que** e **como**, com exemplo tirado da própria
     matéria. Ex.: "O título não tem o nome do clube no começo: 'Palmeiras renova com Belé até 2031' rende mais busca
     que 'Renovação confirmada'"; "As tags 'futebol paulista' e 'palmeiras notícias' são genéricas: use o nome do jogador
     e do adversário (Erick Belé, Vasco)"; "O 1º parágrafo não diz quando: coloque a data (domingo, 8/11)"; "Faltam
     intertítulos: divida o texto em 2 ou 3 H2 em pergunta". Tom profissional e direto, sem bronca e sem passar a mão:
     o SEO da matéria é responsabilidade do redator. O site manda as dicas para o redator no painel e por e-mail.
   - **reescrita + erros** (só `REDATOR`, regra de 14/11/2026): veja a seção "Correção do texto do redator" abaixo.
   - Tags genéricas ("futebol paulista", "X notícias", "mercado da bola", "brasileirão") não contam: o site acrescenta as
     suas tags quando a matéria tem menos de 3 tags boas.
   Regras: português do Brasil; nada de apostas; opinião só atribuída; sem datas relativas sem a data ("sábado (31/10)").
   Padrão SEO/AEO/GEO (diagnóstico de 29/10/2026):
   - meta_title em frase natural, sem o molde "Jogador no Clube: ..." (ruim: "Lucas Moura São Paulo: Atacante critica...";
     bom: "Lucas Moura critica desatenção do São Paulo após derrota").
   - resumo com dado concreto em cada tópico (placar, rodada, data, número de jogos) e com a fonte quando houver
     ("segundo o clube", "em entrevista coletiva"): é o trecho que Google e IAs mais citam.
   - resposta de cada faq com no máximo 40 palavras, começando pela informação pedida.
   - intertitulos: negrito sozinho num parágrafo NÃO conta como intertítulo; nesse caso, só proponha H2 se o texto tiver 6+
     parágrafos e posicione entre os blocos, sem repetir a frase em negrito.
4. Grave a lista em /tmp/itens.json e rode `python3 ferramentas/materias.py adicionar /tmp/itens.json` (corrija se der ERRO).
5. Commit ("editor seo: N matérias") e push no main. O site aplica em até 15 minutos.
6. Resumo de 1 linha (quantas matérias completadas).

## Reescrita imparcial de matéria de redator sobre vários clubes (13/11/2026)
Quando `pendentes` marcar **VÁRIOS CLUBES** (matéria de redator sobre sorteio, tabela, regulamento, grupos ou com 3+ clubes):
1. Reescreva o texto de forma **imparcial**, cobrindo todos os clubes envolvidos (não puxe para um só), com os
   **mesmos fatos** da matéria. Nada novo sem fonte; números, datas e nomes idênticos. Mantenha o tamanho (pelo menos 60%
   das palavras) e os parágrafos em `<p>`; intertítulos `<h2>` se ajudarem.
2. Grave no item: `"reescrita": {"html": "...", "clubes": ["slug1", "slug2", ...], "motivo": "assunto de vários clubes: texto imparcial e completo"}`.
3. O site troca o texto **no mesmo endereço** (uma matéria só, nada de matéria nova), marca os clubes, guarda o texto
   original e avisa o redator que houve ajuste por SEO. Cada matéria é reescrita uma vez só.
4. Sempre com a lista `erros` (o site recusa reescrita sem ela), como na seção abaixo.

## Títulos de CTR baixo (13/11/2026, Fase 0 e Fase 3 do plano de SEO)
Página com muita impressão e CTR baixo no Search Console (matéria, página-pilar, clube ou campeonato) ganha título e
descrição novos em `api/titulos.json` (o site põe por cima do Yoast em até 15 minutos; tirou o item, volta o antigo).
1. Título até 60 caracteres, com a busca exata no começo ("Corinthians x Coritiba: quem venceu mais, ..."), sem caça-clique.
2. Descrição até 155 caracteres, respondendo à busca com um fato da própria página (nada de número sem fonte).
3. Página-pilar de confronto: `"confronto": "time-a-x-time-b"` (nomes como no endereço /confronto/). A página vira a
   principal do confronto: ganha a caixa do próximo jogo e o endereço automático /confronto/ redireciona para ela.
4. Preencha `motivo` (impressões/cliques do período) e `desde`; 14 dias depois, compare o CTR e mantenha ou ajuste.
5. Página de jogo (/jogo/...) não entra na lista: o título dela é automático (TSP Jogos 1.8.8).

## Correção do texto do redator (14/11/2026, pedido do Thiago)
Regra: **sempre que a matéria de redator precisar, o editor corrige o texto. Mas o redator não fica isento: cada erro
dele é apontado a ele.** Vale para toda matéria marcada `REDATOR` (com ou sem VÁRIOS CLUBES).
1. Revise o texto inteiro. Precisa de correção quando houver: erro de português (concordância, crase, acento, pontuação,
   digitação); data relativa sem a data ("nesta sexta-feira" → "nesta sexta-feira (13/11)", só quando a data de
   publicação deixa a data certa); lide sem quem/o quê/quando; nome, número ou informação que se contradiz dentro da própria
   matéria; frase confusa ou repetida; parágrafos colados com `<br><br>` num bloco só (`PROBLEMAS NO TEXTO` na saída de
   `pendentes`: o site não consegue pôr H2 nem resumo direito); negrito usado como intertítulo (vira `<h2>` de verdade,
   de preferência em pergunta); citação sem aspas ou sem quem disse.
2. Se precisar, grave `"reescrita": {"html": ..., "clubes": [...], "motivo": "frase curta do que foi corrigido"}` com o
   **mesmo texto corrigido**: mesmos fatos, números, nomes, citações (palavra por palavra) e ordem; só `<p>`, `<h2>`,
   `<ul><li>`, `<strong>`, `<em>` e os links/imagens que já existiam. Nada de fato novo, nada de opinião. Pelo menos 60%
   das palavras do original. Se tiver H2 na reescrita, não mande `intertitulos`.
3. Grave **sempre** `"erros"` quando houver erro (com ou sem reescrita; até 8): cada item diz o erro com o trecho do
   redator e a forma certa. Ex.: "Data relativa sem a data: 'Nesta sexta-feira, um advogado...' → 'Nesta sexta-feira
   (13/11), um advogado...'"; "Texto todo num parágrafo só, separado por <br><br>: use um parágrafo por ideia
   (Enter, não Shift+Enter)"; "Concordância: 'os jogadores foi' → 'os jogadores foram'". Tom profissional, direto e
   respeitoso: aponta o erro, não ofende. Não invente erro: na dúvida, não aponte. Confira o texto completo (listas
   aparecem como `LISTA:`) antes de dizer que falta algo.
4. Erro só de SEO (título fraco, tags genéricas) vai em `dicas`; erro de texto vai em `erros`. Matéria sem erro: sem
   `reescrita` e sem `erros`.
5. O site troca o texto no mesmo endereço, guarda o original nas revisões, mostra os erros na caixa da matéria e manda
   ao redator "Matéria corrigida" (ou "Erros na matéria", sem reescrita) com a lista e o lembrete de que a revisão é dele.
