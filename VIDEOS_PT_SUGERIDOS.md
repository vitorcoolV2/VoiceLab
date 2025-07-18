# 🇧🇷 Vídeos Sugeridos para Amostras de Português

## 🎯 Melhores Canais Brasileiros para Amostras

### 📺 **Canais de Notícias (Fala Profissional)**
- **Globo News**: https://www.youtube.com/@globo
- **Band News**: https://www.youtube.com/@bandnews
- **CNN Brasil**: https://www.youtube.com/@cnnbrasil
- **Record News**: https://www.youtube.com/@recordnews

### 🎙️ **Podcasts Populares (Fala Natural)**
- **Flow Podcast**: https://www.youtube.com/@flowpodcast
- **PodPah**: https://www.youtube.com/@podpah
- **Inteligência Ltda**: https://www.youtube.com/@inteligencialtda
- **Nerdcast**: https://www.youtube.com/@jovemnerd

### 📚 **Canais Educacionais (Fala Clara)**
- **Manual do Mundo**: https://www.youtube.com/@manualdomundo
- **Canal Nostalgia**: https://www.youtube.com/@CanalNostalgia
- **Ciência Todo Dia**: https://www.youtube.com/@cienciatododia
- **Pirula**: https://www.youtube.com/@pirulla

### 🎭 **Canais de Entretenimento (Fala Expressiva)**
- **Felipe Neto**: https://www.youtube.com/@felipeneto
- **Whindersson Nunes**: https://www.youtube.com/@whinderssonnunes
- **Lucas Inutilismo**: https://www.youtube.com/@lucasinutilismo

## 🎯 **Vídeos Específicos Recomendados**

### **1. Notícias (Fala Profissional)**
```
URL: https://www.youtube.com/watch?v=VIDEO_ID_NOTICIAS
Parâmetros: --start 30 --duration 25
Texto: "Bom dia! Aqui estão as principais notícias do dia. O Brasil enfrenta novos desafios."
```

### **2. Podcast (Fala Natural)**
```
URL: https://www.youtube.com/watch?v=VIDEO_ID_PODCAST
Parâmetros: --start 60 --duration 30
Texto: "Olá pessoal! Bem-vindos ao nosso podcast. Hoje vamos conversar sobre tecnologia."
```

### **3. Educacional (Fala Clara)**
```
URL: https://www.youtube.com/watch?v=VIDEO_ID_EDUCACIONAL
Parâmetros: --start 45 --duration 25
Texto: "Hoje vamos aprender sobre ciência. A física quântica é fascinante."
```

## 🚀 **Como Usar**

### **1. Escolha um vídeo da lista acima**

### **2. Use o comando:**
```bash
python tools/audio_utils/youtube_to_voice_sample.py \
  --url "URL_DO_VIDEO" \
  --text "Olá! Esta é uma demonstração de síntese de voz em português brasileiro." \
  --output amostra_pt \
  --duration 25 \
  --start 30 \
  --language pt-br
```

### **3. Parâmetros recomendados por tipo:**

**Notícias:**
- `--start 30` (evita introduções)
- `--duration 25` (fala profissional)

**Podcasts:**
- `--start 60` (evita introduções longas)
- `--duration 30` (fala natural)

**Educacional:**
- `--start 45` (evita introduções)
- `--duration 25` (fala clara)

## 📝 **Textos Sugeridos para Teste**

### **Texto 1 (Formal):**
"Bom dia! Esta é uma demonstração de síntese de voz em português brasileiro. A qualidade deve estar muito boa agora."

### **Texto 2 (Natural):**
"Olá pessoal! Como vocês estão? Espero que estejam tendo um ótimo dia. Esta é uma amostra de voz clonada."

### **Texto 3 (Educacional):**
"A inteligência artificial está revolucionando a forma como interagimos com a tecnologia. Cada dia surgem novas possibilidades."

### **Texto 4 (Expressivo):**
"O português é uma língua muito rica e expressiva. Temos muitas palavras bonitas e uma pronúncia única."

## 🎯 **Dicas para Melhor Qualidade**

### **✅ Escolha vídeos com:**
- Fala clara e pausada
- Sem música de fundo
- Boa qualidade de áudio
- Duração mínima de 30 segundos

### **❌ Evite vídeos com:**
- Música de fundo
- Ruído excessivo
- Fala muito rápida
- Muitas pessoas falando ao mesmo tempo

### **🔧 Configuração ideal:**
- **`--start`**: 30-60 segundos (evita introduções)
- **`--duration`**: 20-30 segundos (tempo ideal)
- **`--language`**: pt-br (português brasileiro)

## 🚀 **Próximos Passos**

1. **Escolha um vídeo** da lista acima
2. **Teste com diferentes textos** para verificar qualidade
3. **Compare resultados** entre diferentes canais
4. **Use as melhores amostras** para melhorar o TTS

## 📞 **Como Encontrar URLs Atuais**

1. **Vá ao YouTube**
2. **Procure pelo canal** desejado
3. **Escolha um vídeo recente** (últimos 6 meses)
4. **Copie a URL** da barra de endereços
5. **Teste com a ferramenta**

**Exemplo de busca:**
- "Globo News ao vivo"
- "Flow Podcast recente"
- "Manual do Mundo novo vídeo" 