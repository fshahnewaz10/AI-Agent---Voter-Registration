import os
import json
import logging
import azure.functions as func
from azure.functions import FunctionApp, AuthLevel

# v2 programming model entrypoint
app = FunctionApp(http_auth_level=AuthLevel.FUNCTION)

# Required by your assignment/tool schema
REQUIRED_FIELDS = ["name", "dob", "address", "status", "registration_id"]

# App Settings (Azure) / local.settings.json (local)
# STORAGE_ACCOUNT_URL = "https://<account>.blob.core.windows.net"
# STORAGE_CONTAINER   = "voter-test"
STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL")
STORAGE_CONTAINER = os.environ.get("STORAGE_CONTAINER", "voter-test")


def _validate_record(rec: dict) -> tuple[bool, str | None]:
    """Validate that required fields exist and are non-empty."""
    missing = [k for k in REQUIRED_FIELDS if not rec.get(k)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, None


def _init_blob_client():
    """
    Create a BlobServiceClient using DefaultAzureCredential.
    - In Azure: uses Managed Identity automatically.
    - Locally: uses your dev login (az login / VS Code sign-in) if available.
    """
    # Lazy import so function discovery doesn't break if deps aren't installed yet.
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient

    if not STORAGE_ACCOUNT_URL:
        raise ValueError("STORAGE_ACCOUNT_URL is not set.")

    credential = DefaultAzureCredential()
    return BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)


def _ensure_container_exists(bsc):
    """Create the container if it doesn't exist (safe if it already exists)."""
    try:
        bsc.create_container(STORAGE_CONTAINER)
    except Exception:
        # Likely already exists; ignore.
        pass


def _write_record_to_blob(bsc, rec: dict) -> str:
    """
    Write one record as <registration_id>.json into STORAGE_CONTAINER.
    Returns the blob path.
    """
    reg_id = rec["registration_id"].strip()
    blob_name = f"{reg_id}.json"

    blob_client = bsc.get_blob_client(container=STORAGE_CONTAINER, blob=blob_name)
    payload = json.dumps(rec, ensure_ascii=False).encode("utf-8")
    blob_client.upload_blob(payload, overwrite=True)
    return f"{STORAGE_CONTAINER}/{blob_name}"


@app.route(route="new_store_record", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def new_store_record(req: func.HttpRequest) -> func.HttpResponse:
    """
    POST /api/new_store_record
    Accepts either:
      - a single object {name, dob, address, status, registration_id}
      - or an array of those objects
    Writes each record as a JSON blob to the configured storage container.
    """
    logging.info("new_store_record invoked")

    # Parse JSON
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid or missing JSON body"}),
            status_code=400,
            mimetype="application/json",
        )

    # Normalize to list for uniform handling
    items = body if isinstance(body, list) else [body]

    # Initialize storage client
    try:
        bsc = _init_blob_client()
        _ensure_container_exists(bsc)
    except Exception as ex:
        logging.exception("Storage client initialization failed")
        return func.HttpResponse(
            json.dumps({"error": f"Storage init failed: {str(ex)}"}),
            status_code=500,
            mimetype="application/json",
        )

    results = []
    stored_count = 0

    for rec in items:
        if not isinstance(rec, dict):
            results.append({"status": "not_stored", "error": "Each item must be a JSON object"})
            continue

        ok, err = _validate_record(rec)
        if not ok:
            results.append({
                "registration_id": rec.get("registration_id"),
                "status": "not_stored",
                "error": err
            })
            continue

        try:
            blob_path = _write_record_to_blob(bsc, rec)
            stored_count += 1
            results.append({
                "registration_id": rec["registration_id"],
                "status": "stored",
                "blob": blob_path
            })
        except Exception as ex:
            logging.exception("Blob write failed")
            results.append({
                "registration_id": rec.get("registration_id"),
                "status": "not_stored",
                "error": str(ex)
            })

    # Response shape: single vs batch
    response_payload = results[0] if isinstance(body, dict) else {
        "count": len(results),
        "stored": stored_count,
        "items": results
    }

    return func.HttpResponse(
        json.dumps(response_payload),
        status_code=200,
        mimetype="application/json",
    )