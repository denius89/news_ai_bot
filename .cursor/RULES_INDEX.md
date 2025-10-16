# 📚 AI Assistant Rules Index

**Total:** 8 rule files | ~1,200 lines of guidelines

---

## 📁 Rules Structure

### Priority Levels:
- **00-19:** Foundation (purpose, collaboration)
- **20-29:** Code standards
- **30-49:** Security & Critical Operations
- **50-69:** Data & Dependencies
- **70-89:** Development Workflow
- **90-99:** Reserved for project-specific rules

---

## 📋 Current Rules

### 00-29: Foundation & Standards

#### `00-purpose-and-collaboration.mdc`
- Project purpose and mission
- Collaboration guidelines
- Communication standards

#### `10-architecture.mdc`
- PulseAI architecture layers
- No cross-layer imports
- Module responsibilities

#### `20-coding-standards.mdc`
- Python: PEP8, typing, Google docstrings
- React: Function components, hooks, Tailwind
- Import order: stdlib → 3rd party → local

---

### 30-49: Security & Critical Operations

#### `30-env-backup-security.mdc` ⭐ CRITICAL
**Priority:** CRITICAL  
**Impact:** Data leaks prevention

**Key Rules:**
- ALWAYS use `env-save` before .env changes
- NEVER create `.env.backup` files manually
- Use Git Stash exclusively
- Pre-commit hooks protect against leaks

**Context:** Security incident on 2025-10-16
- `.env.backup` leaked to GitHub
- OpenAI API key exposed
- Git history rewritten

**When AI will use:**
- Any .env file modification
- Environment configuration changes
- Secret management

---

#### `40-ai-prompts-management.mdc` ⭐ HIGH
**Priority:** HIGH  
**Impact:** News quality & AI performance

**Key Rules:**
- Source of truth: `digests/prompts_v2.py`
- ALWAYS test prompts before changes
- Use structured format with JSON Schema
- Include self-check instructions
- Monitor: importance ≥ 0.6, credibility ≥ 0.7

**When AI will use:**
- Modifying AI prompts
- Adding new scoring logic
- Changing news filtering
- Updating DigestAIService

---

### 50-69: Data & Dependencies

#### `50-database-migrations.mdc` ⭐ HIGH
**Priority:** HIGH  
**Impact:** Can destroy production data

**Key Rules:**
- ALWAYS backup before migrations
- Test on development first
- Create rollback scripts
- Check for breaking changes
- Never drop tables without confirmation

**When AI will use:**
- Adding/modifying database tables
- Schema changes
- Index creation
- Data migrations

---

#### `60-dependencies-management.mdc`
**Priority:** MEDIUM  
**Impact:** Can break environment

**Key Rules:**
- Never touch `requirements.txt` without permission
- Always pin versions
- Check security before adding packages
- Test after upgrades
- One package at a time

**When AI will use:**
- Adding new Python/NPM packages
- Upgrading dependencies
- Resolving conflicts

---

### 70-89: Development Workflow

#### `70-git-commits.mdc`
**Priority:** LOW  
**Impact:** Code organization

**Key Rules:**
- Use Conventional Commits format
- Type(scope): description format
- Include body for complex changes
- Never commit secrets (hook will block)

**When AI will use:**
- Creating commits
- Suggesting commit messages

---

#### `80-testing.mdc`
**Priority:** MEDIUM  
**Impact:** Code quality

**Key Rules:**
- ALWAYS run tests before "Done"
- Add tests for new features
- Check linter before commit
- Aim for 80%+ coverage
- Never remove tests to pass build

**When AI will use:**
- After code changes
- Before marking task complete
- Adding new features

---

## 🎯 How AI Uses These Rules

### Automatic Triggers:

| User Action | Rules Applied | AI Behavior |
|------------|---------------|-------------|
| "Update .env" | 30-env-backup | Suggest `env-save` first |
| "Change AI prompt" | 40-prompts | Check prompts_v2.py, run tests |
| "Add database column" | 50-migrations | Create migration, test, rollback |
| "Install package" | 60-dependencies | Check security, pin version |
| "Commit changes" | 70-commits | Format as Conventional Commit |
| "Feature is done" | 80-testing | Run tests before confirming |

---

## 📖 Quick Access

### By Topic:

**Security:**
- .env backups: `30-env-backup-security.mdc`
- Pre-commit hooks: `.cursorrules`

**AI/ML:**
- Prompts: `40-ai-prompts-management.mdc`
- Quality gates: `40-ai-prompts-management.mdc`

**Database:**
- Migrations: `50-database-migrations.mdc`
- Models: `database/db_models.py`

**Development:**
- Testing: `80-testing.mdc`
- Commits: `70-git-commits.mdc`
- Dependencies: `60-dependencies-management.mdc`

---

## ✅ Verification Checklist

After restart, AI should:

- [ ] Suggest `env-save` before .env changes
- [ ] Check `prompts_v2.py` for AI prompt changes
- [ ] Create migrations with rollback for DB changes
- [ ] Pin versions when adding dependencies
- [ ] Use Conventional Commits format
- [ ] Run tests before marking complete

---

## 🔄 Updating Rules

### To add new rule:

1. Create file: `.cursor/rules/XX-name.mdc`
   - XX = priority (00-99)
   - Use `.mdc` extension

2. Format:
   ```markdown
   ---
   title: Rule Title
   tags: [tag1, tag2]
   priority: HIGH|MEDIUM|LOW
   ---
   
   # Rule Content
   ```

3. Update this index

4. Restart Cursor

---

## 📊 Statistics

- **Total rules:** 8 files
- **Total lines:** ~1,200
- **Critical rules:** 3 (env, prompts, migrations)
- **Coverage areas:** 6 (security, AI, DB, deps, git, testing)

---

**Last Updated:** 2025-10-16  
**Version:** 1.0  
**Status:** Active


