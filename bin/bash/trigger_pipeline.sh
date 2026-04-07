# Checks that all warehouse CSVs arrived for the current hour, then triggers Dataflow.

set -euo pipefail

PROJECT_ID="xyz-logistics"
BUCKET="gs://xyz-logistics-raw"
REGION="us-central1"
TEMPLATE_PATH="gs://dataflow-templates/latest/GCS_Text_to_BigQuery"
BQ_DATASET="xyz_logistics.raw_inventory"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:00:00Z")
DATE_PREFIX=$(date -u +"%Y/%m/%d/%H")
EXPECTED_WAREHOUSES=10
LOG_FILE="/var/log/xyz_pipeline.log"

log() {
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $1" | tee -a "$LOG_FILE"
}

# ── 1. Count files that arrived for the current hour ──────────────────────────
log "Checking for warehouse file arrivals under ${BUCKET}/${DATE_PREFIX}/"

FILE_COUNT=$(gsutil ls "${BUCKET}/${DATE_PREFIX}/*.csv" 2>/dev/null | wc -l)

log "Found ${FILE_COUNT} of ${EXPECTED_WAREHOUSES} expected warehouse files."

if [ "$FILE_COUNT" -lt "$EXPECTED_WAREHOUSES" ]; then
  log "WARNING: Only ${FILE_COUNT}/${EXPECTED_WAREHOUSES} files arrived. Proceeding anyway — missing files will alert in Cloud Monitoring."
fi

# ── 2. Trigger Dataflow job ───────────────────────────────────────────────────
log "Submitting Dataflow job for batch: ${DATE_PREFIX}"

JOB_ID=$(gcloud dataflow jobs run "inventory-ingest-${DATE_PREFIX//\//-}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --gcs-location="${TEMPLATE_PATH}" \
  --parameters \
    inputFilePattern="${BUCKET}/${DATE_PREFIX}/*.csv",\
    outputTable="${BQ_DATASET}",\
    javascriptTextTransformFunctionName="transformRow",\
    javascriptTextTransformGcsPath="${BUCKET}/udf/transform.js" \
  --format="value(id)" 2>>"$LOG_FILE")

if [ -z "$JOB_ID" ]; then
  log "ERROR: Dataflow job submission failed."
  exit 1
fi

log "Dataflow job submitted successfully. Job ID: ${JOB_ID}"

# ── 3. Archive processed CSVs ─────────────────────────────────────────────────
log "Moving raw files to archive bucket..."

gsutil -m mv \
  "${BUCKET}/${DATE_PREFIX}/*.csv" \
  "gs://xyz-logistics-archive/${DATE_PREFIX}/" \
  >> "$LOG_FILE" 2>&1

log "Pipeline trigger complete for ${DATE_PREFIX}."