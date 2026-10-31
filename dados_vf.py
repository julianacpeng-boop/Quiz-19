"""Quiz-19: 7 temas atuais e 8 nostálgicos. Uma afirmação por vídeo."""
PERGUNTAS = [
  {
    "tema": "Virginia em Miami",
    "pergunta": "O vídeo de Virginia que gerou críticas foi gravado em Miami.",
    "verdadeiro": True,
    "explicacao": "A cobertura da semana situou a festa em Miami, nos Estados Unidos.",
    "imagem": "imagens_perguntas/01_virginia_miami.png",
    "legenda": "Você acompanhou essa polêmica?",
    "hashtags": [
      "#Virginia",
      "#Famosos",
      "#Atualidades",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Virginia e Silvia",
    "pergunta": "A discussão entre Silvia Abravanel e Virginia ficou restrita à roupa usada na festa.",
    "verdadeiro": False,
    "explicacao": "As críticas também atingiram a maternidade de Virginia, e sua equipe divulgou uma resposta.",
    "imagem": "imagens_perguntas/02_virginia_silvia.png",
    "legenda": "Até onde foi essa discussão?",
    "hashtags": [
      "#Virginia",
      "#SilviaAbravanel",
      "#Atualidades",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Craque Neto e BTS",
    "pergunta": "Neto pediu desculpas aos fãs do BTS após criticar o grupo.",
    "verdadeiro": True,
    "explicacao": "No programa de 30 de outubro, Neto se retratou e disse ter ouvido as músicas do grupo.",
    "imagem": "imagens_perguntas/03_neto_bts.png",
    "legenda": "Você viu a reação dos fãs?",
    "hashtags": [
      "#BTS",
      "#CraqueNeto",
      "#Atualidades",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Memes políticos",
    "pergunta": "Uma imagem de político em um meme pode ter sido criada por inteligência artificial.",
    "verdadeiro": True,
    "explicacao": "Memes podem usar montagens e IA. A aparência realista não comprova que a cena aconteceu.",
    "imagem": "imagens_perguntas/04_memes_politicos.png",
    "legenda": "Você cairia nessa montagem?",
    "hashtags": [
      "#Memes",
      "#Politica",
      "#Checagem",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Intolerância política",
    "pergunta": "Reportagens desta semana relataram denúncias de retaliação política no trabalho.",
    "verdadeiro": True,
    "explicacao": "A cobertura de 29 e 30 de outubro abordou demissões e uma ordem de reintegração. Denúncia não equivale a julgamento definitivo.",
    "imagem": "imagens_perguntas/05_convivencia_politica.png",
    "legenda": "A eleição acabou. E a convivência?",
    "hashtags": [
      "#Convivencia",
      "#Atualidades",
      "#Respeito",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Pedidos cancelados",
    "pergunta": "Todo pedido comercial cancelado depois da eleição comprova boicote político.",
    "verdadeiro": False,
    "explicacao": "Houve relatos de cancelamentos, mas a data, sozinha, não comprova o motivo de cada decisão comercial.",
    "imagem": "imagens_perguntas/06_pedidos_cancelados.png",
    "legenda": "Cancelamento ou boicote: dá para concluir?",
    "hashtags": [
      "#Comercio",
      "#Atualidades",
      "#Economia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Vídeos virais",
    "pergunta": "A CNN confirmou que um vídeo de Nikolas era o vídeo sem som mais visto do mundo.",
    "verdadeiro": False,
    "explicacao": "O UOL Confere desmentiu a atribuição à CNN. O trecho que circulava havia sido adulterado.",
    "imagem": "imagens_perguntas/07_video_nikolas.png",
    "legenda": "Um vídeo viral conta a história toda?",
    "hashtags": [
      "#VideosVirais",
      "#Checagem",
      "#Atualidades",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Locadoras e VHS",
    "pergunta": "As fitas VHS precisavam ser rebobinadas para voltar ao início.",
    "verdadeiro": True,
    "explicacao": "A fita magnética era enrolada entre carretéis. Rebobinar fazia a gravação retornar ao começo.",
    "imagem": "imagens_perguntas/08_locadoras_vhs.png",
    "legenda": "Quem lembra de devolver a fita?",
    "hashtags": [
      "#VHS",
      "#Locadora",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Orkut e MSN",
    "pergunta": "Orkut e MSN Messenger eram o mesmo serviço.",
    "verdadeiro": False,
    "explicacao": "Orkut era uma rede social com perfis e comunidades. MSN Messenger era um serviço de mensagens instantâneas.",
    "imagem": "imagens_perguntas/09_orkut_msn.png",
    "legenda": "Qual deles marcou sua adolescência?",
    "hashtags": [
      "#Orkut",
      "#MSN",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Lan house e internet",
    "pergunta": "Na conexão discada pela linha telefônica comum, navegar podia deixar o telefone ocupado.",
    "verdadeiro": True,
    "explicacao": "A conexão discada usava a linha de voz. Na mesma linha, o uso do telefone podia interromper a internet.",
    "imagem": "imagens_perguntas/10_lan_house.png",
    "legenda": "Quem lembra daquele barulho?",
    "hashtags": [
      "#LanHouse",
      "#InternetDiscada",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Walkman e Discman",
    "pergunta": "O Discman tradicional reproduzia fitas cassete.",
    "verdadeiro": False,
    "explicacao": "O Discman era um tocador portátil de CDs. Modelos clássicos de Walkman usavam fitas cassete.",
    "imagem": "imagens_perguntas/11_walkman_discman.png",
    "legenda": "Qual desses ia com você para todo lugar?",
    "hashtags": [
      "#Walkman",
      "#Discman",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Bichinhos virtuais",
    "pergunta": "No Tamagotchi clássico, era preciso cuidar de um bichinho virtual.",
    "verdadeiro": True,
    "explicacao": "O brinquedo eletrônico simulava cuidados como alimentação, limpeza e brincadeiras.",
    "imagem": "imagens_perguntas/12_tamagotchi.png",
    "legenda": "Você conseguia cuidar do seu?",
    "hashtags": [
      "#Tamagotchi",
      "#Brinquedos",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Figurinhas e tazos",
    "pergunta": "Tazos e figurinhas eram exatamente o mesmo tipo de objeto.",
    "verdadeiro": False,
    "explicacao": "Tazos eram peças rígidas, geralmente em forma de disco. Figurinhas eram impressos colecionáveis, muitas vezes adesivos.",
    "imagem": "imagens_perguntas/13_tazos_figurinhas.png",
    "legenda": "Qual era o tesouro do seu recreio?",
    "hashtags": [
      "#Tazos",
      "#Figurinhas",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "TV da infância",
    "pergunta": "A TV aberta exibia desenhos infantis antes de existir streaming.",
    "verdadeiro": True,
    "explicacao": "Por décadas, desenhos integraram a programação da TV aberta, com horários definidos pelas emissoras.",
    "imagem": "imagens_perguntas/14_tv_infancia.png",
    "legenda": "Qual programa fazia você correr para a TV?",
    "hashtags": [
      "#TVAntiga",
      "#Desenhos",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  },
  {
    "tema": "Videogames clássicos",
    "pergunta": "Todos os consoles que usavam cartuchos precisavam de memory card para salvar jogos.",
    "verdadeiro": False,
    "explicacao": "Os sistemas variavam: alguns jogos usavam bateria no cartucho, outros senhas, e muitos nem permitiam salvar.",
    "imagem": "imagens_perguntas/15_videogames.png",
    "legenda": "Você lembra como salvava sua partida?",
    "hashtags": [
      "#Videogame",
      "#GamesRetro",
      "#Nostalgia",
      "#JuhQuiz"
    ]
  }
]
