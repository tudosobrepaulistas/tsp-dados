# Chefe de Redação (21/11/2026, pedido do Thiago)

Toda matéria da Máquina passa por dois agentes antes de ir ao site:

1. **Redator** (a sessão da Máquina): apura, escreve o JSON da matéria em `/tmp/materia.json`.
2. **Chefe de Redação** (um subagente novo, que NÃO escreveu o texto): confere fato por fato contra as fontes e devolve
   aprovado ou a lista de correções. O redator aplica as correções e só então roda `maquina.py adicionar`.

## Como chamar o Chefe de Redação
Use a ferramenta Agent (subagente geral) com este pedido, colando o JSON inteiro:

> Você é o Chefe de Redação do Tudo Sobre Paulista. Leia `diretrizes/chefe-de-redacao.md` (seção "O que conferir") e confira esta
> matéria contra as fontes listadas nela (abra cada link com WebFetch; não use Sofascore, Flashscore, oGol, Transfermarkt,
> FotMob nem placar do Google). Para cada nome, cargo, número, data, placar, divisão e citação, diga se a fonte confirma.
> Responda só em JSON: {"veredito": "aprovado" | "corrigir" | "barrar", "conferidos": [{"fato": "...", "fonte": "url"}],
> "correcoes": [{"trecho": "texto atual", "certo": "texto corrigido", "fonte": "url"}], "motivo": "..."}.

- `aprovado`: grave o retorno no campo `revisao` do JSON e rode `adicionar`.
- `corrigir`: aplique todas as correções, grave `revisao` com `"veredito": "aprovado"` e as `correcoes` aplicadas, e rode `adicionar`.
- `barrar`: não publique. Rode `sem-pauta` com o motivo.

O campo `revisao` é obrigatório: o `adicionar` recusa matéria sem ele, ou com `veredito` diferente de `aprovado`, ou sem fatos conferidos.

## O que conferir (o chefe recusa se faltar qualquer item)
1. **Toda pessoa citada** tem nome e cargo iguais aos da fonte. Treinador, auxiliar, presidente: grafia exata.
2. **Promessa do título é cumprida no texto.** "Veja a lista", "quem são", "os 16 clubes" → a lista completa está no corpo,
   com o nome de cada um (ex.: o treinador de cada clube). Número no título (ex.: "11 dos 16") bate com a contagem no corpo.
3. **Divisão certa, sem apelido trocado.** No futebol paulista masculino:
   - Série A1 = Paulistão (elite) · Série A2 · Série A3 · **Série A4** (4º nível, criada em 2023)
   - **Segunda Divisão** (5º nível, Sub-23), apelidada de **"Bezinha"**. A Bezinha NÃO é a A4.
   - Quem cai da A4 vai para a Segunda Divisão. Quem sobe da A4 vai para a A3.
   Na dúvida, escreva o nome oficial ("Série A4", "Segunda Divisão") e nunca use o apelido.
4. **Datas e números** (início do campeonato, final, rodada, idade, jogos, gols, pontos, posição) aparecem na fonte.
5. **"Ex-clube"**: só escreva "ex-X" se a fonte disser que a pessoa trabalhou/jogou no X. Clube que mudou de nome:
   explique (ex.: "no Joseense, atual Jacareí").
6. **Regulamento** é citado como a fonte diz (ex.: "relacionar até cinco atletas acima de 23 anos por partida", e não "em campo").
7. **Fonte de cada informação** está na lista de fontes da matéria. Informação sem fonte sai do texto.
8. Citação entre aspas: só se a fonte reproduz a frase.
9. Nada de opinião negativa do TSP sobre clube, pessoa ou campeonato. Título e intertítulo em tom neutro.

## Vale também para o editor-chefe e para quem revisar matérias publicadas
A mesma lista é usada pelo editor-chefe (diretrizes/editor-chefe.md) ao conferir o que já está no ar.
