#155 audit-plan admission defect

No worker launched: Bridge correctly rejected render-only steps whose parent was
an external prior-cycle derivative rather than a reviewed native artifact in the
same admitted plan (RENDER_REQUIRES_REVIEWED_NATIVE). Setup's recipe/type/unit
checks had not tested this graph condition.156 adds a no-edit admitted save/reopen
control before the two audit renders. No bypass, counter refund or new database.
This consumes the final approved correction. It is avoidable planning overhead,
not an artistic improvement. Future preflight must check native dependency graph
conditions before admitting a correction, not only recipe fields/time limits.
