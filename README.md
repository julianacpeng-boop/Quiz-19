# Juh Quiz — Quiz-19 Verdadeiro ou Falso 3D

O Quiz-19 gera um vídeo vertical por afirmação, com o fluxo do Quiz-13 e o novo layout 3D aprovado: caderno em relevo, tema em destaque, caixa da afirmação, imagem opcional, opções verde e vermelha, revelação da resposta e explicação digitada.

## Como fica o vídeo

- Formato vertical 1080 × 1920 (9:16).
- Cabeçalho vermelho com caderno espiralado em 3D e marca Juh Quiz.
- Tema exibido em uma etiqueta sobre a caixa da afirmação.
- Imagem dentro de moldura arredondada; quando `imagem` é `None`, a moldura some e as áreas de texto e resposta aumentam.
- Botões Verdadeiro (verde) e Falso (vermelho) lado a lado durante a pergunta.
- A contagem tem três segundos. Depois, a opção errada desaparece e a resposta correta permanece na primeira posição.
- A explicação aparece com animação de digitação enquanto a voz narra.
- Perguntas e explicações ajustam a fonte ao espaço. Se o texto não couber com leitura confortável, a execução para com uma mensagem antes de salvar um vídeo cortado.
- Cada TXT começa com `CAPA_SEGUNDOS=2` e contém a legenda e até quatro hashtags relacionadas.

## Voz e pastas

O gerador usa `pt-BR-AntonioNeural` a `+10%`, seguindo o fluxo do Quiz-13. O serviço de voz é repetido em caso de falha e usa a voz local em português como alternativa. Não é necessária chave Azure.

```text
gerar_vf.py
dados_vf.py
requirements-vf.txt
imagens_perguntas/
.github/workflows/gerar-vf.yml
```

As 15 perguntas e imagens da execução usada como referência foram copiadas do Quiz-13 para teste. As imagens compatíveis são PNG, JPG, JPEG e WebP. Mantenha-as dentro de `imagens_perguntas/`.

## Cadastrar perguntas

Edite `dados_vf.py` e informe `tema`, `pergunta`, `verdadeiro`, `explicacao`, `imagem`, `legenda` e `hashtags`. O caminho de `imagem` é relativo à raiz do repositório e pode ser `None`.

```python
{
    "tema": "ANIMAIS",
    "pergunta": "O polvo tem três corações?",
    "verdadeiro": True,
    "explicacao": "O polvo tem três corações: dois enviam sangue às brânquias e um ao restante do corpo.",
    "imagem": "imagens_perguntas/polvo_tres_coracoes.jpg",
    "legenda": "Você sabia que o polvo tem três corações?",
    "hashtags": ["#Polvo", "#Animais", "#Curiosidades", "#JuhQuiz"],
},
```

## Google Drive e GitHub Actions

1. No Quiz-19, abra **Settings → Secrets and variables → Actions**.
2. Adicione o secret `RCLONE_DRIVE_TOKEN` com o JSON do token rclone usado nos quizzes anteriores.
3. Abra **Actions → Quiz-19 — Verdadeiro ou Falso 3D → Run workflow**.
4. O workflow salva MP4 e TXT no Drive em `saida/Juh-Quiz-19/verdadeiro-ou-falso/execucao-ID/` e também os disponibiliza como artefato do Actions por 30 dias.

O token não deve ser colocado no repositório, no README ou em `dados_vf.py`.

## Gerar localmente

Instale Python 3.11, FFmpeg, espeak-ng e os pacotes do projeto:

```bash
python -m pip install -r requirements-vf.txt
python gerar_vf.py
```

Para enviar ao Drive numa execução local, configure o rclone e execute:

```bash
python gerar_vf.py --enviar-drive
```
