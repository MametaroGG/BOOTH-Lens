from fastapi import APIRouter, Depends, Request, Header
from ..services.stripe_service import StripeService
from pydantic import BaseModel

router = APIRouter()
SERVICE = StripeService()

class CheckoutRequest(BaseModel):
    user_id: str
    email: str

@router.post("/subscription/checkout")
async def create_checkout(req: CheckoutRequest):
    url = await SERVICE.create_checkout_session(req.user_id, req.email)
    return {"url": url}

@router.post("/subscription/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    await SERVICE.handle_webhook(payload, stripe_signature)
    return {"status": "received"}
