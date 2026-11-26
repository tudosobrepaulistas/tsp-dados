# Páginas pilares de treinadores parceiros (26/11/2026, pedido do Thiago)

Meta: os treinadores parceiros do canal no top 3 do Google pelo nome (ex.: "moises egert", 210 buscas/mês, concorrência baixa).
Lista: Marcelo Marelli, Moisés Egert, Elio Sizenando, Fernando Marchiori, Raphael Pereira, Danilo Sacramento, Thiago Oliveira, Paulo Roberto Santos.

## Onde fica
- Dados: `dados/pessoas.json` → `python3 ferramentas/pessoas.py gerar` → `api/pessoas.json` (o tema 1.12.0+ lê a cada 30 min).
- Endereço fixo: `/treinador/<nome>/` (não muda quando troca de clube; o endereço antigo com o clube dá 301).
- Mapa do site: `/pessoas-sitemap.xml` (entra no índice do Yoast).
- Link automático: a primeira menção do nome numa matéria vira link para a página pilar.
- A página do episódio do TSP Exclusiva ganha "Perfil completo de X".

## Como escrever (regras de diretrizes/pessoas.md, sem exceção)
- `pilar.titulo` (até 75 caracteres, com o nome primeiro), `pilar.descricao` (até 160), `pilar.resposta_rapida` (até 55 palavras).
- `pilar.secoes`: H2 em forma de pergunta de busca real; `resposta` de até 55 palavras que se sustenta sozinha; `texto` aprofunda com datas.
- Título, acesso, número e citação: 2 fontes aceitas. O TSP Exclusiva é fonte primária do que o próprio entrevistado disse.
- Dado sem fonte fica fora (aparece "Em atualização"). Nada de "1 fonte" visível ao leitor.
- Depois de mudar: `python3 ferramentas/pessoas.py gerar`, commit e push.
