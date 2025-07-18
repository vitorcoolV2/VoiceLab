# Guia de Variáveis de Ambiente - Coqui TTS

Este guia documenta todas as variáveis de ambiente usadas no projeto Coqui TTS e como configurá-las para máxima portabilidade e flexibilidade.

## 📋 Variáveis de Ambiente Principais

### 1. **COQUI_TTS_DOWNLOADS**
- **Descrição**: Diretório para armazenar ficheiros descarregados (vídeos, amostras de voz)
- **Valor padrão**: `downloads`
- **Exemplo**: `/media/vitor/ssd990/home-backup/coqui-downloads`
- **Uso**: YouTube voice cloner, testes de clonagem, amostras de voz

### 2. **COQUI_TTS_OUTPUTS**
- **Descrição**: Diretório para ficheiros de saída (áudio sintetizado, relatórios)
- **Valor padrão**: `output`
- **Exemplo**: `/media/vitor/ssd990/home-backup/coqui-outputs`
- **Uso**: Servidor TTS, scripts de processamento, demonstrações

### 3. **COQUI_TTS_HOME**
- **Descrição**: Diretório principal dos modelos TTS
- **Valor padrão**: Configurado no `settings.yaml`
- **Exemplo**: `/media/vitor/ssd990/home-backup/coqui-models`
- **Uso**: Servidor TTS, migração de modelos, cache de modelos

### 4. **TTS_CACHE_DIR**
- **Descrição**: Diretório de cache para modelos e ficheiros temporários
- **Valor padrão**: Configurado no `settings.yaml`
- **Exemplo**: `/media/vitor/ssd990/ai_models/cache`
- **Uso**: Cache de modelos, ficheiros temporários

## 🔧 Configuração

### 1. Ficheiro `.env`
Crie um ficheiro `.env` na raiz do projeto:

```bash
# Diretórios principais
COQUI_TTS_DOWNLOADS=/media/vitor/ssd990/home-backup/coqui-downloads
COQUI_TTS_OUTPUTS=/media/vitor/ssd990/home-backup/coqui-outputs
COQUI_TTS_HOME=/media/vitor/ssd990/home-backup/coqui-models
TTS_CACHE_DIR=/media/vitor/ssd990/ai_models/cache

# Configurações opcionais
EXTERNAL_SSD_PATH=/media/vitor/ssd990
WHISPER_CACHE_DIR=/media/vitor/ssd990/ai_models/whisper
```

### 2. Carregamento Automático
O projeto carrega automaticamente as variáveis de ambiente:
- Do ficheiro `.env` (se existir)
- Das variáveis de ambiente do sistema
- Com fallback para valores padrão

## 📁 Estrutura de Diretórios Recomendada

```
/media/vitor/ssd990/
├── home-backup/
│   ├── coqui-downloads/     # COQUI_TTS_DOWNLOADS
│   ├── coqui-outputs/       # COQUI_TTS_OUTPUTS
│   └── coqui-models/        # COQUI_TTS_HOME
└── ai_models/
    └── cache/               # TTS_CACHE_DIR
```

## 🛠️ Scripts e Utilitários Atualizados

### Scripts Principais
- ✅ `youtube_voice_cloner.py` - Usa `COQUI_TTS_DOWNLOADS`
- ✅ `coqui_tts_client.py` - Usa `COQUI_TTS_OUTPUTS`
- ✅ `tts_server.py` - Usa todas as variáveis
- ✅ `performance_optimizer.py` - Usa `COQUI_TTS_OUTPUTS`

### Utilitários de Processamento
- ✅ `simple_voice_processor.py` - Usa `COQUI_TTS_OUTPUTS`
- ✅ `voice_sample_preprocessor.py` - Usa `COQUI_TTS_OUTPUTS`
- ✅ `simple_clone_optimizer.py` - Usa `COQUI_TTS_OUTPUTS`

### Testes e Demonstrações
- ✅ `xtts_customization_demo.py` - Usa `COQUI_TTS_OUTPUTS`
- ✅ `migrate_models_to_ssd.py` - Usa `COQUI_TTS_HOME` e `TTS_CACHE_DIR`

## 🔍 Verificação da Configuração

### Teste de Configuração
```bash
# Verificar se as variáveis estão carregadas
python -c "
import os
print('📋 Variáveis de Ambiente:')
print(f'   COQUI_TTS_DOWNLOADS: {os.environ.get(\"COQUI_TTS_DOWNLOADS\", \"NÃO DEFINIDA\")}')
print(f'   COQUI_TTS_OUTPUTS: {os.environ.get(\"COQUI_TTS_OUTPUTS\", \"NÃO DEFINIDA\")}')
print(f'   COQUI_TTS_HOME: {os.environ.get(\"COQUI_TTS_HOME\", \"NÃO DEFINIDA\")}')
print(f'   TTS_CACHE_DIR: {os.environ.get(\"TTS_CACHE_DIR\", \"NÃO DEFINIDA\")}')
"
```

### Teste do Servidor
```bash
# Verificar configuração do servidor
python -c "
import sys; sys.path.append('src')
from tts_server import load_config
config = load_config()
print('✅ Configuração do Servidor:')
print(f'   Output: {config[\"output\"][\"path\"]}')
print(f'   Downloads: {config[\"downloads\"][\"path\"]}')
print(f'   Models: {config[\"models\"][\"path\"]}')
print(f'   Cache: {config[\"models\"][\"cache_dir\"]}')
"
```

## 🚀 Benefícios

### 1. **Portabilidade**
- Funciona em diferentes máquinas sem alterar código
- Fácil migração entre sistemas
- Configuração centralizada

### 2. **Flexibilidade**
- Pode usar diferentes diretórios para diferentes propósitos
- Suporte a múltiplos ambientes (dev, prod, test)
- Configuração dinâmica

### 3. **Manutenibilidade**
- Código mais limpo sem paths hardcoded
- Fácil alteração de configurações
- Documentação clara

### 4. **Consistência**
- Todos os scripts usam as mesmas variáveis
- Comportamento previsível
- Menos erros de configuração

## 🔧 Migração de Projetos Existentes

### 1. Backup
```bash
# Fazer backup dos diretórios atuais
cp -r downloads downloads_backup
cp -r output output_backup
```

### 2. Configurar Variáveis
```bash
# Editar .env com os novos paths
nano .env
```

### 3. Migrar Dados
```bash
# Mover dados para novos diretórios
mv downloads_backup/* $COQUI_TTS_DOWNLOADS/
mv output_backup/* $COQUI_TTS_OUTPUTS/
```

### 4. Testar
```bash
# Executar testes para verificar funcionamento
python tests/voice_cloning/test_portuguese_cloning.py
```

## 📝 Notas Importantes

1. **Fallbacks**: Todos os scripts têm fallbacks para valores padrão
2. **Criação Automática**: Diretórios são criados automaticamente se não existirem
3. **Logs**: O servidor regista quais variáveis estão a ser usadas
4. **Compatibilidade**: Mantém compatibilidade com configurações antigas

## 🆘 Resolução de Problemas

### Problema: Variáveis não carregadas
```bash
# Verificar se .env existe
ls -la .env

# Carregar manualmente
source .env
```

### Problema: Diretórios não encontrados
```bash
# Criar diretórios manualmente
mkdir -p $COQUI_TTS_DOWNLOADS
mkdir -p $COQUI_TTS_OUTPUTS
mkdir -p $COQUI_TTS_HOME
mkdir -p $TTS_CACHE_DIR
```

### Problema: Permissões
```bash
# Verificar permissões
ls -la $COQUI_TTS_DOWNLOADS
ls -la $COQUI_TTS_OUTPUTS

# Corrigir se necessário
chmod 755 $COQUI_TTS_DOWNLOADS
chmod 755 $COQUI_TTS_OUTPUTS
```

---

**✅ Status**: Todas as variáveis de ambiente implementadas e testadas
**📅 Última atualização**: 2025-07-17
**🔧 Versão**: 1.0.0 