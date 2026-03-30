# Lending App Backend (DRF + Docker)

This is a Nigeria-first lending backend with support for diaspora borrowers.

## Core borrower segments
- Military
- Paramilitary
- Civil servants
- Businessmen
- Nigeria residents and diaspora Nigerians

## Quick start, Run full app from root
```bash
cp .env .env.local
docker compose up --build
```

In another shell:
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py loaddata apps/loan/fixtures/loan_products.json
```

## Suggested test flow
1. Register borrower
2. Login and copy access token
3. Send OTP and verify OTP
4. Create/update profile
5. Submit KYC
6. Login as admin and approve KYC
7. Run credit evaluation
8. List loan products
9. Create loan application
10. Submit loan application
11. Login as admin and approve application
12. Disburse loan
13. View repayment schedule
14. Initiate payment
15. Trigger payment webhook

## Main endpoints
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `GET/PATCH /api/v1/auth/me/`
- `POST /api/v1/otp/send/`
- `POST /api/v1/otp/verify/`
- `GET/PATCH /api/v1/profile/`
- `GET/POST /api/v1/profile/bank-accounts/`
- `GET /api/v1/kyc/status/`
- `PATCH /api/v1/kyc/submit/`
- `POST /api/v1/kyc/review/<user_id>/approve/`
- `POST /api/v1/credit/evaluate/`
- `GET /api/v1/credit/latest/`
- `GET /api/v1/loan-products/`
- `GET/POST /api/v1/loan-applications/`
- `POST /api/v1/loan-applications/<id>/submit/`
- `POST /api/v1/loan-applications/<id>/approve/`
- `GET /api/v1/loans/`
- `POST /api/v1/loans/<id>/disburse/`
- `GET /api/v1/loans/<id>/schedule/`
- `POST /api/v1/payments/initiate/`
- `POST /api/v1/payments/webhook/`
- `GET /api/v1/payments/<id>/`

## Example borrower profile payload
```json
{
  "customer_category": "civil_servant",
  "residency_status": "resident_nigeria",
  "first_name": "Amina",
  "last_name": "Okafor",
  "date_of_birth": "1991-04-12",
  "national_id": "NAT123456",
  "bvn": "12345678901",
  "nin": "22334455667",
  "country_of_residence": "Nigeria",
  "state_of_residence": "Lagos",
  "has_nigerian_bank_account": true,
  "has_foreign_bank_account": false,
  "currency_preference": "NGN",
  "employer_name": "Ministry of Finance",
  "staff_or_service_number": "MOF-9981",
  "monthly_income": "250000.00"
}
```

## Notes
- OTP returns the code in the response for local testing only.
- KYC approval and loan approval are admin-only endpoints.
- Payments are simulated via the webhook endpoint for testing.
