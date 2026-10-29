# Pré-jogo do TSP (página de confronto de cada jogo)

Cada página de jogo do site (ex.: /jogo/criciuma-x-ponte-preta-30-10-2026/) mostra, além do placar:
onde assistir, prováveis escalações, análise do jogo ("O que está em jogo"), retrospecto do confronto e a foto do estádio.
Tudo vem do campo "prejogo" do jogo, gravado com `python3 ferramentas/tsp.py prejogo ID --json /tmp/pre.json`.

## Quando
- **Até 72h antes do jogo:** análise, retrospecto, onde assistir (se já anunciado) e estadio_wiki.
- **Entre 6h e 4h antes do jogo:** prováveis escalações (e confirmar onde assistir). Se já houver escalação mais recente
  depois disso, pode atualizar de novo até o início.
- Prioridade: jogos com clube paulista primeiro; depois o resto da Série A e da Série B.

## Formato do arquivo (só os campos que for gravar)
```json
{
 "onde_assistir": {"canais": [{"nome": "Premiere", "tipo": "pay-per-view"}, {"nome": "Disney+", "tipo": "streaming"}],
                   "fontes": ["https://matéria que confirma a transmissão"]},
 "provaveis": {
   "casa": {"tecnico": "Nome", "time": "Goleiro; Lateral, Zagueiro, Zagueiro e Lateral; Volante, Meia e Meia; Atacante, Atacante e Atacante",
            "desfalques": "Fulano (lesão no joelho) e Beltrano (suspenso, 3º amarelo)", "duvidas": "Ciclano"},
   "fora": {"tecnico": "...", "time": "...", "desfalques": "...", "duvidas": ""},
   "fontes": ["https://...", "https://..."]},
 "analise": ["2 a 6 parágrafos ..."],
 "retrospecto": "1 parágrafo sobre o histórico do confronto, com números e a fonte",
 "estadio_wiki": "Estádio Heriberto Hülse",
 "fontes": ["https://... usadas na análise e no retrospecto"]
}
```

## Regras (valem as do CLAUDE.md)
- **Nunca inventar.** Escalação só "provável", como as matérias trazem (ge, Lance!, site oficial, jornais regionais
  grandes). Use as fontes que publicaram a provável escalação nas últimas 24h; se duas fontes divergem, use a mais recente
  do jornal local/site oficial e diga as dúvidas em "duvidas". Sem fonte: não grave "provaveis".
- **Onde assistir:** só canais confirmados por matéria ou comunicado (CBF, clube, emissora). Não confirmado: não grave.
- **Análise (texto rico, jornalístico, nosso):** 3 a 5 parágrafos curtos, português do Brasil, sem copiar frases.
  1º: o que está em jogo (posição na tabela, objetivo: título, acesso, G4, Z4, classificação) com números da Base TSP
  (`api/classificacao/<comp>.json` e os últimos jogos). 2º: momento do mandante (últimos 5, em casa, artilheiro se a
  base tiver). 3º: momento do visitante (fora de casa). 4º: o que dizem os técnicos/bastidores (só com fonte, atribuído).
  Datas absolutas ("sexta-feira (30/10)"). Sem opinião própria nem palpite de resultado. Nada de apostas.
- **Retrospecto:** histórico do confronto (total de jogos, vitórias de cada lado, último encontro) só com fonte.
  Sem fonte confiável: escreva só o último confronto que estiver na Base TSP, ou deixe sem.
- **estadio_wiki:** o título exato da página do estádio na Wikipédia em português (ex.: "Estádio Heriberto Hülse",
  "Arena Fonte Nova"). O site busca a foto do estádio lá, só se a licença for livre (CC BY, CC BY-SA, CC0 ou domínio público),
  e mostra com o crédito do autor. Não precisa mandar foto.
