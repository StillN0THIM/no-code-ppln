# No-Code MLOps Platform

I'm building this to actually understand MLOps end to end — not just the
training/evaluation part most portfolio projects stop at, but the
orchestration, the CI/CD, the drift monitoring, all of it. The idea: a canvas
where you wire up Dataset → Validation → Training → Evaluation → Registry →
Deployment → Monitoring → Retraining, and the pipeline-config-as-code it emits
runs on top of MLflow, DVC, Evidently and GitHub Actions instead of
reinventing any of them.

It's scoped into four phases on purpose. I didn't want a project that's "90%
done" for six months straight — each phase is something that actually runs
and can be shown, even if the next one hasn't been started.

## Where it actually is right now

Phase 0 and Phase 1 are built and working locally — canvas, FastAPI backend,
the five pipeline services, MLflow registration, and a test suite
(`backend/tests/`) covering the happy path, a failed evaluation gate, and a
failed validation gate. Phase 2 is in progress: `ci.yml` runs the unit tests
on every push, `cd.yml` and the promotion script exist but haven't been run
against a real deploy target yet. Phases 3 and 4 haven't started.

## Stack

Canvas is React + React Flow. Backend is FastAPI, with Pydantic models
defining the pipeline config — that schema is the thing everything else is
built around (`pipeline_schema/models.py`). Training uses scikit-learn,
tracked and registered through MLflow, run metadata in Postgres. CI/CD is
GitHub Actions. Monitoring, once Phase 3 happens, will be Evidently against a
Postgres-backed prediction log.

## Running it

Python 3.11+, Node 18+, Docker.

```bash
docker-compose up -d postgres mlflow

cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd ..
uvicorn backend.app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

Drop the five nodes onto the canvas, wire them top to bottom, fill in the
fields, hit run. To check the backend works without touching the UI at all,
there's a sample dataset generator and a test payload —
`datasets/generate_sample.py` and `test_pipeline.json`.

## Layout

pipeline_schema/ pydantic models for the pipeline config
backend/app/services/ one class per pipeline stage
frontend/src/ the canvas
serving/ standalone model-serving app (Phase 2+)
monitoring/ drift jobs (Phase 3)
.github/workflows/ ci.yml, cd.yml



## What's deliberately not here

No Kubernetes, no distributed training, no feature store, no cloud infra. Not
because they're hard — because none of them teach you anything about MLOps
specifically, they're infrastructure problems, not pipeline problems. Might
revisit as future work once the core loop is solid.

