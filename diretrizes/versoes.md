# Versões por clube (mesma notícia, ótica de cada clube marcado)

Quando um redator publica uma matéria que envolve **dois ou mais clubes paulistas** e marca todos eles (ex.: pós-jogo da A4
Lemense x São Caetano; "FPF divulga a tabela da A3" com 16 clubes), a Redação TSP publica **uma versão para cada clube que
não é o foco da original**, contada pelo lado dele. A original do redator continua sendo a da home; as versões aparecem
**só na página do clube** (o site já esconde da home e dos blocos) e **não contam para o pagamento do redator**.

## Passo a passo (cada execução)
1. `python3 ferramentas/maquina.py versoes-pendentes` → matérias e as versões que faltam. `nenhuma`: termine.
2. Para cada matéria (no máximo **15 versões por execução**, das mais antigas para as mais novas):
   - `python3 ferramentas/maquina.py original ID` → texto da original e clubes marcados.
   - Escreva a versão de cada clube pendente, **só com os fatos da original** (e, se quiser, dados da base `api/tsp.json`:
     próximo jogo, posição na tabela). Nada novo sem fonte. Não copie frases: reescreva com o clube como sujeito.
     Ex.: original "Lemense goleia o São Caetano por 4 a 0 no Brunão" → versão do São Caetano: "São Caetano é goleado
     pelo Lemense em Leme e se complica na A4". Tabela da A3 → versão do Rio Branco: "Rio Branco estreia em casa contra o
     Inter de Bebedouro na A3"; versão do Inter de Bebedouro: "Inter de Bebedouro encara o Rio Branco em Americana na estreia".
     Placar, datas, nomes e números idênticos aos da original.
   - Monte o JSON e rode `python3 ferramentas/maquina.py adicionar /tmp/versao.json`.
3. `git add -A && git commit -m "versões: N versões por clube"` (com as linhas de coautoria) e `git push`;
   no fim, `python3 ferramentas/maquina.py avisar-site`.

## Formato
```json
{"tipo": "versao", "versao_de": 546635, "clube": "palmeiras", "clube_nome": "Palmeiras",
 "titulo": "Palmeiras conhece datas e horários das duas últimas rodadas do Brasileirão",
 "subtitulo": "...", "corpo": [{"p": "..."}, {"h2": "Quando o Palmeiras joga?"}, {"p": "..."}, {"p": "..."}, {"p": "..."}],
 "resumo": ["...", "...", "..."], "faq": [["...?", "..."]],
 "foco": "jogos do Palmeiras na reta final do Brasileirão", "meta_title": "...", "meta_desc": "...",
 "tags": ["Palmeiras", "Brasileirão"],
 "fontes": [{"nome": "Matéria original do TSP", "url": "https://tudosobrepaulista.com.br/materia/..."}]}
```
- `clube` = o slug que o `versoes-pendentes` mostrou; o nome do clube precisa estar no título.
- A foto é a mesma da original (o site copia com o crédito). Sai na hora, assinada pela Redação TSP, com o aviso
  "Versão do clube … Leia a matéria original".
- `foco` diferente do da original (palavra-chave do clube). Sem apostas.
