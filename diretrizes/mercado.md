# Mercado da Bola 2027 e Elenco 2027 (pedido do Thiago, 14/11/2026)

O site mostra o mercado em 7 blocos da home (Série A, Série B, Feminino, Paulistão A1, A2, A3 e A4), na página
`/mercado-da-bola/` e na página de cada clube ("Mercado da bola" + "Elenco 2027" com foto). Tudo vem de
`dados/mercado.json` e `dados/elencos/`, gerados em `api/mercado.json` e `api/elencos.json` (o site lê a cada 30 min).

## Rotina diária (tarefa agendada, 1 vez por dia)
1. **Varredura** (gaste pouco: buscas curtas, sem abrir página à toa). Ordem de prioridade:
   - Série A (Corinthians, Palmeiras, Santos, São Paulo, Bragantino, Mirassol, Novorizontino) e Série B (São Bernardo,
     Botafogo-SP, Ponte Preta e quem mais for paulista na B 2027);
   - Futebol feminino (Corinthians, Palmeiras, São Paulo, Santos, Ferroviária, Bragantino, Mirassol, Taubaté);
   - Paulistão A1, A2, A3 e A4 (Futebol Interior, DGABC, jornais regionais e ge regionais anunciam quase todo dia).
   Buscas úteis: "<clube> anuncia contratação 2027", "<clube> renova", "reforço para 2027 Paulistão A2/A3/A4",
   "Mercado da Bola" da Gazeta Esportiva do dia.
2. **Só entra o que está fechado**: `oficial` (o clube anunciou) ou `acertado` (2 veículos dizem que está fechado).
   Sondagem, interesse, proposta, "perto de" = **não entra**.
3. **Fontes**: 2 links de fontes aceitas (CLAUDE.md). Clube pequeno (A2 a A4) que só anuncia no Instagram: vale 1 matéria de
   veículo aceito que relata o anúncio oficial, com `"anuncio_do_clube": true`.
   **oGol e Transfermarkt**: o Thiago liberou como **referência** para descobrir movimentos e conferir posição/clube de origem.
   Não valem como fonte e nada é copiado deles (a ferramenta recusa esses links em `fontes`).
4. **Gravar**: monte um JSON (lista) e rode
   `python3 ferramentas/mercado.py registrar --json /tmp/mercado.json` → `python3 ferramentas/mercado.py validar` → `python3 ferramentas/mercado.py gerar`.
   - `data` = dia do anúncio (o que a matéria diz; sem data clara, a data de publicação da matéria).
   - `de`/`para` como o clube é chamado; `de_slug`/`para_slug` = endereço do clube paulista no site (ver `dados/clubes_paulistas.json`).
     Feminino: `"feminino": true` (o sistema usa o endereço do time feminino).
   - `de` pode ficar vazio só em contratação quando a fonte não diz de onde o jogador veio. Nunca chute.
   - Renovação: `de` = `para`, `tipo: renovacao`, `obs` com o novo prazo ("contrato até dezembro de 2028").
   - `foto` só com foto oficial do clube + crédito; sem isso o site mostra a inicial (nada de imagem gerada).
5. **Elencos**: `python3 ferramentas/tsp.py elencos-faltando`; para cada clube paulista das Séries A e B sem elenco ou com
   elenco velho, grave o elenco do site oficial (`diretrizes/banco-times.md`, seção 2). O "Elenco 2027" do site = elenco
   oficial + chegadas oficiais − saídas oficiais do mercado (calculado sozinho no `gerar`).
6. `python3 ferramentas/tsp.py calcular && python3 ferramentas/tsp.py validar`, commit "mercado: N movimentos (dd/mm)" e push no main.
7. Resumo curto para o Thiago: quantos movimentos entraram por bloco e os 3 mais importantes.

## Quando a temporada começar
As estatísticas de 2027 de cada jogador (jogos, gols, minutos) entram nas páginas pelo banco de times
(`diretrizes/banco-times.md` e `diretrizes/temporada.md`), ligadas ao mesmo nome do elenco.

## Figurinhas 2027 (14/11/2026)
- Card no formato figurinha: o site monta a moldura (escudo do clube novo, divisão, nome, posição, idade, números de 2026) e
  mostra "Montagem com IA · ilustrativa" no rodapé quando a imagem é montagem.
- Retrato gerado no ChatGPT pago do Thiago (Chrome dele), SEM custo extra: 1ª imagem = foto oficial do jogador (arte de anúncio
  "Divulgação/Clube" ou foto de matéria aceita), 2ª imagem = escudo do clube (o do próprio site). O ChatGPT desenha o escudo no peito
  (pedido do Thiago, para não perder resolução). Sem foto oficial de referência com o rosto de frente, NÃO gera (nada de rosto inventado).
- Prompt: `python3 ferramentas/mercado.py figurinhas`. Baixar pelo botão de download do ChatGPT (vai para Downloads do Mac),
  conferir a imagem e gravar: `python3 ferramentas/mercado.py figurinha ID --img ARQUIVO --ref URL_DA_REFERENCIA`.
