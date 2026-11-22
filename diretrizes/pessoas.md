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
