# Communication & Development Process

Guidelines for effective communication and development workflow in the PulseAI project.

## Table of Contents

- [Git Workflow](#git-workflow)
- [Task Management](#task-management)
- [Documentation Standards](#documentation-standards)
- [Daily Summaries](#daily-summaries)
- [Code Review Process](#code-review-process)
- [Communication Channels](#communication-channels)

## Git Workflow

### Commit Standards
- **Commit after each logical step** — Don't accumulate changes
- **Meaningful commit messages** — Use format: `type: description`
- **Small, focused commits** — One logical change per commit
- **Always push after commits** — Keep remote repository updated

### Branch Strategy
- **Main branch:** `main` — Production-ready code
- **Feature branches:** `feature/description` — New features
- **Bug fixes:** `fix/description` — Bug fixes
- **Documentation:** `docs/description` — Documentation updates

### Pre-commit Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated if needed
- [ ] Commit message is descriptive

## Task Management

### Task Lifecycle
1. **Task Creation** — Add to TASKS.md with priority
2. **Task Planning** — Create checklist and acceptance criteria
3. **Task Execution** — Work through checklist items
4. **Task Review** — Verify acceptance criteria met
5. **Task Completion** — Update status and document results

### Priority System
- 🔴 **Urgent** — Blocks work or critical bugs
- 🟡 **Important** — Should be done in coming days
- 🟢 **Can be postponed** — Nice to have features

### Task Documentation
- **Context** — Why the task is needed
- **Subtasks** — Breakdown of work items
- **Acceptance Criteria** — Definition of done
- **Related Decisions** — Link to MASTER_FILE.md decisions

## Documentation Standards

### Core Documents
- **MASTER_FILE.md** — Project rules, architecture, decisions
- **TASKS.md** — Current tasks and backlog
- **README.md** — Project overview and quick start
- **docs/** — Detailed technical documentation

### Documentation Principles
- **English for technical docs** — Code, architecture, APIs
- **Russian for product descriptions** — When appropriate
- **Consistent formatting** — Use standard Markdown practices
- **Table of Contents** — For files with 3+ headings
- **Regular updates** — Keep documentation current

### Document Maintenance
- **Review before changes** — Check MASTER_FILE.md and TASKS.md
- **Update after changes** — Reflect new decisions and progress
- **Version control** — Track documentation changes in git

## Daily Summaries

### Evening Summary Format
- ✅ **Completed** — What was accomplished today
- 🔜 **In Progress** — What's currently being worked on
- 🚧 **Blockers** — What's preventing progress

### Example Summary
```
✅ Completed:
- Fixed Telegram bot timeout errors
- Updated test suite for new architecture
- Added Makefile for development commands

🔜 In Progress:
- Documentation cleanup and standardization
- Test coverage expansion

🚧 Blockers:
- None currently
```

## Code Review Process

### Review Checklist
- [ ] Code follows project conventions
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes without notice
- [ ] Performance implications considered

### Review Standards
- **Constructive feedback** — Focus on improvement
- **Clear explanations** — Why changes are needed
- **Respectful communication** — Professional tone
- **Timely responses** — Don't delay reviews

## Communication Channels

### Primary Communication
- **GitHub Issues** — Bug reports and feature requests
- **GitHub Discussions** — General project discussion
- **Commit Messages** — Technical change communication
- **Documentation** — Project knowledge base

### Communication Guidelines
- **Be specific** — Provide clear, actionable information
- **Be concise** — Respect others' time
- **Be respectful** — Maintain professional tone
- **Be responsive** — Acknowledge and respond to messages

### Escalation Process
1. **Document the issue** — Create detailed issue/PR
2. **Tag relevant people** — Use @mentions appropriately
3. **Provide context** — Include relevant background
4. **Follow up** — Ensure issues are resolved

## Project Memory

### Key References
- **Project Core** — PulseAI vision and goals
- **Full Description** — Complete project documentation
- **Roadmap/Tasks** — Current priorities and timeline

### Decision Tracking
- **Architecture decisions** — Documented in MASTER_FILE.md
- **Process changes** — Updated in this document
- **Technical choices** — Explained with rationale

### Knowledge Sharing
- **Regular updates** — Keep team informed of progress
- **Documentation reviews** — Ensure accuracy and completeness
- **Lessons learned** — Share insights and improvements