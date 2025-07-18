# 📋 Guia de Scripts do Coqui TTS

Este documento explica as diferenças entre os scripts de inicialização e utilitários do projeto coqui-tts.

**📁 Localização:** Todos os scripts estão na pasta `scripts/`

## 🚀 Scripts de Inicialização

### `scripts/script_start.sh` - Script Principal
**Função:** Inicialização padrão do servidor TTS & Whisper

**Características:**
- ✅ Verifica e ativa ambiente conda local
- ✅ Para servidor já em execução
- ✅ Libera porta 8000 se ocupada
- ✅ Cria diretórios necessários (output, logs, downloads)
- ✅ Inicia servidor com Python local

**Uso:**
```bash
./scripts/script_start.sh
```

**Ideal para:** Desenvolvimento local e uso padrão

---

### `scripts/script_start_server.sh` - Script para SSD Externo
**Função:** Inicialização específica para ambiente no SSD externo

**Características:**
- ✅ Usa ambiente conda do SSD externo
- ✅ Configurado para GPU NVIDIA RTX 3060
- ✅ Caminho hardcoded para SSD externo
- ✅ Para servidor já em execução
- ✅ Libera porta 8000 se ocupada
- ✅ Cria diretórios necessários (output, logs, downloads)

**Uso:**
```bash
./scripts/script_start_server.sh
```

**Ideal para:** Produção com GPU e SSD externo

---

## 🔧 Scripts Utilitários

### `scripts/script_run_with_env.sh` - Executor de Comandos
**Função:** Executa comandos Python com ambiente do SSD externo

**Características:**
- ✅ Configura ambiente do SSD externo
- ✅ Aceita comandos como argumentos
- ✅ Flexível para qualquer comando Python

**Uso:**
```bash
./scripts/script_run_with_env.sh "script.py arg1 arg2"
./scripts/script_run_with_env.sh run_tests.py
./scripts/script_run_with_env.sh talk.py "Olá mundo"
```

**Ideal para:** Executar scripts específicos com ambiente correto

---

### `scripts/script_install.sh` - Instalação
**Função:** Instala dependências e configura ambiente

**Uso:**
```bash
./scripts/script_install.sh
```

---

### `scripts/script_migrate_to_ssd.sh` - Migração
**Função:** Move modelos para SSD externo

**Uso:**
```bash
./scripts/script_migrate_to_ssd.sh
```

---

### `scripts/script_setup_external_models.sh` - Setup de Modelos Externos
**Função:** Configura ambiente/modelos externos

**Uso:**
```bash
./scripts/script_setup_external_models.sh
```

---

## 📊 Comparação de Scripts

| Script | Ambiente | GPU | Verificações | Cria Dir | Flexibilidade |
|--------|----------|-----|--------------|----------|---------------|
| `script_start.sh` | Local | ❌ | ✅ | ✅ | ❌ |
| `script_start_server.sh` | SSD Externo | ✅ | ✅ | ✅ | ❌ |
| `script_run_with_env.sh` | SSD Externo | ✅ | ❌ | ❌ | ✅ |
| `script_install.sh` | Local | ❌ | ❌ | ❌ | ❌ |
| `script_migrate_to_ssd.sh` | SSD Externo | ✅ | ❌ | ❌ | ❌ |
| `script_setup_external_models.sh` | SSD Externo | ✅ | ❌ | ❌ | ❌ |

## 🎯 Recomendações de Uso

### Para Desenvolvimento:
```bash
./scripts/script_start.sh
```

### Para Produção com GPU:
```bash
./scripts/script_start_server.sh
```

### Para Executar Scripts Específicos:
```bash
./scripts/script_run_with_env.sh "comando"
```

### Para Testes:
```bash
./scripts/script_run_with_env.sh run_tests.py
```

## ⚠️ Notas Importantes

1. **Ambiente Local vs SSD Externo:**
   - Scripts com "server" no nome usam SSD externo
   - Scripts sem "server" usam ambiente local

2. **Verificações de Segurança:**
   - `script_start.sh` e `script_start_server.sh` verificam processos em execução
   - `script_start.sh` e `script_start_server.sh` criam diretórios automaticamente

3. **GPU:**
   - `script_start_server.sh` e `script_run_with_env.sh` configurados para GPU
   - `script_start.sh` usa configuração padrão

4. **Flexibilidade:**
   - `script_run_with_env.sh` é o mais flexível
   - `script_start.sh` e `script_start_server.sh` são específicos para servidor

## 🔄 Fluxo de Trabalho Recomendado

1. **Primeira vez:** `./scripts/script_install.sh`
2. **Desenvolvimento:** `./scripts/script_start.sh`
3. **Produção:** `./scripts/script_start_server.sh`
4. **Scripts específicos:** `./scripts/script_run_with_env.sh "comando"`
5. **Testes:** `./scripts/script_run_with_env.sh run_tests.py`

## 📁 Estrutura de Pastas

```
coqui-tts/
├── scripts/                    # 📁 Scripts organizados
│   ├── script_start.sh        # 🚀 Inicialização principal
│   ├── script_start_server.sh # 🖥️ Servidor com GPU
│   ├── script_run_with_env.sh # 🔧 Executor de comandos
│   ├── script_install.sh      # 📦 Instalação
│   ├── script_migrate_to_ssd.sh # 💾 Migração para SSD
│   └── script_setup_external_models.sh # ⚙️ Setup externo
├── src/                       # 📁 Código fonte
├── tests/                     # 📁 Testes
├── config/                    # 📁 Configurações
├── output/                    # 📁 Saídas de áudio
└── logs/                      # 📁 Logs
``` 