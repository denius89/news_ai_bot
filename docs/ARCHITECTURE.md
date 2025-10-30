# 🧱 Architecture Overview

_Generated on 2025-10-30 18:06:32 UTC_

## Layers

- ai_modules
- digests
- parsers
- database
- routes
- webapp
- tools

## Dependency Graph (by imports)

- ai_modules → database, other
- digests → ai_modules, database, other
- parsers → ai_modules, database, other, tools
- database → ai_modules, other
- routes → ai_modules, database, digests, other, parsers, tools
- webapp → other
- tools → ai_modules, database, digests, other, parsers
- other → ai_modules, database, digests, parsers, routes, tools

> Rule: no cross-layer violations beyond documented flows.
