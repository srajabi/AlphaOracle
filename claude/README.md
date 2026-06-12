# claude/ - Agent Context Hub

Everything an AI coding agent (or a human resuming after a break) needs to
rebuild full context, in reading order:

1. **[agents.md](agents.md)** - HOW we work: workflow, the 8-step research
   loop, git conventions, testing rules, what never to touch.
2. **[context.md](context.md)** - WHAT this project is: architecture,
   pipeline, components.
3. **[current.md](current.md)** - session-by-session narrative log of what
   changed (newest first).
4. **[findings.md](findings.md)** - WHAT WE KNOW: the canonical registry of
   every empirical result, with numbers, caveats, and result pointers.
   **Update this in every session that produces a result.**

Related, outside this folder:

- `../spikes/` - deep research docs and design explorations (one per topic)
- `../papers/` - the papers library: per-paper notes with OUR backtest
  verdicts; `papers/private/` (gitignored) for personally-licensed material
- `../CLAUDE.md` (repo root) - auto-loaded by Claude Code each session;
  points here.

## Documentation discipline

| Doc | Update when |
|---|---|
| findings.md | any empirical result, immediately |
| current.md | end of every work session |
| agents.md | workflow/process changes |
| context.md | architecture changes |
| spikes/<topic>.md | new research thread or design decision |
| papers/<note>.md | paper sourced or verdict reached |
