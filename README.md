# Nigeria Lending Fullstack

This package contains a fullstack lending starter with:
- `backend/` Django REST Framework API
- `frontend/` React + Vite frontend
- `compose.yaml` at the root for the whole stack
- branch-office administration for Nigeria operations
- customer categories: military, paramilitary, civil servant, private sector, businessman
- residency handling for Nigeria residents and diaspora users

## Core business features
- customer registration and JWT login
- OTP send and verify
- profile management with branch selection
- KYC submission and approval
- risk segmentation and credit evaluation
- loan products, applications, recommendation, approval, disbursement
- repayment schedule generation
- payment initiation and webhook simulation
- branch dashboard and branch-scoped staff queue

## Run everything
```bash
cd nigeria-lending-fullstack
cp frontend/.env.example frontend/.env

docker compose up --build
```

## Run only the backend services
```bash
docker compose up backend db redis --build
```

## Run frontend locally
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Useful URLs
- frontend: http://localhost:5173
- backend API: http://localhost:8000
- admin: http://localhost:8000/admin

## Django setup after containers start
```bash
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py loaddata apps/branch/fixtures/branches.json
docker compose exec backend python manage.py loaddata apps/loan/fixtures/loan_products.json
```

## Important note about migrations
The package includes model code but no generated migration files beyond placeholders. Create them after extracting:
```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

## Staff / branch model
- each customer has a `home_branch`
- diaspora customers must choose a servicing branch in Nigeria
- branch staff can only view and act on cases in their own branch
- head office and super admins can view everything

## Suggested manual test flow
1. Register customer
2. Login and copy access token
3. Send OTP and verify OTP
4. Save profile with `home_branch`
5. Submit KYC
6. Approve KYC from admin or staff account
7. Run credit evaluation
8. Create loan application
9. Submit application
10. Branch recommend the application
11. Approve application
12. Disburse loan
13. Initiate payment
14. Trigger webhook

## Postman
Import the root `postman_collection.json` file.
