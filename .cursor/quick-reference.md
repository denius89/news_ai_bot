# AI Assistant Quick Reference

## 🔥 Most Important Rule

### Before ANY .env changes:

```bash
env-save "what you're changing"
```

## ⚡ Quick Commands

```bash
env-save "description"   # Save before changes
env-restore              # Rollback
env-list                 # Show backups
env-edit                 # Edit with auto-backup
```

## 🚫 Never Do

- `cp .env .env.backup` ❌
- Commit .env files ❌
- Create backup files ❌

## ✅ Always Do

- Use Git Stash via env-save ✅
- Remind user about backup ✅
- Mention rollback option ✅

## 📖 Full Rules

See: `.cursor/rules`
