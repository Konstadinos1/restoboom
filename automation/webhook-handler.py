"""
ReplyAI Webhook Handler

Optional standalone webhook server for receiving Stripe events
and triggering client onboarding. Use this if you want more control
than Make.com provides, or as a backup integration.

Run: python webhook-handler.py
Requires: STRIPE_WEBHOOK_SECRET and OPENAI_API_KEY env vars
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

import stripe

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
PORT = int(os.environ.get("PORT", 8080))


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/webhook/stripe":
            self._handle_stripe_webhook()
        else:
            self._respond(404, {"error": "Not found"})

    def _handle_stripe_webhook(self):
        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length)
        sig_header = self.headers.get("Stripe-Signature", "")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET
            )
        except ValueError:
            self._respond(400, {"error": "Invalid payload"})
            return
        except stripe.error.SignatureVerificationError:
            self._respond(400, {"error": "Invalid signature"})
            return

        if event["type"] == "customer.subscription.created":
            self._handle_new_subscription(event["data"]["object"])
        elif event["type"] == "customer.subscription.deleted":
            self._handle_cancelled_subscription(event["data"]["object"])
        elif event["type"] == "invoice.payment_failed":
            self._handle_payment_failed(event["data"]["object"])

        self._respond(200, {"status": "ok"})

    def _handle_new_subscription(self, subscription):
        customer_id = subscription["customer"]
        customer = stripe.Customer.retrieve(customer_id)

        client_data = {
            "email": customer.get("email"),
            "name": customer.get("name"),
            "business_name": customer.get("metadata", {}).get("business_name"),
            "google_maps_url": customer.get("metadata", {}).get("google_maps_url"),
            "subscription_id": subscription["id"],
            "plan": subscription["items"]["data"][0]["price"]["id"],
        }

        print(f"[NEW CLIENT] {client_data['business_name']} — {client_data['email']}")
        # TODO: Create Airtable record via API
        # TODO: Trigger welcome email
        # TODO: Run initial review scrape

    def _handle_cancelled_subscription(self, subscription):
        customer_id = subscription["customer"]
        print(f"[CANCELLED] Customer {customer_id} — Subscription {subscription['id']}")
        # TODO: Update Airtable record status to "cancelled"
        # TODO: Send cancellation confirmation email

    def _handle_payment_failed(self, invoice):
        customer_id = invoice["customer"]
        print(f"[PAYMENT FAILED] Customer {customer_id} — Invoice {invoice['id']}")
        # TODO: Update Airtable record with payment failure flag
        # TODO: Send payment failure notification

    def _respond(self, status_code, body):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


def main():
    if not WEBHOOK_SECRET:
        print("WARNING: STRIPE_WEBHOOK_SECRET not set. Signature verification disabled.")

    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    print(f"ReplyAI webhook handler running on port {PORT}")
    print(f"Stripe webhook endpoint: http://localhost:{PORT}/webhook/stripe")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
