# Páginas e matérias de pessoas: jogador, treinador, comissão técnica e dirigente (22/11/2026, pedido do Thiago)

Meta: ser o guia mais completo, mais limpo e mais útil do futebol paulista, melhor que Sofascore, oGol, Transfermarkt e Soccerway.
Vale para a página fixa da pessoa (/jogador/..., /treinador/..., /comissao-tecnica/...) e para toda matéria de perfil.
Esses sites são **referência de formato**: ver o que eles mostram e fazer melhor. **Nunca copiar dado deles**. O oGol vale só para os
números do card de jogador (CLAUDE.md, regra 13).

## Formatos (o Thiago escolhe qual gerar)
- **Artigo pilar:** perfil completo e permanente da pessoa. É a base da página fixa.
- **Notícia de jogo:** atuação da pessoa num jogo específico.
- **Perfil tático:** como joga ou como faz o time jogar (esquema, ideias, números).
- **FAQ:** só perguntas e respostas, para busca por voz e para IA.

## Regras obrigatórias
1. **SEO**
   - Um H1 com o nome e a informação principal. H2 em forma de pergunta natural; H3 para os detalhes.
   - Semântica rica: ligar as entidades certas (pessoa ↔ clubes ↔ competições ↔ temporadas ↔ prêmios), com link interno para a página de cada clube, campeonato e jogo do TSP.
   - Nome completo e apelido iguais em todo o site.
2. **AEO**
   - Logo abaixo de cada H2 em forma de pergunta vem uma resposta **direta, objetiva e que se sustenta sozinha, com no máximo 55 palavras**. Só depois o texto aprofunda.
   - FAQ no fim com as mesmas regras e com dados estruturados (FAQPage).
3. **GEO**
   - Muitos fatos por parágrafo, com **data explícita** (dia/mês/ano ou temporada).
   - Métricas: jogos, vitórias, empates, derrotas, aproveitamento, gols, minutos, posição na tabela.
   - **Tabelas** para carreira, temporadas e títulos.
   - Nada de adjetivo vazio ("excelente", "renomado"). No lugar, o dado: "esquema 4-2-3-1", "Melhor Técnico do Brasileirão 2025".
4. **Fontes (regra do jornalista, não muda)**
   - Todo fato precisa de fonte aceita (CLAUDE.md, regra 3).
   - Título, prêmio, acesso, número e citação: **2 fontes independentes**.
   - O que o pedido traz como exemplo (prêmio, método, esquema) **também precisa ser conferido**. Sem fonte, fica fora.
   - Dado que falta aparece como "Em atualização". Nunca é estimado.
   - "Fontes e transparência" no fim, com links exatos. Revisão do Chefe de Redação antes de publicar (diretrizes/chefe-de-redacao.md).

## Estrutura da página fixa (para ser mais limpa e útil que os concorrentes)
1. **Topo:**
   - foto ou figurinha com crédito;
   - nome, cargo e clube com escudo;
   - linha de fatos: idade e nascimento, cidade natal, nacionalidade, esquema preferido (técnico) ou posição e pé (jogador), contrato até;
   - **Resposta rápida** em uma frase.
2. **Números da temporada atual:** caixas grandes. Técnico: jogos, V, E, D, aproveitamento. Jogador: jogos, minutos, gols, assistências. Em seguida, a temporada anterior.
3. **Títulos, acessos e prêmios:** em lista, com ano e clube.
4. **Carreira temporada a temporada:** tabela com ano, clube, função e números, com escudo de cada clube.
5. **Estilo de jogo / perfil tático:** só com fonte (esquema, ideias, falas do próprio).
6. **Linha do tempo:** contratação, estreia, marcos, saída.
7. **Mercado da Bola, "Saiu no BID" e jogos da temporada no TSP.**
8. **Matérias do TSP sobre a pessoa.**
9. **Perguntas frequentes:** respostas de até 55 palavras.
10. **Fontes e transparência.**

Dados estruturados: Person (com memberOf, birthDate, nationality, award, sameAs para os perfis oficiais da pessoa), FAQPage, BreadcrumbList.
O que fica de fora: anúncio no meio dos dados, página vazia e listas sem contexto.

## Agente editor: perguntar às IAs e definir as intenções de busca (22/11/2026, pedido do Thiago)
Para cada pessoa nova (ou página com muito "Em atualização"):
1. **Perguntar a uma IA** (Perplexity aberto no navegador, sem login) a trajetória completa: ficha técnica, formação, clubes com
   anos, títulos e acessos, estilo de jogo e esquema. Gravar a resposta em `rascunhos/ia-<nome>.md` como **pistas**: a IA não é fonte.
2. **Anotar quais fontes a IA usa.** Se ela cita Transfermarkt, Sofascore, Wikipedia ou Futebol Interior, é ali que o TSP precisa
   passar a ser a fonte citada (GEO). Dado que a IA não sabe ou erra = oportunidade do TSP.
3. **Intenções de busca de treinador** (viram campos da ficha e perguntas frequentes):
   - quem é / quantos anos tem / de onde é;
   - estilo de jogo; esquema tático preferido (formação em campo); formação acadêmica e licenças;
   - clubes que treinou; títulos; acessos;
   - números (jogos, vitórias, aproveitamento); contrato até quando.
   Jogador: posição e pé, idade, clubes, números da temporada, gols, títulos, valor de mercado só com fonte oficial.
4. **Conferir pista por pista** (subagente editor): título, acesso, número e nascimento com 2 fontes. Estilo e esquema só com matéria
   ou entrevista que os descreva. Pista derrubada ou sem fonte não entra.
5. Gravar na base (ficha: `nome_completo`, `natural`, `posicao_jogador`, `formacao`, `esquema`, `estilo`, `titulos`, `acessos`,
   `destaques`, `clubes_anteriores`; `carreira` por temporada; `carreira_fonte`). O tema mostra na ficha e nas perguntas frequentes.

## Clubes de fora de São Paulo (22/11/2026, pedido do Thiago)
- Todo clube citado numa trajetória vira link. O clube paulista leva para /times/<slug>/; o clube de fora, para /clube/<nome>/ (tema 1.8.4).
- Clube de fora: **sem notícias**. Entram só tabelas, elencos, ficha (dados/guia_clubes.json, com fonte) e evergreen, sempre com custo zero, saindo da base.
- O foco de cobertura continua sendo os clubes paulistas. Página de clube de fora com pouco conteúdo fica com noindex até a base crescer.
- Escudo de clube de fora: dados/escudos_extra.json + api/escudos/<nome>.png (120 px). Nome igual ao usado no mercado e na carreira.

## Números de treinador: só completos (23/11/2026, pedido do Thiago)
- Total de jogos, vitórias, aproveitamento e números por temporada só aparecem quando **toda** a carreira de técnico
  principal estiver levantada e conferida (cada trabalho com J/V/E/D em fonte aceita; número com 2 fontes).
  Aí marque `ficha.carreira_completa: true`. Sem isso o site mostra "Números da carreira: em atualização".
- Número parcial (só alguns clubes, só jogos da base do TSP) não vai ao ar.
- oGol, Sofascore, Transfermarkt e similares não valem para número de técnico. Exceção (26/11/2026): lista de jogos do oGol conferida com as datas de entrada e saída (diretrizes/paginas-pilares.md).

## Home do Mercado da Bola (23/11/2026)
- Cada divisão mostra primeiro as figurinhas publicadas por último (`foto.em`, gravado pelo `mercado.py figurinha`).

### Trajetória sem buracos (24/11/2026, Thiago)
Antes de publicar a trajetória de um treinador, compare a lista com pelo menos uma lista pronta (Wikipédia, oGol, Sofascore) só como **pista** do que pode estar faltando. Cada passagem que aparecer lá e não estiver aqui é pesquisada em matérias (ge, Futebol Interior, jornais regionais, site do clube). Entra com 2 fontes; com 1 fonte entra com "1 fonte" no campo obs; sem matéria, não entra. Ex.: Paulo Roberto Santos estava sem XV de Piracicaba (2023-24), ASA (2023), Guarani (2015), Uberlândia (2025) e Manaus (2026).
