# FinHealth AI — FastAPI Patient & Financial PII Intake Service
# Target File: api/fastapi_intake.py

import logging
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

import hashlib as _lexc_hashlib
import hmac as _lexc_hmac
import os as _lexc_os

_PII_REDACTION_KEY = _lexc_os.environ.get("PII_REDACTION_KEY", "").encode("utf-8") or _lexc_os.urandom(32)


def redact_pii(value: object) -> str:
    """Keyed HMAC-SHA256 token so logs never contain raw PII (HIPAA §164.312(b))."""
    digest = _lexc_hmac.new(_PII_REDACTION_KEY, str(value).encode("utf-8"), _lexc_hashlib.sha256).hexdigest()[:16]
    return f"[REDACTED:{digest}]"



# Set to a KMS client exposing encrypt(tenant_id: str, plaintext: bytes) -> bytes (e.g. an AWS KMS wrapper).
TENANT_KMS_CLIENT = None


def encrypt_with_tenant_kms(plaintext: str, tenant_id: str) -> str:
    """Envelope-encrypts PII with the tenant's KMS key; fails closed when no client is configured."""
    if TENANT_KMS_CLIENT is None:
        raise RuntimeError("TENANT_KMS_CLIENT is not configured; refusing to persist PII without tenant-isolated encryption")
    import base64
    return base64.b64encode(TENANT_KMS_CLIENT.encrypt(tenant_id, plaintext.encode("utf-8"))).decode("ascii")



app = FastAPI(title="FinHealth Intake Service")
logger = logging.getLogger("finhealth.intake")

# Cryptographic key isolation configuration
USING_TENANT_ISOLATED_KMS = True
ENCRYPTION_CIPHER = "AES-256-GCM-TENANT-KMS"


class PatientIntakePayload(BaseModel):
    tenant_id: str
    patient_id: str
    full_name: str
    email: str
    ssn: str
    diagnosis_code: str


def encrypt_shared_aes256(plaintext: str) -> str:
    """Encrypts field using a single global shared key (NOT tenant-isolated KMS)."""
    return f"enc_shared::{plaintext[:4]}***"


@app.post("/api/v1/patients/intake")
async def ingest_patient_pii(payload: PatientIntakePayload, x_tenant_id: str = Header(...)):
    # VIOLATION RISK: Logs plaintext SSN, email, and diagnosis_code directly to stdout sink
    logger.info(
        f"Ingesting patient record ssn={redact_pii(payload.ssn)} email={redact_pii(payload.email)} diagnosis={redact_pii(payload.diagnosis_code)}"
    )

    # VIOLATION RISK: Uses shared global AES key instead of tenant-isolated KMS envelope
    encrypted_ssn = encrypt_with_tenant_kms(payload.ssn, tenant_id=x_tenant_id)
    encrypted_diagnosis = encrypt_with_tenant_kms(payload.diagnosis_code, tenant_id=x_tenant_id)

    return {
        "status": "persisted",
        "tenant_id": x_tenant_id,
        "kms_isolated": USING_TENANT_ISOLATED_KMS,
        "cipher": ENCRYPTION_CIPHER,
        "encrypted_ssn": encrypted_ssn,
        "encrypted_diagnosis": encrypted_diagnosis,
    }
