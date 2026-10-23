"""Quiz-19: uma afirmação por tema, no padrão do Quiz-13.

Cada item reúne afirmação, gabarito, explicação, legenda e nome da imagem
realista correspondente. As imagens serão produzidas depois da revisão destes
dados.
"""

PERGUNTAS = [{'tema': 'Amazônia vista do espaço',
  'pergunta': 'O PRODES e o DETER têm exatamente a mesma função no monitoramento do desmatamento.',
  'verdadeiro': False,
  'explicacao': 'O PRODES calcula a taxa anual de corte raso; o DETER emite alertas mais rápidos '
                'para apoiar a fiscalização.',
  'legenda': 'Você sabe o que os satélites conseguem observar na Amazônia?',
  'hashtags': ['#Amazônia', '#Satélites', '#MeioAmbiente', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/amazonia_satelites_01.png'},
 {'tema': 'Queimadas e recuperação da floresta',
  'pergunta': 'A vegetação seca pode facilitar que um incêndio iniciado se espalhe.',
  'verdadeiro': True,
  'explicacao': 'Vegetação seca funciona como combustível; vento e baixa umidade também podem '
                'acelerar a propagação do fogo.',
  'legenda': 'O que faz uma queimada se espalhar com mais facilidade?',
  'hashtags': ['#Queimadas', '#Florestas', '#Natureza', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/queimadas_recuperacao_01.png'},
 {'tema': 'Árvores junto ao gado',
  'pergunta': 'Um sistema silvipastoril combina árvores, pastagem e animais na mesma área.',
  'verdadeiro': True,
  'explicacao': 'O sistema integra componentes florestais, agrícolas ou pastoris; a combinação '
                'exata depende do projeto.',
  'legenda': 'É possível criar gado e manter árvores na mesma área?',
  'hashtags': ['#Agropecuária', '#Sustentabilidade', '#Campo', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/arvores_gado_01.png'},
 {'tema': 'O custo físico da inteligência artificial',
  'pergunta': 'Servidores de centros de dados usam eletricidade para processar informações.',
  'verdadeiro': True,
  'explicacao': 'O processamento digital depende de equipamentos físicos que consomem energia e '
                'precisam operar em condições controladas.',
  'legenda': 'A inteligência artificial também depende de estruturas físicas?',
  'hashtags': ['#InteligênciaArtificial', '#Tecnologia', '#Energia', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/ia_centros_dados_01.png'},
 {'tema': 'Supercomputadores na ciência',
  'pergunta': 'Supercomputadores servem exclusivamente para treinar modelos de inteligência '
              'artificial.',
  'verdadeiro': False,
  'explicacao': 'Eles também são usados em pesquisas como previsão do tempo, simulações físicas, '
                'química e análise de grandes conjuntos de dados.',
  'legenda': 'Que outros problemas a supercomputação pode ajudar a resolver?',
  'hashtags': ['#Computação', '#Pesquisa', '#Curiosidades', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/supercomputador_ciencia_01.png'},
 {'tema': 'Deepfakes e segurança digital',
  'pergunta': 'Um deepfake pode imitar a voz de uma pessoa, além de alterar imagens ou vídeos.',
  'verdadeiro': True,
  'explicacao': 'Ferramentas de síntese podem criar ou modificar rostos, movimentos e vozes para '
                'parecerem reais.',
  'legenda': 'Uma voz conhecida em um áudio é sempre prova de que ele é verdadeiro?',
  'hashtags': ['#Deepfake', '#SegurançaDigital', '#Internet', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/deepfakes_seguranca_01.png'},
 {'tema': 'Corais e aquecimento dos oceanos',
  'pergunta': 'Todo coral que fica branco morreu imediatamente.',
  'verdadeiro': False,
  'explicacao': 'O branqueamento é sinal de estresse e pode ser reversível se as condições '
                'melhorarem, embora o coral fique mais vulnerável.',
  'legenda': 'Coral branco significa sempre que ele já morreu?',
  'hashtags': ['#Corais', '#Oceano', '#MeioAmbiente', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/corais_oceanos_01.png'},
 {'tema': 'Pontos de inflexão do clima',
  'pergunta': 'Um ponto de inflexão climático é um único dia em que o clima de todo o planeta muda '
              'de uma vez.',
  'verdadeiro': False,
  'explicacao': 'O termo descreve um limiar que pode desencadear mudanças grandes em um sistema; '
                'não significa uma virada simultânea em todo o planeta.',
  'legenda': 'O que os cientistas querem dizer com ponto de inflexão?',
  'hashtags': ['#Clima', '#Ciência', '#MudançasClimáticas', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/pontos_inflexao_clima_01.png'},
 {'tema': 'Solo vivo e agricultura regenerativa',
  'pergunta': 'Manter plantas cobrindo o solo pode ajudar a reduzir a erosão causada pela chuva e '
              'pelo vento.',
  'verdadeiro': True,
  'explicacao': 'A cobertura vegetal protege a superfície do solo e pode diminuir o impacto das '
                'gotas de chuva e do vento.',
  'legenda': 'O solo também precisa de proteção contra chuva e vento?',
  'hashtags': ['#AgriculturaRegenerativa', '#Solo', '#Natureza', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/solo_agricultura_01.png'},
 {'tema': 'Ilhas de calor nas cidades',
  'pergunta': 'Toda área urbana é sempre mais quente do que qualquer área rural, em qualquer '
              'horário.',
  'verdadeiro': False,
  'explicacao': 'Ilhas de calor são padrões locais e dependem de materiais, vegetação, clima e '
                'horário; não tornam toda cidade sempre mais quente que todo campo.',
  'legenda': 'A cidade inteira é sempre mais quente que o campo?',
  'hashtags': ['#IlhasDeCalor', '#Geografia', '#Clima', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/ilhas_calor_cidades_01.png'},
 {'tema': 'Energia renovável e baterias',
  'pergunta': 'Uma bateria armazena energia para liberá-la depois; ela não cria energia do nada.',
  'verdadeiro': True,
  'explicacao': 'Baterias convertem energia em uma forma armazenável e depois a devolvem, com '
                'perdas no processo.',
  'legenda': 'A bateria cria eletricidade ou guarda energia para depois?',
  'hashtags': ['#Baterias', '#Energia', '#Tecnologia', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/energia_baterias_01.png'},
 {'tema': 'Microplásticos na cadeia alimentar',
  'pergunta': 'Todas as consequências dos microplásticos para a saúde humana já estão '
              'completamente esclarecidas.',
  'verdadeiro': False,
  'explicacao': 'A pesquisa sobre exposição e efeitos na saúde continua; ainda há perguntas '
                'científicas em investigação.',
  'legenda': 'A ciência já conhece todos os efeitos dos microplásticos?',
  'hashtags': ['#Microplásticos', '#Saúde', '#Ciência', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/microplasticos_cadeia_01.png'},
 {'tema': 'Camuflagem no reino animal',
  'pergunta': 'A camuflagem serve apenas para defesa e nunca ajuda um animal a capturar alimento.',
  'verdadeiro': False,
  'explicacao': 'A camuflagem também pode ajudar predadores a se aproximarem da presa sem serem '
                'percebidos.',
  'legenda': 'A camuflagem pode ajudar na caça também?',
  'hashtags': ['#VidaSelvagem', '#Animais', '#Curiosidades', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/camuflagem_animais_01.png'},
 {'tema': 'Sono, cérebro e memória',
  'pergunta': 'O sono participa de processos relacionados à consolidação da memória.',
  'verdadeiro': True,
  'explicacao': 'O sono está ligado à organização e consolidação de memórias, embora aprender '
                'também dependa de outros fatores.',
  'legenda': 'O cérebro continua trabalhando enquanto a gente dorme?',
  'hashtags': ['#Sono', '#Cérebro', '#Memória', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/sono_memoria_01.png'},
 {'tema': 'Como checar uma informação',
  'pergunta': 'Ter muitos seguidores garante que um perfil compartilhe informações verdadeiras.',
  'verdadeiro': False,
  'explicacao': 'Popularidade não comprova precisão; é importante verificar a fonte, a evidência e '
                'a confirmação independente.',
  'legenda': 'Popularidade é a mesma coisa que confiabilidade?',
  'hashtags': ['#Checagem', '#Internet', '#Informação', '#JuhQuiz'],
  'imagem': 'imagens_perguntas/checagem_informacao_01.png'}]
