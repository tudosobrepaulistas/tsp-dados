# Máquina de Notícias do TSP (fase 1)

Uma matéria a cada 1h30, das 8h às 23h (horários em `maquina/clubes.json`), publicada sozinha no site, sem revisão humana.
Por isso o padrão é o do Radar Palestrino: **nada sem fonte, nada inventado, texto próprio do TSP.**

**Responsável: Thiago Barbalho. Clubes da Máquina: Paulistão A4 (16, prioridade), futebol feminino (8) e os 41 sem divisão / Segunda Divisão**,
todos em `maquina/clubes.json` (campo `grupo`). A redação humana cobre o Paulistão A1, A2 e A3 (48 clubes): a Máquina NÃO escreve sobre eles.
**Cota diária (07/11/2026): 24 matérias por dia = 8 da A4, 8 dos clubes sem divisão e 8 do futebol feminino**, uma a cada
30 minutos, das 9h às 20h30. Toda matéria **com foto real e crédito** (a ferramenta recusa sem foto) e **notícia atualizada**
sempre que existir. `proximo` mostra a cota do dia e sugere clubes dos grupos atrasados. Não escreva sobre clube fora da lista.

## Varredura (como cada execução funciona)
São **duas varreduras por dia**: a das 6h agenda as matérias das 9h às 14h30 e a das 10h30 agenda as das 15h às 20h30.
Cada execução escreve **até 12 matérias** (4 de cada grupo, seguindo a cota que o `proximo` mostra), de clubes diferentes,
e cada uma vai para o próximo horário livre de 30 em 30 minutos (`adicionar` preenche sozinho). O administrador pode soltar
qualquer uma na hora ("Publicar agora") ou deixar sair no horário. Rode `proximo` de novo depois de cada `adicionar`.
Tente no máximo 25 clubes por execução. Pare quando o `proximo` disser **COTA DO DIA COMPLETA** ou não houver horário livre no dia.
Faça **um commit e push depois de cada matéria** (se a execução cair no meio, o que já foi feito não se perde).

## Passo a passo de cada matéria
1. `python3 ferramentas/maquina.py proximo` → horário livre e 6 clubes sorteados entre os mais esquecidos. Pegue o 1º.
2. `python3 ferramentas/maquina.py historico CLUBE` → o que o site e a Máquina já publicaram. **Não repita assunto nem palavra-chave.**
3. Se o clube ainda não tem cidade/site/jornais em `clubes.json`, pesquise e grave com `maquina.py clube ...`.
4. Procure notícia dos últimos 7 dias (WebSearch + WebFetch, só páginas de notícia), nesta ordem:
   - **site oficial e redes oficiais do clube** (fonte obrigatória de consulta): notas, contratações, coletivas, entrevistas, pronunciamentos.
     **Instagram e YouTube oficiais do clube valem como fonte oficial** (contam como a fonte do clube): ache o post/vídeo pelo
     WebSearch (ex.: `site:instagram.com novorizontino`, `site:youtube.com Novorizontino coletiva`) e use só o que dá para ler
     sem login (legenda do post, título e descrição do vídeo). Cite o **link exato do post ou vídeo**. Se o Instagram pedir login
     e o texto não aparecer, não use: procure o mesmo anúncio no site do clube ou num jornal da cidade. Nunca contorne login;
   - **jornais e portais da cidade/região do clube** (ex.: Folha da Região em Araçatuba, Diário da Região em Rio Preto, O Imparcial em Presidente Prudente, Jornal Cidade em Rio Claro, A Cidade em Ribeirão Preto, EPTV/ge regional);
   - FPF (calendário, tabela, súmulas e notas oficiais), ge, Gazeta Esportiva, UOL, Lance! e as demais de `CLAUDE.md`.
5. Decida o tipo:
   - **noticia**: fato novo confirmado por **2 fontes independentes** (o site oficial do clube + um jornal conta como 2).
   - **coletiva**: entrevista/pronunciamento publicado pelo próprio clube (vídeo ou texto). Use só falas que aparecem na fonte, entre aspas, com o nome de quem falou. Pode ser 1 fonte (o canal oficial), mas cite o link.
   - **historia** = conteúdo **evergreen** (sem notícia nova). Clubes **sem divisão** quase não têm notícia fora da temporada:
     **A cota de 8 por grupo é obrigatória** (pedido do Thiago, 08/11/2026: A4 e sem divisão estavam com 2 a 4 por dia).
     Sem notícia, **faça evergreen**: até **4 por dia** dos clubes sem divisão, **4 da A4** e **2 do feminino**,
     e **1 por clube a cada 14 dias** (a ferramenta recusa o excesso). Antes de desistir de um grupo, passe por TODOS os
     clubes dele (não só os 6 primeiros): coletiva/entrevista no canal oficial, post do site oficial, jornal da cidade. Varie o formato, não só "a história do clube":
     guia do estádio (onde fica, como chegar, capacidade), ídolos e "você sabia que Fulano jogou no clube", títulos e acessos,
     rivalidades e clássicos regionais, apelidos e mascote, como está o clube hoje (diretoria, base, projetos) e o que esperar
     da próxima temporada (só com fonte). Nada de lista de jogos antigos e estatísticas. Sem tema seguro, **peça a pauta** com `sem-pauta`.
     Tema histórico, quando usar: tema histórico/atemporal **conferido em pelo menos 1 fonte confiável** (de preferência 2): títulos, acessos, ídolos, "você sabia que Fulano jogou no clube", estádio, rivalidades, apelidos (ex.: "O que foi o Carrossel Caipira", "Os títulos do Araçatuba", "Craques que passaram pelo Matonense"). Nunca preencha lacuna com suposição: data, placar ou nome sem fonte fica de fora.
6. Sem notícia (ou com a cota de histórias do dia cheia)? **Não escreva.** Rode
   `maquina.py sem-pauta CLUBE --motivo "..." --sugestao "pauta concreta para um redator"` e passe para o próximo clube da lista.
   Só termine com o grupo abaixo de 8 depois de tentar todos os clubes dele; diga no resumo quantos faltaram e por quê.
7. Monte o JSON (formato abaixo) em `/tmp/materia.json` e rode `maquina.py adicionar /tmp/materia.json`. A ferramenta recusa
   título repetido, palavra-chave repetida, fonte proibida, conteúdo de aposta e horário ocupado. Corrija e rode de novo.
8. `git add -A && git commit -m "máquina: <clube> - <título curto>" && git push` (com as linhas de coautoria do CLAUDE.md da sessão).

## Fontes sempre à vista (para a redação conferir)
- Em `fontes`, coloque **todas** as fontes usadas: as 2 do cruzamento (ou a única, em coletiva/história), com o **nome do veículo**
  e o **link exato da matéria/post** (nunca a página inicial). Elas aparecem no fim da matéria ("Fontes e transparência"),
  no editor do WordPress e na tela da Máquina, para o administrador checar.
- No texto, atribua a informação: "segundo o site oficial do clube", "de acordo com a Folha da Região". Fala entre aspas sempre com quem disse e onde.
- Na foto, `fonte` = a página exata de onde a imagem veio.

## Texto (SEO, GEO e AEO, sem forçar)
- Reescreva com palavras do TSP. Nunca copie frases das fontes (só falas entre aspas, curtas e atribuídas).
- **Título** (até 100): com o nome do clube e a informação principal; sem caixa alta, sem clickbait, sem ponto final.
- **Subtítulo** (até 220): completa o título com um dado novo.
- **1º parágrafo** responde o quê, quem, quando, onde (lide). Isso é o que buscadores e IAs citam.
- 5 a 9 parágrafos curtos, 1 a 3 intertítulos (`h2`) em forma de pergunta natural ("Quando o Tupã volta a jogar?").
- Contexto local: cidade, estádio, divisão, temporada, próximo compromisso (só se confirmado).
- **foco** (palavra-chave principal, 2 a 5 palavras): a busca que um torcedor faria. Diferente das já usadas para o clube
  (veja `historico`) para não canibalizar. **meta_title** até 65, **meta_desc** até 160 com a palavra-chave.
- **tags**: 3 a 6 (clube, cidade, competição, pessoa citada).
- **resumo**: 3 a 4 frases curtas ("O que você precisa saber"). **faq**: 3 a 5 perguntas e respostas curtas, só com fatos das fontes.
- **Fontes no rodapé, não no texto** (boas práticas, 08/11/2026): o campo `fontes` já vira a lista "Fontes" no fim da
  matéria. No texto, **não** escreva "segundo o site X", "confirmado também por Y", "de acordo com as fontes" em cada
  frase. Cite o veículo ou jornalista **só** quando a informação for exclusiva dele (furo: "a informação foi publicada
  primeiro pelo ge") ou quando ele fizer parte da notícia. Nota oficial e coletiva: atribua uma vez ("em nota, o clube
  informou"; "na coletiva, o técnico disse"). Fala entre aspas sempre com quem disse. A ferramenta recusa texto com
  mais de 2 "segundo o/de acordo com" ou que fale da checagem.
- Proibido: apostas/odds/palpites, boato, "segundo informações" sem dizer de quem, opinião ofensiva.

## Foto (sempre com crédito)
Ordem de preferência:
1. **Foto do próprio clube** (site oficial ou rede oficial) publicada junto da notícia: crédito `Foto: Nome do fotógrafo/Clube`
   ou, sem nome, `Foto: Reprodução/Site oficial do Clube`. `fonte` = a página onde ela está.
2. **Coletiva/entrevista em vídeo do canal oficial**: miniatura do vídeo (`https://i.ytimg.com/vi/ID/maxresdefault.jpg`),
   crédito `Foto: Reprodução/YouTube Nome do Clube`.
3. **Wikimedia Commons ou Flickr** com licença CC BY, CC BY-SA, CC0 ou domínio público (nunca NC ou ND): crédito
   `Foto: Autor / Wikimedia Commons (CC BY-SA 4.0)`. Ótimo para estádios e matérias históricas.
- **A foto tem que mostrar exatamente o assunto da matéria** (regra endurecida em 08/11/2026, a pedido do Thiago):
  - matéria de **jogo** (prévia, decisão, "contra o X"): foto **de jogo**, de preferência **entre os mesmos dois times**
    (o jogo do 1º turno, a ida). Se não houver, foto de jogo recente do clube. Nunca retrato, coletiva ou estádio vazio.
  - matéria de **título, acesso ou conquista**: foto **daquela conquista** (taça, comemoração, festa no campo daquele ano).
  - matéria **histórica**: foto da época ou do personagem; se não existir livre, foto do clube na conquista mais próxima do tema.
  - matéria sobre **uma pessoa** (técnico, jogador, dirigente): foto dessa pessoa.
  - Nunca: arte, card, montagem, escudo, logo, foto de outro clube, foto que não tem ligação com o título.
- **Olhe a foto antes de usar** (obrigatório desde 08/11/2026): baixe a imagem (`curl -sL URL -o /tmp/foto.jpg`) e abra com
  Read. Se não conseguir baixar, use a página da notícia no navegador ou escolha outra foto: **nunca descreva uma foto que
  você não viu**. Selfie, retrato de celular, print de rede social com interface, foto vertical estreita ou com menos de
  600 px de largura não servem como foto principal. Se o clube não publicou foto daquele jogo, use foto de outro jogo
  da mesma categoria e do mesmo clube (e diga isso no `mostra`), ou passe para outra matéria.
- Campo **`foto.mostra` obrigatório**: uma frase dizendo o que a foto mostra (quem, qual jogo ou momento, data). A ferramenta
  confere se cita o clube, se é foto de jogo em matéria de jogo e foto de conquista em matéria de título, e recusa se não for.
  Descreva com honestidade o que está na imagem: se não bate com a matéria, procure outra.
- Mínimo 600 px de largura; **prefira 1200 px ou mais** (o Google Discover só mostra foto grande). Não use foto de agência (Getty, AGIF, Reuters etc.) nem de jornal.
- **Foto é obrigatória.** Sem foto segura com crédito, a ferramenta recusa: procure no site e nas redes oficiais do clube
  (post do Instagram, miniatura do vídeo do YouTube), no Commons/Flickr livre, ou passe para outro clube do mesmo grupo.

## Sem foto conferida: matéria pronta para o redator (14/11/2026, pedido do Thiago)
Quando a notícia está confirmada mas você **não achou ou não conseguiu abrir** uma foto certa (ex.: o site da imagem bloqueia
o download), **não descarte a matéria**. Escreva o texto completo, com o mesmo capricho de sempre, e no lugar de `foto` use:
```json
"foto_pendente": "Foto de jogo do Botafogo-SP, de preferência do 4 x 2 sobre o Juventude (23/07/2026). Há foto da Agência Botafogo (João Victor Menezes de Souza) em https://... Crédito sugerido: Foto: João Victor Menezes de Souza/Agência Botafogo"
```
Diga **que foto falta** (seguindo as regras acima: jogo, conquista ou a pessoa), **onde ela está** (links exatos que você viu
citados) e o **crédito sugerido**. Nunca descreva uma foto que você não viu. A matéria vai para o site como **rascunho**: os
redatores veem o aviso "📸 matérias prontas esperando foto" no painel e na tela Aprovação → "Esperando você", com o recado
"Foto que falta". O redator põe a foto com crédito, confere e publica, e a matéria passa a contar para ele.
Não use para evergreen de cota (A4, feminino, sem divisão): ali, sem foto, passe para outro clube. Na cobertura 6h, um
rascunho recente esperando foto conta como pauta feita (a ferramenta não pede outra matéria do mesmo clube/bloco por 6h).

## Formato do JSON
```json
{
  "clube": "aracatuba",
  "tipo": "noticia",
  "titulo": "Araçatuba anuncia técnico para a Segunda Divisão de 2027",
  "subtitulo": "...",
  "corpo": [{"p": "..."}, {"h2": "Quem é o novo técnico do Araçatuba?"}, {"p": "..."}, {"citacao": "Fala exata — Nome, cargo"}],
  "resumo": ["...", "...", "..."],
  "faq": [["Pergunta?", "Resposta."], ["...", "..."], ["...", "..."]],
  "foco": "técnico do Araçatuba",
  "meta_title": "...",
  "meta_desc": "...",
  "tags": ["Araçatuba", "Segunda Divisão", "..."],
  "fontes": [{"nome": "Site oficial do Araçatuba", "url": "https://..."}, {"nome": "Folha da Região", "url": "https://..."}],
  "foto": {"url": "https://...", "credito": "Foto: Reprodução/Site oficial do Araçatuba", "fonte": "https://página-da-foto", "alt": "descrição da foto", "mostra": "Jogadores do Araçatuba comemoram gol contra o Penapolense no Adhemar de Barros, 12/10/2026"}
}
```
`publish_at` é preenchido sozinho com o próximo horário livre.


## Não repetir assunto (13/11/2026)
O Google deixa de indexar matérias parecidas. Antes de escrever, confira se o site já tem o mesmo fato nas últimas 48h
(de qualquer clube): `python3 ferramentas/maquina.py ja-tem "palavras do assunto"`. Se já tiver, procure outro assunto
ou outro clube. Assunto de vários clubes (sorteio, tabela, regulamento) = UMA matéria completa marcando todos os clubes.
