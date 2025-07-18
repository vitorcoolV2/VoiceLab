# Scripts Coqui TTS – Padrão DRY, SSD Externo e Sistema de Estado

## Visão Geral

Todos os scripts desta pasta seguem o padrão DRY (Don't Repeat Yourself), estão otimizados para uso com ambiente, modelos e outputs centralizados em um SSD externo, e incluem um sistema de estado para continuar de onde pararam em caso de interrupção.

---

## Sistema de Estado

Todos os scripts implementam um sistema de estado que:
- **Marca o progresso** em ficheiros temporários (`/tmp/coqui_tts_*.state`)
- **Continua de onde parou** se o script for interrompido
- **Mostra o estado atual** durante a execução
- **Permite reiniciar** apagando o ficheiro de estado

### Estados Comuns:
- `INICIADO` - Script iniciado
- `CONDA_ATIVADO` - Ambiente conda ativado
- `VARIAVEIS_VERIFICADAS` - Variáveis do .env verificadas
- `DEPENDENCIAS_INSTALADAS` - Dependências instaladas
- `COMPLETO` - Script terminado com sucesso

---

## Scripts Disponíveis

### `start.sh` - Iniciar Servidor TTS
```bash
./start.sh
```
**Estados:** INICIADO → CONDA_ATIVADO → SERVIDOR_PARADO → PORTA_LIVRE → DIRETORIOS_CRIADOS → SERVIDOR_INICIADO

### `install.sh` - Instalar Dependências
```bash
./install.sh
```
**Estados:** INICIADO → VARIAVEIS_VERIFICADAS → MINICONDA_VERIFICADO → PYTHON_VERIFICADO → ESPACO_VERIFICADO → CONDA_ATIVADO → AMBIENTE_REMOVIDO → AMBIENTE_CRIADO → AMBIENTE_ATIVADO → CACHE_CONFIGURADO → DEPENDENCIAS_INSTALADAS → DIRETORIOS_CRIADOS → INSTALACAO_COMPLETA

### `migrate.sh` - Migrar Modelos para SSD
```bash
./migrate.sh
```
**Estados:** INICIADO → CONDA_ATIVADO → DIRETORIO_VERIFICADO → MIGRACAO_COMPLETA

### `run.sh` - Executar Comandos Python
```bash
./run.sh script.py arg1 arg2
```
**Estados:** INICIADO → CONDA_ATIVADO → COMANDO_EXECUTADO

### `setup_external_ssd.sh` - Preparar SSD Externo
```bash
./setup_external_ssd.sh
```
**Estados:** INICIADO → CONDA_ATIVADO → DIRETORIOS_CRIADOS → PERMISSOES_AJUSTADAS → LINK_CRIADO → SETUP_COMPLETO

---

## Padrão de todos os scripts

- **Carregamento automático do `.env`:**
  - Todos os scripts carregam o arquivo `.env` na raiz do projeto, que define os caminhos para modelos, outputs, downloads e cache.
  - Exemplo de `.env`:
    ```env
    MINICONDA_SSD=/media/vitor/ssd990/home-backup/miniconda3
    ENV_NAME=coqui-tts
    COQUI_TTS_HOME=/media/vitor/ssd990/home-backup/coqui-models
    HF_HOME=/media/vitor/ssd990/home-backup/whisper-models
    TRANSFORMERS_CACHE=/media/vitor/ssd990/home-backup/whisper-models
    COQUI_TTS_OUTPUTS=/media/vitor/ssd990/home-backup/coqui-outputs
    COQUI_TTS_DOWNLOADS=/media/vitor/ssd990/home-backup/coqui-downloads
    PIP_CACHE_DIR=/media/vitor/ssd990/home-backup/pip_cache
    TMPDIR=/media/vitor/ssd990/home-backup/tmp
    ```

- **Sistema de Estado:**
  - Cada script marca seu progresso em `/tmp/coqui_tts_[script].state`
  - Se interrompido, continua de onde parou na próxima execução
  - Para reiniciar do zero: `rm -f /tmp/coqui_tts_[script].state`

- **Ativação do ambiente Conda:**
  - Antes de qualquer comando Python, o ambiente `coqui-tts` é ativado a partir do SSD externo.
  - Isso garante dependências corretas e performance otimizada.

- **Eliminação de hardcodes:**
  - Nenhum caminho é hardcoded nos scripts. Tudo é lido do `.env`.

---

## Como usar

1. **Mantenha o arquivo `.env` atualizado** na raiz do projeto (`coqui-tts/.env`).
2. **Execute qualquer script desta pasta normalmente**:
   ```bash
   ./start.sh
   ./install.sh
   ./migrate.sh
   ./run.sh script.py
   ./setup_external_ssd.sh
   ```
3. **O ambiente estará sempre correto**: variáveis carregadas, conda ativado, paths centralizados no SSD.
4. **Se um script for interrompido**: execute novamente e ele continuará de onde parou.

---

## Gestão de Estado

### Verificar estado atual:
```bash
cat /tmp/coqui_tts_install.state
cat /tmp/coqui_tts_start.state
cat /tmp/coqui_tts_migrate.state
```

### Reiniciar script do zero:
```bash
rm -f /tmp/coqui_tts_install.state
./install.sh
```

### Limpar todos os estados:
```bash
rm -f /tmp/coqui_tts_*.state
```

---

## Manutenção

- Se mudar algum caminho, **atualize apenas o `.env`**.
- Se adicionar dependências, atualize o `requirements.txt` e rode o `install.sh`.
- Para backup, basta copiar a pasta `home-backup` do SSD.
- Os ficheiros de estado são temporários e podem ser apagados sem problemas.

---

**Dúvidas ou manutenção?**
Fale com o seu assistente AI builder! 😉 