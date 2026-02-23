import stripe
import os
from ..db import get_db_connection
from fastapi import HTTPException
# from prisma.enums import Plan

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = "http://localhost:3000"  # Frontend URL

class StripeService:
    def __init__(self):
        self.price_id_premium = os.getenv("STRIPE_PRICE_ID_PREMIUM") # Add to .env

    async def create_checkout_session(self, user_id: str, email: str):
        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=email,
                line_items=[
                    {
                        'price': self.price_id_premium,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=DOMAIN + '/pricing?success=true',
                cancel_url=DOMAIN + '/pricing?canceled=true',
                metadata={
                    "user_id": user_id
                }
            )
            return checkout_session.url
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def handle_webhook(self, payload: bytes, sig_header: str):
        endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET") # Add to .env

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session.get("metadata", {}).get("user_id")
            stripe_customer_id = session.get("customer")
            
            if user_id:
                await self._update_user_plan(user_id, "PREMIUM", stripe_customer_id)

        elif event['type'] == 'customer.subscription.deleted':
             # Downgrade to FREE
             subscription = event['data']['object']
             stripe_customer_id = subscription.get("customer")
             await self._downgrade_user_by_stripe_id(stripe_customer_id)

        return {"status": "success"}

    async def _update_user_plan(self, user_id: str, plan: str, stripe_id: str):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("UPDATE User SET plan = ?, stripeId = ? WHERE id = ?", (plan, stripe_id, user_id))
            conn.commit()
        finally:
            conn.close()

    async def _downgrade_user_by_stripe_id(self, stripe_id: str):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("UPDATE User SET plan = 'FREE' WHERE stripeId = ?", (stripe_id,))
            conn.commit()
        finally:
            conn.close()
