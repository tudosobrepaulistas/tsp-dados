# Máquina de Notícias do TSP (fase 1)

Uma matéria a cada 1h30, das 8h às 23h (horários em `maquina/clubes.json`), publicada sozinha no site, sem revisão humana.
Por isso o padrão é o do Radar Palestrino: **nada sem fonte, nada inventado, texto próprio do TSP.**

**Fase 1: só os 41 clubes de `maquina/clubes.json`** (sem divisão / Segunda Divisão, a "Bezinha").
Próximas fases: Paulistão A4, depois A3, depois A2. Não escreva sobre clube fora da lista.

## Varredura (como cada execução funciona)
Cada execução é uma **varredura**: escreve de **5 a 6 matérias**, de clubes diferentes, e cada uma vai para o próximo horário livre
(`adicionar` preenche sozinho). Assim sempre fica um estoque agendado no site; o administrador pode soltar qualquer uma na hora
("Publicar agora") ou deixar sair no horário. Repita os passos abaixo até ter 5 a 6 matérias na fila nesta execução
(rode `proximo` de novo depois de cada `adicionar`: ele já tira os clubes que acabaram de entrar). Tente no máximo 10 clubes.
Se `proximo` mostrar que já há 8 ou mais horários ocupados à frente, pare: o estoque está cheio.
Faça **um commit e push depois de cada matéria** (se a execução cair no meio, o que já foi feito não se perde).

## Passo a passo de cada matéria
1. `python3 ferramentas/maquina.py proximo` → horário livre e 6 clubes sorteados entre os mais esquecidos. Pegue o 1º.
2. `python3 ferramentas/maquina.py historico CLUBE` → o que o site e a Máquina já publicaram. **Não repita assunto nem palavra-chave.**
3. Se o clube ainda não tem cidade/site/jornais em `clubes.json`, pesquise e grave com `maquina.py clube ...`.
4. Procure notícia dos últimos 7 dias (WebSearch + WebFetch, só páginas de notícia), nesta ordem:
   - **site oficial e redes oficiais do clube** (fonte obrigatória de consulta): notas, contratações, coletivas, entrevistas, pronunciamentos;
   - **jornais e portais da cidade/região do clube** (ex.: Folha da Região em Araçatuba, Diário da Região em Rio Preto, O Imparcial em Presidente Prudente, Jornal Cidade em Rio Claro, A Cidade em Ribeirão Preto, EPTV/ge regional);
   - FPF (calendário, tabela, súmulas e notas oficiais), ge, Gazeta Esportiva, UOL, Lance! e as demais de `CLAUDE.md`.
5. Decida o tipo:
   - **noticia**: fato novo confirmado por **2 fontes independentes** (o site oficial do clube + um jornal conta como 2).
   - **coletiva**: entrevista/pronunciamento publicado pelo próprio clube (vídeo ou texto). Use só falas que aparecem na fonte, entre aspas, com o nome de quem falou. Pode ser 1 fonte (o canal oficial), mas cite o link.
   - **historia** (sem notícia nova): tema histórico/atemporal **conferido em pelo menos 1 fonte confiável** (de preferência 2): títulos, acessos, ídolos, "você sabia que Fulano jogou no clube", estádio, rivalidades, apelidos (ex.: "O que foi o Carrossel Caipira", "Os títulos do Araçatuba", "Craques que passaram pelo Matonense"). Nunca preencha lacuna com suposição: data, placar ou nome sem fonte fica de fora.
6. Sem notícia e sem tema histórico seguro? **Não escreva.** Rode
   `maquina.py sem-pauta CLUBE --motivo "..." --sugestao "pauta concreta para um redator"` e passe para o próximo clube da lista.
   Se nenhum dos 6 render, registre os avisos e termine (o horário fica vazio, sem problema).
7. Monte o JSON (formato abaixo) em `/tmp/materia.json` e rode `maquina.py adicionar /tmp/materia.json`. A ferramenta recusa
   título repetido, palavra-chave repetida, fonte proibida, conteúdo de aposta e horário ocupado. Corrija e rode de novo.
8. `git add -A && git commit -m "máquina: <clube> - <título curto>" && git push` (com as linhas de coautoria do CLAUDE.md da sessão).

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
- Proibido: apostas/odds/palpites, boato, "segundo informações" sem dizer de quem, opinião ofensiva.

## Foto (sempre com crédito)
Ordem de preferência:
1. **Foto do próprio clube** (site oficial ou rede oficial) publicada junto da notícia: crédito `Foto: Nome do fotógrafo/Clube`
   ou, sem nome, `Foto: Reprodução/Site oficial do Clube`. `fonte` = a página onde ela está.
2. **Coletiva/entrevista em vídeo do canal oficial**: miniatura do vídeo (`https://i.ytimg.com/vi/ID/maxresdefault.jpg`),
   crédito `Foto: Reprodução/YouTube Nome do Clube`.
3. **Wikimedia Commons ou Flickr** com licença CC BY, CC BY-SA, CC0 ou domínio público (nunca NC ou ND): crédito
   `Foto: Autor / Wikimedia Commons (CC BY-SA 4.0)`. Ótimo para estádios e matérias históricas.
- A foto precisa mostrar o assunto (o clube, o estádio, a pessoa). Nada de foto genérica de outro clube.
- Mínimo 600 px de largura. Não use foto de agência (Getty, AGIF, Reuters etc.) nem de jornal.
- **Não achou foto segura?** Mande sem `foto`. O site guarda a matéria como **rascunho** e avisa os redatores para
  colocar a foto e publicar (a matéria passa a contar para quem finalizar).

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
  "foto": {"url": "https://...", "credito": "Foto: Reprodução/Site oficial do Araçatuba", "fonte": "https://página-da-foto", "alt": "descrição da foto"}
}
```
`publish_at` é preenchido sozinho com o próximo horário livre.
