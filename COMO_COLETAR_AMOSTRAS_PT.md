# 🇧🇷 Como Coletar Amostras de Áudio em Português

## 🛠️ Ferramentas Disponíveis

O projeto já possui ferramentas prontas em `tools/audio_utils/`:

- `youtube_to_voice_sample.py` - Baixa vídeo e extrai amostra de voz
- `youtube_voice_cloner.py` - Clona voz usando YourTTS
- `audio_player.py` - Reproduz áudio
- `download_high_quality.py` - Baixa áudio de alta qualidade

## 📋 Como Usar

### 1. Encontrar um Vídeo em Português

Procure por vídeos com:
- ✅ Fala clara e pausada
- ✅ Sem música de fundo
- ✅ Duração mínima de 30 segundos
- ✅ Boa qualidade de áudio

**Sugestões:**
- Podcasts em português
- Notícias brasileiras
- Aulas online
- Entrevistas
- Documentários

### 2. Usar a Ferramenta Principal

```bash
python tools/audio_utils/youtube_to_voice_sample.py \
  --url "URL_DO_VIDEO" \
  --text "Texto para sintetizar em português" \
  --output nome_amostra \
  --duration 25 \
  --start 15 \
  --language pt-br
```

### 3. Parâmetros Importantes

- `--url`: URL do vídeo do YouTube
- `--text`: Texto em português para testar
- `--output`: Nome base dos arquivos (sem extensão)
- `--duration`: Duração da amostra em segundos (padrão: 30)
- `--start`: Segundo inicial para extrair (padrão: 10)
- `--language`: Idioma (padrão: pt-br)

### 4. Exemplo Prático

```bash
python tools/audio_utils/youtube_to_voice_sample.py \
  --url "https://www.youtube.com/watch?v=SEU_VIDEO_PT" \
  --text "Olá! Esta é uma demonstração de síntese de voz em português brasileiro. A qualidade deve estar muito boa agora." \
  --output minha_amostra_pt \
  --duration 25 \
  --start 20 \
  --language pt-br
```

## 📁 Arquivos Gerados

A ferramenta gera 3 arquivos:

1. **`nome_amostra.wav`** - Áudio original baixado
2. **`nome_amostra_voice_sample.wav`** - Amostra de voz extraída
3. **`nome_amostra_cloned.wav`** - Áudio sintetizado em português

## 🎯 Dicas para Melhor Qualidade

### Escolha do Vídeo:
- ✅ Fala clara e natural
- ✅ Sem ruído de fundo
- ✅ Sem música
- ✅ Boa qualidade de áudio
- ✅ Duração suficiente (30s+)

### Configuração dos Parâmetros:
- **`--start`**: Escolha um momento com fala clara
- **`--duration`**: 20-30 segundos é ideal
- **`--text`**: Use frases naturais em português

### Textos Sugeridos para Teste:

1. "Olá! Esta é uma demonstração de síntese de voz em português brasileiro. A qualidade deve estar muito boa agora."

2. "Bom dia! Como você está? Espero que esteja tendo um ótimo dia. Esta é uma amostra de voz clonada."

3. "A inteligência artificial está revolucionando a forma como interagimos com a tecnologia. Cada dia surgem novas possibilidades."

4. "O português é uma língua muito rica e expressiva. Temos muitas palavras bonitas e uma pronúncia única."

## 🔧 Ferramentas Adicionais

### Reproduzir Áudio:
```bash
python tools/audio_utils/audio_player.py nome_amostra_cloned.wav
```

### Analisar Voz:
```bash
curl -X POST "http://localhost:8000/analyze_voice" \
  -F "audio_file=@nome_amostra_voice_sample.wav"
```

### Usar YourTTS Diretamente:
```bash
python tools/audio_utils/youtube_voice_cloner.py
```

## 🚀 Próximos Passos

1. **Colete várias amostras** de diferentes vozes
2. **Teste diferentes textos** para verificar qualidade
3. **Compare resultados** entre diferentes vídeos
4. **Use as melhores amostras** para melhorar o TTS

## ⚠️ Observações

- A ferramenta usa YourTTS para clonagem
- O modelo específico de português (`tts_models/pt/cv/vits`) é usado para síntese
- A qualidade depende muito da amostra original
- Sempre teste com diferentes vídeos para encontrar os melhores 