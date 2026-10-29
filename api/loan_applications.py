import logging

from fastapi import APIRouter, Header
from pydantic import BaseModel

from api.privacy import redact_pii

logger = logging.getLogger("finhealth.loans")
router = APIRouter()


class LoanApplicant(BaseModel):
    full_name: str
    phone: str
    national_id: str
    requested_amount: int


@router.post("/v1/loan-applications")
async def create_application(applicant: LoanApplicant, x_tenant_id: str = Header(...)):
    logger.info(f"new application phone={applicant.phone} national_id={applicant.national_id}")
    return {"status": "received", "tenant": x_tenant_id}
