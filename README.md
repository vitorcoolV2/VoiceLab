# Coqui TTS Server

Servidor TTS (Text-to-Speech) baseado no Coqui TTS com suporte a múltiplos idiomas e modelos.

## 🚀 Instalação Rápida

### 1. Instalar dependências e ambiente
```bash
cd coqui-tts
./scripts/install.sh
```

### 2. Executar o servidor
```bash
./scripts/run.sh
```

## 📋 Requisitos do Sistema

### Dependências do Sistema
- **ffmpeg** - Processamento de áudio
- **sox** - Manipulação de áudio
- **espeak-ng** - Síntese de fala

### Dependências Python
- **TTS>=0.22.0** - Framework principal
- **torch==2.5.1** - PyTorch
- **transformers==4.39.3** - Modelos de linguagem
- **whisper** - Reconhecimento de fala
- **fastapi** - Servidor web
- **uvicorn** - Servidor ASGI

## 🔧 Configuração

### Ficheiro de Configuração
Edite `config.env` para personalizar as configurações:

```bash
# Configurações do Miniconda
MINICONDA_SSD=/media/vitor/ssd990/miniconda3
ENV_NAME=coqui-tts

# Configurações do servidor
TTS_SERVER_HOST=0.0.0.0
TTS_SERVER_PORT=8000

# Modelos padrão
DEFAULT_TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
DEFAULT_WHISPER_MODEL=base
```

## 📥 Modelos TTS

### Modelos Incluídos
- **XTTS v2** - Multilingue, alta qualidade
- **Mai (Português)** - Modelo específico para português
- **LJSpeech (Inglês)** - Voz feminina em inglês
- **VCTK (Inglês)** - Múltiplas vozes em inglês
- **YourTTS** - Clone de voz

### Download Manual de Modelos
```bash
./scripts/download_models.sh
```

## 🎯 Uso

### Ativar Ambiente Manualmente
```bash
conda activate coqui-tts
```

### Executar Servidor
```bash
./scripts/run.sh
```

### Aceder à API
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

## 🔍 Verificação de Modelos

O script `run.sh` verifica automaticamente se os modelos necessários estão disponíveis:

```bash
./scripts/run.sh
```

Se algum modelo estiver em falta, execute:
```bash
./scripts/download_models.sh
```

## 📁 Estrutura de Ficheiros

```
coqui-tts/
├── environment.yml          # Dependências Conda
├── config.env              # Configurações
├── scripts/
│   ├── install.sh          # Instalação completa
│   ├── run.sh              # Execução do servidor
│   └── download_models.sh  # Download de modelos
└── src/
    └── tts_server.py       # Servidor principal
```

## 🛠️ Solução de Problemas

### Erro: "No such file or directory: tts_models"
Execute o download de modelos:
```bash
./scripts/download_models.sh
```

### Erro: "Conda not found"
Verifique se o Miniconda está instalado e no PATH:
```bash
which conda
```

### Erro: "Permission denied"
Torne os scripts executáveis:
```bash
chmod +x scripts/*.sh
```

## 📊 Cache e Armazenamento

Os modelos são armazenados em:
- **TTS Cache:** `/media/vitor/ssd990/cache/tts`
- **Whisper Cache:** `/media/vitor/ssd990/cache/whisper`
- **Logs:** `/media/vitor/ssd990/logs/coqui-tts.log`

## 🔄 Atualizações

Para atualizar o ambiente:
```bash
conda env update -f environment.yml --prune
```

## 📝 Logs

Os logs são guardados em:
- **Ficheiro:** `/media/vitor/ssd990/logs/coqui-tts.log`
- **Nível:** INFO (configurável em `config.env`) 

## 🗣️ Gestão de Speakers (Vozes Personalizadas)

O servidor permite registar, listar, atualizar e remover speakers (vozes personalizadas) de forma persistente.

### Endpoints principais

| Ação         | Endpoint                | Método  | Descrição                        |
|--------------|-------------------------|---------|----------------------------------|
| Registar     | /speaker/register       | POST    | Regista novo speaker             |
| Atualizar    | /speaker/update         | POST    | Atualiza speaker existente       |
| Remover      | /speaker/delete         | DELETE  | Remove speaker                   |
| Listar       | /speaker/list           | GET     | Lista todos os speakers          |

### Exemplos de uso

#### Registar um speaker
```bash
curl -X POST http://localhost:8000/speaker/register \
  -F "name=joana" \
  -F "audio_file=@/caminho/para/joana.wav" \
  -F "lang=pt" -F "desc=Voz Joana demo"
```

#### Listar speakers
```bash
curl http://localhost:8000/speaker/list
```

#### Atualizar um speaker
```bash
curl -X POST http://localhost:8000/speaker/update \
  -F "name=joana" \
  -F "desc=Nova descrição" \
  -F "audio_file=@/caminho/para/novo_joana.wav"
```

#### Remover um speaker
```bash
curl -X DELETE http://localhost:8000/speaker/delete \
  -F "name=joana"
```

#### Exemplo em Python (requests)
```python
import requests

# Registar
with open("joana.wav", "rb") as f:
    files = {"audio_file": f}
    data = {"name": "joana", "lang": "pt", "desc": "Voz Joana demo"}
    r = requests.post("http://localhost:8000/speaker/register", files=files, data=data)
    print(r.json())

# Listar
r = requests.get("http://localhost:8000/speaker/list")
print(r.json())

# Atualizar
with open("novo_joana.wav", "rb") as f:
    files = {"audio_file": f}
    data = {"name": "joana", "desc": "Nova descrição"}
    r = requests.post("http://localhost:8000/speaker/update", files=files, data=data)
    print(r.json())

# Remover
r = requests.request("DELETE", "http://localhost:8000/speaker/delete", data={"name": "joana"})
print(r.json())
```

- Todos os endpoints retornam JSON.
- Os campos extra enviados no form são guardados como propriedades do speaker.
- O ficheiro de áudio é obrigatório no registo e opcional na atualização. 

## cuDNN Setup & Compliance

Due to NVIDIA licensing, cuDNN binaries are **not distributed** in this repository.

**To enable GPU acceleration:**
1. Download cuDNN for your CUDA version from: https://developer.nvidia.com/cudnn
2. Extract the contents into `coqui-tts/cuda/` so that you have:
   - `coqui-tts/cuda/include/cudnn.h`
   - `coqui-tts/cuda/lib64/libcudnn*.so*`
3. (Optional) Run `scripts/install_cudnn.sh` to set up the environment.

**You must accept NVIDIA’s terms to use cuDNN.** 