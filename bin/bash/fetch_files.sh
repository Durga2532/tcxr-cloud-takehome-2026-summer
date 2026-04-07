# Polls a remote SFTP/HTTP source for new warehouse files and copies them to GCS.

set -euo pipefail

REMOTE_HOST="${SFTP_HOST}"           # set in environment or Secret Manager
REMOTE_USER="${SFTP_USER}"
REMOTE_KEY_PATH="/secrets/sftp_key"
REMOTE_DIR="/exports/inventory"
LOCAL_STAGING="/tmp/xyz_staging"
BUCKET="gs://xyz-logistics-raw"
DATE_PREFIX=$(date -u +"%Y/%m/%d/%H")
EXPECTED_COUNT=10

log() { echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $1"; }

mkdir -p "$LOCAL_STAGING"

# ── 1. Pull files from remote SFTP ───────────────────────────────────────────
log "Connecting to ${REMOTE_HOST} to fetch inventory exports..."

sftp -i "$REMOTE_KEY_PATH" -o StrictHostKeyChecking=no \
  "${REMOTE_USER}@${REMOTE_HOST}" <<EOF
  cd ${REMOTE_DIR}
  lcd ${LOCAL_STAGING}
  mget *.csv
  bye
EOF

FETCHED=$(ls "${LOCAL_STAGING}"/*.csv 2>/dev/null | wc -l)
log "Fetched ${FETCHED} files from remote."

# ── 2. Validate file count and size ──────────────────────────────────────────
FAILED=0
for f in "${LOCAL_STAGING}"/*.csv; do
  SIZE=$(stat -c%s "$f")
  if [ "$SIZE" -lt 1024 ]; then
    log "WARNING: ${f} is suspiciously small (${SIZE} bytes). Skipping."
    FAILED=$((FAILED + 1))
    rm "$f"
  fi
done

if [ "$FETCHED" -lt "$EXPECTED_COUNT" ]; then
  log "WARNING: Expected ${EXPECTED_COUNT} files, got ${FETCHED}. Check source system."
fi

# ── 3. Upload valid files to GCS ─────────────────────────────────────────────
log "Uploading to ${BUCKET}/${DATE_PREFIX}/..."

gsutil -m cp "${LOCAL_STAGING}"/*.csv "${BUCKET}/${DATE_PREFIX}/"

log "Upload complete. ${FETCHED} files staged for pipeline."

# ── 4. Clean up local staging ─────────────────────────────────────────────────
rm -f "${LOCAL_STAGING}"/*.csv
log "Local staging cleared."