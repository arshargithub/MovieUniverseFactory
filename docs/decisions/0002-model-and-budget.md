# Decision 0002 — API model and budget

Use `gpt-5.4-2026-03-05` for planning and visual review because the frozen official model record supports structured outputs, image input, and reasoning controls. Prices retrieved 2026-09-08 are recorded in `config/prices.json`.

All live calls share one persistent campaign ledger. The campaign ceiling is USD 40; each scored initial stage is capped at USD 3 and each scored revision at USD 2, with the aggregate allocations described in the feasibility specification. Missing or uncertain usage is not zero and retains its reservation.
