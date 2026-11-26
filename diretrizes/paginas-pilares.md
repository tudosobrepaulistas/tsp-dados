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

## Números de técnico pelo oGol (26/11/2026, liberado pelo Thiago)
- A lista de jogos do oGol (página "jogos realizados" do técnico) pode ser a base de jogos, vitórias, empates e derrotas,
  **desde que conferida com as datas de entrada e saída de cada clube publicadas pela imprensa**. Jogo fora do período = fora da conta
  (ex.: Moisés Egert: saiu de 5 jogos que o oGol atribui a ele depois da saída do Rio Branco em 2012 e do Mirassol em 2019).
- Jogos como interino/auxiliar não entram na conta de técnico principal (citar à parte).
- Com todas as passagens conferidas, marcar `ficha.carreira_completa: true` e preencher jogos/vitorias/empates/derrotas em cada linha.
- Marcos (1º jogo, 50º, 100º... 500º; 1ª, 50ª, 100ª... vitória) viram tabela na página e pauta para a redação.
  O próximo marco ("faltam N jogos para os 500") também é pauta: acompanhar quando o técnico assumir um clube.
- Naturalidade só com 2 fontes que concordem (Egert: oGol diz São Borja, Wikipédia diz Caxias do Sul; fica só o estado).
