# Movie Factory implementation instructions

- Use this project's `.venv` for all outer Python commands and dependencies. Never install packages globally.
- Treat `.env` as private. Never print, log, commit, or pass its values to Blender. Only the trusted provider module may read known settings.
- Follow `MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md`. Preserve failed evidence and report `NOT_RUN` or YELLOW when a prerequisite or Director review is missing.
- Blender workers execute only validated structured operations. Do not add arbitrary model-generated Python execution on the developer account.
- Do not run live provider calls outside the persistent campaign budget ledger. Mocks are the default for tests.
- Houdini and Unreal remain later-phase design notes until the Blender qualification is complete.
- Record announced engineering-model switches, handoffs, and their outcomes in `docs/engineering-intelligence/events.json`, following its README. Keep Codex engineering attribution separate from experiment API models, mark unknown effort/usage as unknown, and include Director-rejected outcomes after escalation. Consult this record when proposing Factory model routing; do not treat it as a controlled model benchmark.
