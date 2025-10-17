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

### 90-99: Production Operations

#### `90-logging-monitoring.mdc` ⭐ HIGH
**Priority:** HIGH  
**Impact:** Production debugging & monitoring

**Key Rules:**
- Structured JSON logging with request_id
- Log levels: INFO (normal), WARNING (issues), ERROR (failures)
- Log AI metrics: model, tokens, latency
- Never log API keys or PII
- Monitor job execution and performance

**When AI will use:**
- Adding logging statements
- Debugging production issues
- Tracking AI performance

---

#### `91-error-handling.mdc` ⭐ HIGH
**Priority:** HIGH  
**Impact:** Production stability

**Key Rules:**
- Handle OpenAI errors with retry logic (3 attempts, exponential backoff)
- User-friendly messages vs internal logging
- Graceful degradation (fallback to cached/simple logic)
- Never expose internal errors to users
- Telegram bot error handling

**When AI will use:**
- Adding error handling
- Fixing production bugs
- Implementing API integrations

---

#### `92-background-jobs.mdc`
**Priority:** MEDIUM  
**Impact:** Data freshness & ML accuracy

**Key Rules:**
- Background jobs in `tools/` directory
- Log start/end times, records processed
- Handle failures gracefully (don't block other jobs)
- Resource management: memory/disk checks
- Batch processing for large datasets (25k+ records)

**When AI will use:**
- Creating new background tasks
- Optimizing cron jobs
- Debugging failed jobs

---

#### `93-performance.mdc`
**Priority:** MEDIUM  
**Impact:** Cost & speed

**Key Rules:**
- Use local ML predictor (60-70% token savings)
- Database indexes on published_at, importance, credibility
- Batch processing: chunks of 100-1000
- Cache AI responses with `ai_modules/cache.py`
- Quality gates: skip AI if importance/credibility < 0.6/0.7

**When AI will use:**
- Performance optimization
- Reducing API costs
- Fixing slow queries

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
| "Add logging" | 90-logging | Use structured JSON format |
| "Fix production bug" | 91-error-handling | Add retry logic, graceful degradation |
| "Create background job" | 92-background-jobs | Use template, add monitoring |
| "Optimize performance" | 93-performance | Check ML predictor, caching, indexes |

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

**Production:**
- Logging: `90-logging-monitoring.mdc`
- Error handling: `91-error-handling.mdc`
- Background jobs: `92-background-jobs.mdc`
- Performance: `93-performance.mdc`

---

## ✅ Verification Checklist

After restart, AI should:

- [ ] Suggest `env-save` before .env changes
- [ ] Check `prompts_v2.py` for AI prompt changes
- [ ] Create migrations with rollback for DB changes
- [ ] Pin versions when adding dependencies
- [ ] Use Conventional Commits format
- [ ] Run tests before marking complete
- [ ] Use structured JSON logging
- [ ] Add retry logic for API errors
- [ ] Log background job metrics
- [ ] Check for performance optimizations (ML predictor, caching)

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

- **Total rules:** 12 files
- **Total lines:** ~2,200
- **Critical rules:** 5 (env, prompts, migrations, logging, errors)
- **Coverage areas:** 10 (security, AI, DB, deps, git, testing, logging, errors, background, performance)

---

**Last Updated:** 2025-10-17  
**Version:** 1.1  
**Status:** Active


