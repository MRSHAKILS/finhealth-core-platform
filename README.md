# FinHealth AI core platform (demo)

Synthetic code for testing the [LexCompiler](https://github.com/shahriar-ahmed-seam/LexCompiler) GitHub App. It contains no real data.

The code breaks four illustrative rules on purpose, so `main` starts with known findings:

| Rule | Where |
| :--- | :--- |
| R-1 Retention within 72 hours and tenant-isolated keys | `schema/postgres_pii.sql`, `api/fastapi_intake.py`, `workers/redis_cache_worker.py` |
| R-2 No unredacted personal data in logs | `api/fastapi_intake.py` |
| R-3 Human review below 85% AI confidence | `services/ai_credit_triage.ts` |
| R-4 No replication outside the EU | `services/cross_border_sync.ts` |

LexCompiler checks every pull request and fails it only for findings the pull request adds.
