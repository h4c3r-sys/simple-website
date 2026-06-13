# The Sacred Citadel: Architectural & Design Theory 🏛️

This document outlines the computer science principles, architectural decisions, and design theories underpinning *The Sacred Citadel*.

## 1. System Architecture: Next.js App Router & Serverless Paradigm
The application is built on the **Next.js 16 App Router**. Unlike older monolithic Node.js servers (e.g., Express), Next.js utilizes a serverless-first paradigm.

### Why Serverless?
- **Statelessness:** Each API route (like `/api/generate-thread`) executes independently. This ensures extreme horizontal scalability. If the app goes viral, Vercel or your Docker swarm can spin up 100 parallel instances of the `/api/generate-thread` endpoint without any memory-sharing conflicts.
- **React Server Components (RSC):** The UI (like `/app/page.tsx`) uses RSCs to fetch Prisma database records *directly on the server* before shipping HTML to the client. This results in zero client-side JavaScript bundle bloat for fetching data, leading to blazing fast Time-to-Interactive (TTI).

## 2. Database Paradigm: Prisma + SQLite
While Postgres is the modern standard, **SQLite** was intentionally chosen for this project for absolute maximum portability.

### Why SQLite over Postgres?
- **Zero-Configuration Deployment:** In containerized environments, setting up a dual-container (App + DB) network introduces points of failure and credential management overhead. SQLite embeds the database engine directly into the application process.
- **The `dev.db` File:** The entire state of the forum exists as a single binary file (`prisma/dev.db`). This makes backing up, migrating, or sharing the forum as trivial as copying a file.
- **Connection Pooling:** Because SQLite runs in the same process space as the Node application, it does not suffer from TCP connection overhead or pool exhaustion that serverless Postgres adapters often face.

## 3. The Cross-Platform Execution Bug (`tsx` vs `ts-node`)
During development, a critical bug was encountered on Windows PowerShell when seeding the database:
\`\`\`bash
SyntaxError: Expected property name or '}' in JSON at position 1
\`\`\`
### Root Cause (OS-Level Shell Escaping):
The original Prisma seed command used `ts-node --compilerOptions '{"module":"CommonJS"}' prisma/seed.ts`.
Linux (bash) properly interprets single quotes enclosing double quotes. However, Windows PowerShell strips single quotes, causing the JSON compiler options to be parsed incorrectly by the Node binary.

### The Solution: Native `tsx`
We migrated from `ts-node` to `tsx`. `tsx` natively hooks into Node's ESM loader and transpiles TypeScript on-the-fly without requiring inline JSON compiler injections. By pointing Prisma directly to `tsx` in `package.json`, we decoupled the execution logic from the OS shell, ensuring 100% cross-platform deterministic behavior.

## 4. The AI Mimicry Engine: Prompt Engineering Theory
The core feature of this application is its ability to perfectly mimic a 2012-era forum. This is not achieved by simple string replacement, but through **System-Level Few-Shot Prompting**.

### The Orchestration Flow:
1. **The Request:** The user submits a generic topic string (e.g., "WebSockets").
2. **The Prompt Construction:** The server wraps this topic in a highly restrictive structural prompt.
   - We enforce **JSON-only output** using system directives.
   - We instruct the model (Claude 3.5 Sonnet) to assume a highly specific persona ("2012 forum members").
   - We define the expected emotional variance (agreements, disagreements, "did you even search?").
3. **The Multi-Key Load Balancer:** To bypass restrictive rate limits on free-tier APIs, the application parses the `ANTHROPIC_API_KEY` string as an array of keys and uses `Math.random()` to implement an application-layer round-robin load balancer.
4. **Data Hydration:** The raw JSON returned by the AI is parsed and injected directly into the Prisma Object-Relational Mapper (ORM), dynamically creating `User`, `Thread`, and `Post` entities in a single transactional flow.

## 5. UI Paradigm: Theming via CSS Variables
Instead of shipping multiple giant CSS stylesheets for different forum themes (vBulletin, StackOverflow, Terminal), the app uses a singular `globals.css` powered by **CSS Custom Properties (Variables)**.

### How it works:
When an Admin changes the theme in the control panel, it updates a global state record in SQLite. The root layout reads this record and injects a `data-theme="retro-so"` attribute onto the `<html>` tag.

```css
:root { --primary: #0055ff; }
[data-theme="retro-so"] { --primary: #f48024; }
```
Because the `<html>` tag defines the scope, the browser's CSS engine instantly recalculates all descendant nodes using `--primary` without requiring a page reload or JavaScript re-render. This is an O(1) complexity operation for theme swapping.