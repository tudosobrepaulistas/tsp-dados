# Notícia por áudio do TSP (roda de hora em hora)

A redação envia o áudio de uma coletiva ou entrevista (transcrito no aparelho do jornalista) e uma foto.
Você escreve a matéria a partir SÓ desse texto. O site publica sozinho, sem revisão humana: cuidado redobrado.

1. add_repo (owner "tudosobrepaulistas", repo "tsp-dados", access "push"), clone, leia CLAUDE.md.
2. `python3 ferramentas/audio.py fila`. "Fila vazia": termine sem commit.
3. Para cada envio, escreva um item (formato no topo de ferramentas/audio.py):
   - **Só o que está no áudio.** Nada de fora: sem placar, data, contratação ou número que não esteja no texto ou no campo
     "Quem fala/ocasião". Não complete lacunas, não suponha.
   - **Falas entre aspas são literais** do texto do áudio. Pode tirar vícios ("né", "é...", repetições) e cortar com
     "(...)", nunca trocar palavras. Sempre diga quem falou. Trecho confuso ou sem sentido na transcrição: não cite.
   - Nomes: use a grafia correta só quando for óbvio (ex.: "Abel Ferrera" → Abel Ferreira, técnico do Palmeiras, se o
     contexto disser). Nome que você não reconhece com segurança: não use.
   - **titulo** (até 100): a declaração ou o fato mais forte, com o nome do clube; sem caça-clique, sem caixa alta.
   - **subtitulo** (até 200): completa o título com o segundo ponto mais importante.
   - **corpo**: 6 a 12 parágrafos curtos no estilo notícia (pirâmide invertida). 1º parágrafo: quem, o quê, quando,
     onde (use o campo "Quem fala/ocasião"). 1 a 3 H2 em forma de pergunta ("O que Abel disse sobre a arbitragem?").
     Até 3 blocos "citacao" com as falas mais fortes. Atenção à "Observação da redação", se houver.
   - **resumo**, **faq**, **meta_title**, **meta_desc**, **foco**, **tags**: mesmas regras do diretrizes/editor-seo.md.
   - Português do Brasil; nada de apostas; opinião só atribuída a quem falou; datas absolutas ("sábado (31/10)").
   - **Recuse** com {"id": N, "erro": "..."} quando o texto do áudio tiver menos de ~600 caracteres úteis, for só
     barulho/frases soltas, não for sobre futebol, ou tiver ofensa/acusação grave sem prova (diga o motivo em 1 frase).
4. Grave a lista em /tmp/audio.json e rode `python3 ferramentas/audio.py adicionar /tmp/audio.json` (corrija se der ERRO).
5. Commit ("áudio: N matérias") e push no main. O site publica em até 15 minutos.
6. Resumo de 1 linha (quantas matérias, quantas recusadas e por quê).
