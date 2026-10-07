# No-Code MLOps Platform

A visual, drag-and-drop pipeline builder for ML workflows:

```
Dataset → Validation → Training → Evaluation → Registry → Deployment → Monitoring → Retraining
```

Built as an **orchestration + UI layer over existing MLOps tools** (MLflow, DVC,
Evidently, GitHub Actions) rather than reinventing them. The goal is a platform
where a user builds a pipeline visually, and that pipeline runs, tracks, gates,
deploys, and monitors itself using production-grade tools underneath.

The project is scoped into four phases so each one is independently demoable —
it's never "not done enough" to show.

---

## Project Phases

| Phase | Goal | Status |
|-------|------|--------|
| **0 — Foundations** | Pipeline config schema, repo skeleton, base Docker image, dataset selection | ⬜ |
| **1 — Core Pipeline** | Visual canvas (React Flow) → config → manual pipeline run (ingest, validate, train, evaluate, register) | ⬜ |
| **2 — CI/CD for ML** | GitHub Actions pipeline: auto validate/train/evaluate on push, auto-promote + redeploy on pass | ⬜ |
| **3 — Monitoring & Retraining** | Drift detection (Evidently), scheduled reports, automatic retrain trigger | ⬜ |
| **4 — Polish** | Multi-pipeline support, run history, live node status, demo video | ⬜ |

See [`docs/architecture.md`](docs/architecture.md) for the detailed design per phase.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Canvas UI | React + React Flow |
| Backend / orchestration | FastAPI |
| Config schema | Pydantic |
| Data versioning | DVC |
| Data validation | Great Expectations / Pydantic checks |
| Training | scikit-learn / PyTorch |
| Experiment tracking + registry | MLflow |
| Run metadata storage | PostgreSQL |
| CI/CD | GitHub Actions |
| Image registry | GitHub Container Registry |
| Model serving | FastAPI (separate service) |
| Drift / monitoring | Evidently AI |
| Dashboard | Prometheus + Grafana (or lightweight FastAPI+HTML) |
| Containerization | Docker / docker-compose |

---

## Repository Structure

```
no-code-mlops-platform/
├── pipeline_schema/        # Phase 0: Pydantic models for the pipeline config (nodes, params, edges, gates)
├── datasets/                # Chosen dataset + notes
├── notebooks/                # Baseline exploration notebook
├── docker/
│   └── base.Dockerfile       # Reproducible execution image used locally + in CI
├── backend/                  # FastAPI orchestration service (Phase 1+)
│   ├── app/
│   │   ├── api/               # Route handlers
│   │   ├── core/              # Config, settings, shared utilities
│   │   ├── models/             # DB/domain models
│   │   └── services/          # One class per pipeline stage
│   │       ├── ingestion.py
│   │       ├── validation.py
│   │       ├── training.py
│   │       ├── evaluation.py
│   │       └── registry.py
│   └── tests/
├── frontend/                  # React + React Flow canvas (Phase 1+)
│   └── src/
│       ├── components/nodes/   # Dataset/Validation/Training/Evaluation/Registry node components
│       ├── pages/
│       └── services/            # API client layer
├── serving/                     # Standalone model-serving FastAPI service (Phase 2+)
├── monitoring/                   # Drift jobs + generated reports (Phase 3)
├── .github/workflows/              # ci.yml, cd.yml
├── docs/
│   └── architecture.md
├── docker-compose.yml
└── LICENSE
```

---

## Getting Started

**Prerequisites:** Python 3.11+, Node 18+, Docker & Docker Compose, Git.

```bash
git clone <your-repo-url>
cd no-code-mlops-platform

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Infra (Postgres + MLflow)
cd ..
docker-compose up -d postgres mlflow
```

Run the backend locally:

```bash
cd backend
uvicorn app.main:app --reload
```

Run the frontend locally:

```bash
cd frontend
npm run dev
```

---

## Explicitly Out of Scope (v1)

Kubernetes orchestration, distributed/multi-GPU training, feature stores, and
cloud infrastructure (AWS/GCP) are deliberately deferred as future extensions —
noted here to signal awareness without taking them on in v1.

---

## License

MIT — see [LICENSE](LICENSE).
