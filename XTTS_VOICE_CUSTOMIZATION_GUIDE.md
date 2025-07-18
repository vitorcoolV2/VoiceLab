# 🎭 XTTS v2 Voice Customization Guide

Guia completo sobre as capacidades de customização de voz do modelo **XTTS v2** (eXtended Text-To-Speech v2).

## 🎯 Visão Geral do XTTS v2

O **XTTS v2** é um modelo de síntese de voz avançado que oferece:
- ✅ **Clonagem de voz** a partir de amostras de áudio
- ✅ **Suporte multilingue** (português, inglês, espanhol, etc.)
- ✅ **Customização avançada** de parâmetros vocais
- ✅ **Qualidade de voz humana** muito natural
- ✅ **Controle fino** sobre características vocais

## 🎛️ Parâmetros de Customização Disponíveis

### 1. **Parâmetros Básicos de Voz**

#### **Speed (Velocidade)**
```python
speed: float = 1.0  # Range: 0.5 - 2.0
```
- **0.5**: Muito lento (dramático)
- **0.8**: Lento (calmo)
- **1.0**: Normal
- **1.2**: Rápido (energético)
- **1.5**: Muito rápido (excitado)
- **2.0**: Máximo (para efeitos especiais)

#### **Pitch (Tom)**
```python
pitch: float = 1.0  # Range: 0.5 - 2.0
```
- **0.5**: Tom muito baixo (voz masculina profunda)
- **0.8**: Tom baixo (voz masculina)
- **1.0**: Tom normal
- **1.2**: Tom alto (voz feminina)
- **1.5**: Tom muito alto (voz feminina aguda)
- **2.0**: Máximo (efeitos especiais)

#### **Volume**
```python
volume: float = 1.0  # Range: 0.1 - 3.0
```
- **0.1**: Muito baixo (sussurro)
- **0.5**: Baixo (voz suave)
- **1.0**: Normal
- **1.5**: Alto (enfático)
- **2.0**: Muito alto (dramático)
- **3.0**: Máximo (para efeitos especiais)

### 2. **Estilos de Voz**

#### **Voice Styles Disponíveis**
```python
voice_style: str = "normal"  # Opções disponíveis
```

| Estilo | Descrição | Características |
|--------|-----------|-----------------|
| **normal** | Voz padrão | Tom natural, velocidade média |
| **emphatic** | Enfático | Mais forte, pausas marcadas |
| **excited** | Entusiástico | Rápido, tom alto, energético |
| **calm** | Calmo | Lento, tom baixo, relaxado |
| **whisper** | Sussurro | Muito baixo, íntimo |

### 3. **Parâmetros de Clonagem**

#### **Amostra de Voz (Speaker WAV)**
```python
speaker_wav: str = "path/to/voice_sample.wav"
```
- **Duração ideal**: 10-30 segundos
- **Qualidade**: Sem ruído, sem música
- **Formato**: WAV, 16kHz ou 22kHz
- **Conteúdo**: Fala clara e natural

#### **Idioma**
```python
language: str = "pt"  # Códigos suportados
```
- **pt**: Português
- **pt-br**: Português brasileiro
- **pt-pt**: Português europeu
- **en**: Inglês
- **es**: Espanhol
- **fr**: Francês
- **de**: Alemão
- **it**: Italiano
- **pl**: Polaco
- **tr**: Turco
- **ru**: Russo
- **ja**: Japonês
- **zh**: Chinês
- **ko**: Coreano

## 🎨 Exemplos Práticos de Customização

### 1. **Voz Feminina Portuguesa**
```python
# Configuração para voz feminina portuguesa
tts_args = {
    'text': 'Olá! Esta é uma demonstração de voz feminina em português.',
    'speaker_wav': 'portuguese_female_sample.wav',
    'language': 'pt',
    'speed': 1.1,        # Ligeiramente mais rápida
    'pitch': 1.2,        # Tom mais alto
    'volume': 1.0,       # Volume normal
    'voice_style': 'excited'  # Estilo energético
}
```

### 2. **Voz Masculina Profunda**
```python
# Configuração para voz masculina profunda
tts_args = {
    'text': 'Esta é uma voz masculina com tom profundo e autoridade.',
    'speaker_wav': 'deep_male_sample.wav',
    'language': 'pt',
    'speed': 0.8,        # Mais lenta
    'pitch': 0.7,        # Tom mais baixo
    'volume': 1.2,       # Volume mais forte
    'voice_style': 'emphatic'  # Estilo enfático
}
```

### 3. **Voz Calma e Relaxada**
```python
# Configuração para voz calma
tts_args = {
    'text': 'Esta é uma voz calma e relaxante para meditação.',
    'speaker_wav': 'calm_voice_sample.wav',
    'language': 'pt',
    'speed': 0.7,        # Muito lenta
    'pitch': 0.9,        # Tom ligeiramente baixo
    'volume': 0.8,       # Volume suave
    'voice_style': 'calm'  # Estilo calmo
}
```

### 4. **Voz Dramática**
```python
# Configuração para voz dramática
tts_args = {
    'text': 'Esta é uma voz dramática para narração de histórias!',
    'speaker_wav': 'dramatic_sample.wav',
    'language': 'pt',
    'speed': 0.9,        # Lenta para drama
    'pitch': 1.1,        # Tom ligeiramente alto
    'volume': 1.3,       # Volume forte
    'voice_style': 'emphatic'  # Estilo enfático
}
```

## 🔧 Implementação no Servidor

### 1. **Endpoint de Clonagem**
```python
@app.post("/clone_voice")
async def clone_voice(
    audio_file: UploadFile = File(...),
    text: str = Form(...),
    language: str = Form(None),
    model_name: str = Form(None)
):
    # Parâmetros XTTS v2
    tts_args = {
        'text': text,
        'file_path': str(output_path),
        'speaker_wav': str(temp_path)
    }
    if language:
        tts_args['language'] = language
    
    tts_instance.tts_to_file(**tts_args)
```

### 2. **Endpoint de Síntese**
```python
@app.post("/synthesize")
async def synthesize_speech(request: SynthesisRequest):
    synthesis_params = {
        "text": request.text,
        "file_path": str(output_path),
        "speed": request.speed,
        "pitch": request.pitch,
        "volume": request.volume
    }
    
    if request.language:
        synthesis_params["language"] = request.language
```

## 🎯 Técnicas Avançadas

### 1. **Combinação de Parâmetros**
```python
# Voz feminina energética para apresentações
config = {
    'speed': 1.2,        # Rápida
    'pitch': 1.3,        # Tom alto
    'volume': 1.1,       # Volume alto
    'voice_style': 'excited'
}

# Voz masculina autoritária para comandos
config = {
    'speed': 0.8,        # Lenta
    'pitch': 0.6,        # Tom baixo
    'volume': 1.4,       # Volume forte
    'voice_style': 'emphatic'
}
```

### 2. **Ajuste por Contexto**
```python
def get_voice_config(context):
    if context == "presentation":
        return {'speed': 1.1, 'pitch': 1.2, 'volume': 1.1}
    elif context == "storytelling":
        return {'speed': 0.9, 'pitch': 1.0, 'volume': 1.0}
    elif context == "command":
        return {'speed': 0.8, 'pitch': 0.7, 'volume': 1.3}
    else:
        return {'speed': 1.0, 'pitch': 1.0, 'volume': 1.0}
```

### 3. **Otimização de Qualidade**
```python
# Para máxima qualidade
high_quality_config = {
    'speed': 1.0,        # Velocidade natural
    'pitch': 1.0,        # Tom natural
    'volume': 1.0,       # Volume natural
    'voice_style': 'normal'
}

# Para velocidade
fast_config = {
    'speed': 1.3,        # Mais rápido
    'pitch': 1.0,        # Tom normal
    'volume': 1.0,       # Volume normal
    'voice_style': 'excited'
}
```

## 📊 Comparação de Qualidade

### **Qualidade vs Performance**
| Configuração | Qualidade | Velocidade | Uso de GPU |
|--------------|-----------|------------|------------|
| **Alta Qualidade** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Média Qualidade** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Baixa Qualidade** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

### **Estilos vs Naturalidade**
| Estilo | Naturalidade | Expressividade | Adequação |
|--------|--------------|----------------|-----------|
| **normal** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Geral |
| **emphatic** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Apresentações |
| **excited** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Energético |
| **calm** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Relaxamento |
| **whisper** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Íntimo |

## 🚀 Dicas de Otimização

### 1. **Para Melhor Qualidade**
- Use amostras de voz de alta qualidade (16kHz+)
- Mantenha parâmetros próximos do natural (0.8-1.2)
- Use o modo "normal" para máxima naturalidade
- Evite valores extremos de pitch e speed

### 2. **Para Performance**
- Use amostras de voz mais curtas (10-15s)
- Reduza a qualidade de áudio se necessário
- Use valores de speed mais altos (1.2-1.5)
- Considere o modo "excited" para mais energia

### 3. **Para Consistência**
- Mantenha os mesmos parâmetros para o mesmo speaker
- Use templates de configuração
- Documente as configurações que funcionam melhor
- Teste com diferentes textos

## 🎭 Casos de Uso Específicos

### **Educação**
```python
educational_config = {
    'speed': 0.9,        # Ligeiramente lento para clareza
    'pitch': 1.1,        # Tom ligeiramente alto
    'volume': 1.0,       # Volume normal
    'voice_style': 'emphatic'  # Enfático para importância
}
```

### **Narração**
```python
narration_config = {
    'speed': 0.8,        # Lento para drama
    'pitch': 1.0,        # Tom natural
    'volume': 1.1,       # Volume ligeiramente alto
    'voice_style': 'calm'  # Calmo para imersão
}
```

### **Comandos**
```python
command_config = {
    'speed': 0.7,        # Muito lento para clareza
    'pitch': 0.8,        # Tom baixo para autoridade
    'volume': 1.3,       # Volume forte
    'voice_style': 'emphatic'  # Enfático
}
```

## ✅ Conclusão

O **XTTS v2** oferece um controle muito fino sobre a customização de voz, permitindo:

- ✅ **Clonagem precisa** de vozes reais
- ✅ **Ajuste fino** de parâmetros vocais
- ✅ **Estilos variados** para diferentes contextos
- ✅ **Suporte multilingue** completo
- ✅ **Qualidade profissional** de áudio

Com estas capacidades, consegue criar vozes personalizadas para qualquer aplicação, desde educação até entretenimento, mantendo sempre a naturalidade e expressividade humana. 