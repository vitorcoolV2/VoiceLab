# 🎛️ GPU Coexistence Guide: Coqui TTS + Ollama Phi-3

Este guia explica como configurar o Coqui TTS para coexistir com Ollama Phi-3 na mesma GPU NVIDIA GeForce RTX 3060.

## 📊 Situação Atual

- **GPU**: NVIDIA GeForce RTX 3060 (12GB VRAM)
- **Coqui TTS**: ~2.1GB VRAM (modo coexistência)
- **Ollama Phi-3**: ~2-4GB VRAM (estimado)
- **Sistema**: ~100MB VRAM
- **Total Disponível**: ~5.7GB para outros processos

## 🎯 Configurações Disponíveis

### 1. 🚀 **Speed Mode** (Dedicated GPU)
**Use quando**: Ollama não está a correr ou precisa de máxima performance

```bash
python scripts/switch_config.py speed
```

**Configurações**:
- GPU Memory: 85% (10.4GB)
- Batch Size: 4
- Audio Quality: Medium
- Workers: 2
- Performance: ~15-18 segundos

### 2. 🤝 **Coexistence Mode** (Shared GPU)
**Use quando**: Ollama Phi-3 está a correr

```bash
python scripts/switch_config.py coexistence
```

**Configurações**:
- GPU Memory: 30% (3.7GB)
- Batch Size: 1
- Audio Quality: Low
- Workers: 1
- Performance: ~17-20 segundos

## 🔄 Como Alternar Configurações

### Detecção Automática
```bash
python scripts/switch_config.py
```
O script detecta automaticamente se o Ollama está a correr e recomenda o modo apropriado.

### Alternância Manual
```bash
# Para coexistência com Ollama
python scripts/switch_config.py coexistence

# Para velocidade máxima
python scripts/switch_config.py speed
```

## 📈 Performance Comparison

| Mode | GPU Memory | Batch Size | Quality | Time | Use Case |
|------|------------|------------|---------|------|----------|
| **Speed** | 85% (10.4GB) | 4 | Medium | ~17s | Dedicated GPU |
| **Coexistence** | 30% (3.7GB) | 1 | Low | ~18s | Shared with Ollama |

## 🛠️ Otimizações Aplicadas

### Para Coexistência:
1. **GPU Memory Fraction**: 30% (vs 85% no speed mode)
2. **Batch Size**: 1 (vs 4 no speed mode)
3. **Audio Quality**: Low (vs Medium no speed mode)
4. **Sample Rate**: 16kHz (reduzido de 22kHz)
5. **Workers**: 1 (vs 2 no speed mode)
6. **Whisper Model**: Tiny (mais rápido)

### Para Speed:
1. **GPU Memory Fraction**: 85% (máximo uso)
2. **Batch Size**: 4 (processamento paralelo)
3. **Audio Quality**: Medium (melhor qualidade)
4. **Workers**: 2 (múltiplos workers)
5. **Queue Size**: 30 (maior capacidade)

## 🔍 Monitorização

### Verificar Uso da GPU
```bash
nvidia-smi
```

### Verificar Status do Servidor
```bash
curl -s http://localhost:8000/health
```

### Verificar Se Ollama Está a Correr
```bash
pgrep ollama
```

## 🚨 Troubleshooting

### Problema: GPU Out of Memory
**Solução**: Mudar para modo coexistência
```bash
python scripts/switch_config.py coexistence
```

### Problema: Performance Lenta
**Solução**: Verificar se Ollama está a usar muita memória
```bash
nvidia-smi
# Se Ollama usar >4GB, considere parar temporariamente
```

### Problema: Servidor Não Inicia
**Solução**: Reduzir ainda mais a memória GPU
```bash
# Editar config/settings_coexistence.yaml
# Mudar gpu_memory_fraction: 0.2 (20%)
```

## 📋 Checklist de Configuração

### Para Coexistência:
- [ ] Ollama Phi-3 instalado e configurado
- [ ] Executar `python scripts/switch_config.py coexistence`
- [ ] Verificar `nvidia-smi` para confirmar uso de memória
- [ ] Testar clonagem de voz
- [ ] Verificar se Ollama ainda funciona

### Para Speed:
- [ ] Parar Ollama se necessário
- [ ] Executar `python scripts/switch_config.py speed`
- [ ] Verificar performance
- [ ] Testar clonagem de voz

## 🎯 Recomendações

### Para Desenvolvimento:
- Use **Coexistence Mode** para ter ambos os serviços disponíveis
- A qualidade de áudio é suficiente para testes

### Para Produção:
- Use **Speed Mode** para máxima qualidade e velocidade
- Considere parar Ollama temporariamente se necessário

### Para Demonstrações:
- Use **Coexistence Mode** para mostrar ambas as funcionalidades
- A diferença de qualidade é mínima para a maioria dos casos

## 📊 Backup e Restore

### Backup Automático
O script cria automaticamente backups antes de alternar:
```
config/settings_backup_1752708810.yaml
```

### Restore Manual
```bash
cp config/settings_backup_1752708810.yaml config/settings.yaml
```

## 🔧 Configurações Avançadas

### Ajustar Memória GPU
Editar `config/settings_coexistence.yaml`:
```yaml
performance:
  gpu_memory_fraction: 0.25  # 25% em vez de 30%
```

### Ajustar Qualidade de Áudio
```yaml
audio:
  quality: low      # low, medium, high
  sample_rate: 16000  # 16000, 22050, 44100
```

## ✅ Conclusão

Com estas configurações, consegue:
- ✅ Correr Coqui TTS e Ollama Phi-3 simultaneamente
- ✅ Manter performance aceitável (~18s vs ~17s)
- ✅ Alternar facilmente entre modos
- ✅ Monitorizar uso de recursos
- ✅ Manter qualidade suficiente para a maioria dos casos

A diferença de performance é mínima (1-2 segundos), mas a flexibilidade de ter ambos os serviços disponíveis é valiosa para desenvolvimento e demonstrações. 