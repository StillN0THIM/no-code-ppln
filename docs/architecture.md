# Architecture & Phase Details

## Phase 0 — Foundations & Pipeline Schema
Define the pipeline config contract (JSON/YAML: nodes, params, edges, quality-gate
thresholds) as Pydantic models in `pipeline_schema/`. Set up the base Docker image,
repo skeleton, and pick one public tabular classification dataset to build against.

## Phase 1 — Core Pipeline (Manual Trigger)
Fixed-node canvas (Dataset, Validation, Training, Evaluation, Registry) built with
React Flow, each node with a config form. The canvas emits a Phase 0 config object.
`backend/app/services/` runs the stages in order: ingest → validate → train →
evaluate → register in MLflow (`Staging`) if the metric clears the Evaluation
node's threshold. Triggered manually via a "Run" button.

## Phase 2 — CI/CD for ML
A pipeline-config change pushed to Git triggers `.github/workflows/ci.yml`:
validate → train → evaluate inside the same base Docker image used locally. On
pass, `cd.yml` promotes the MLflow model to `Production` and redeploys the
`serving/` container (rebuild → push to registry → restart).

## Phase 3 — Monitoring, Drift Detection & Continuous Training
The serving endpoint logs predictions. A scheduled job in `monitoring/jobs/` runs
Evidently against recent predictions vs. the training reference data, simulating
traffic with held-out shifted data slices. Crossing a drift/performance threshold
re-triggers the Phase 2 workflow via `workflow_dispatch` — closing the loop.

## Phase 4 — Polish & Resume-Ready Extras
Multi-pipeline support, run-history view, live canvas node status
(running/passed/failed), optional JWT auth, Tailwind polish, demo video.
