# AI Assistant Configuration for PulseAI

This directory contains AI-specific rules and configurations for working with PulseAI project.

## 📁 Files

### `.cursor/rules`
Complete AI assistant rules including:
- **CRITICAL:** .env file management with Git Stash
- Security guidelines
- Project architecture
- Development workflow
- Best practices

### `../.cursorrules`
Short version of rules loaded by Cursor automatically.

## 🔐 Key Rule: .env Management

**ALWAYS use Git Stash for .env backups:**

```bash
# Before changes
env-save "description"

# To rollback
env-restore
```

**NEVER:**
- Create backup files: `cp .env .env.backup` ❌
- Commit .env files ❌
- Bypass security hooks ❌

## 📖 Why These Rules Exist

**Security Incident on 2025-10-16:**
- `.env.backup` was accidentally committed to Git
- OpenAI API key leaked to public repository
- Git history had to be force-rewritten

**Prevention:**
- Git Stash is now the ONLY approved backup method
- Pre-commit hooks block all .env files
- AI assistant reminds about backups

## 🎯 Quick Start for AI

When user wants to modify .env:

1. Suggest: `env-save "description"`
2. Provide edit command
3. Remind: `env-restore` if issues

See full examples in `.cursor/rules`

## 📚 Documentation References

- `ENV_BACKUP_CHEATSHEET.md` - Quick reference
- `.env-stash-guide.md` - Complete guide
- `SECURITY_INCIDENT_REPORT.md` - Incident details
- `BACKUP_GUIDE.md` - All backup methods

---

**Version:** 1.0  
**Created:** 2025-10-16  
**Purpose:** Prevent security incidents, enforce best practices


