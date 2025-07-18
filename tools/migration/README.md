# Migration Tools

This directory contains tools for migrating Coqui TTS Server data, models, and configurations.

## 📁 Available Migration Tools

### `migrate_models_to_ssd.py`
**Purpose**: Migrate LLM models to external SSD to free up space and enable GPU acceleration

**What it does**:
- Moves TTS models from `~/.local/share/tts` to external SSD
- Moves Whisper models from `~/.cache/huggingface/hub` to external SSD
- Creates symlinks to maintain compatibility
- Updates server configuration to enable GPU mode
- Creates environment setup script

**Usage**:
```bash
cd tools/migration
python migrate_models_to_ssd.py
```

**Benefits**:
- ✅ Frees up ~1.6GB on main disk
- ✅ Enables GPU acceleration for Whisper
- ✅ Maintains backward compatibility
- ✅ Automatic configuration updates

## 🎯 Why Create a Migration Folder?

### **1. Organization**
- Keeps migration tools separate from main application code
- Makes it easy to find and manage migration scripts
- Follows the existing tools structure pattern

### **2. Reusability**
- Migration tools can be used multiple times
- Easy to create new migration scripts for different scenarios
- Can be imported and used programmatically

### **3. Safety**
- Migration operations are isolated
- Easy to backup and restore if needed
- Clear separation of concerns

### **4. Documentation**
- Each migration tool can have its own documentation
- Clear purpose and usage instructions
- Version control for migration scripts

## 📋 Migration Scenarios

### **Current Migration**
- **From**: Internal disk (limited space, CPU-only)
- **To**: External SSD (44GB free, GPU-enabled)
- **Models**: TTS (877MB) + Whisper (681MB) = ~1.6GB

### **Future Migration Possibilities**
- Cloud storage migration
- Model format conversion
- Configuration migration
- Database migration
- Backup/restore operations

## 🔧 Migration Process

1. **Pre-migration Checks**
   - Verify external SSD availability
   - Check available space
   - Backup current configuration

2. **Model Migration**
   - Copy models to external SSD
   - Create symlinks for compatibility
   - Update configuration files

3. **Post-migration Setup**
   - Create environment scripts
   - Update server configuration
   - Test functionality

4. **Verification**
   - Run tests to ensure everything works
   - Check GPU acceleration
   - Verify model accessibility

## 🚨 Safety Considerations

- **Backup**: Original models are backed up before migration
- **Rollback**: Symlinks can be easily reverted
- **Testing**: Comprehensive tests after migration
- **Documentation**: Clear instructions for each step

## 📊 Expected Results

After migration to external SSD:
- **Disk Space**: +1.6GB freed on main disk
- **Performance**: GPU acceleration enabled
- **Compatibility**: All existing functionality preserved
- **Scalability**: Room for more models on external SSD 