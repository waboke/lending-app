# Lending Fullstack Structure

This package is organized into two folders:

- `backend/` - Django REST Framework backend
- `frontend/` - React frontend built with Vite

## Backend
The backend folder contains the lending API, Docker files, Compose files, Postman collection, and README from the DRF implementation.

## Frontend
The frontend folder contains a minimal React app that can test the main lending flows against the DRF backend.

### Start frontend
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

### Default API base URL
`http://localhost:8000/api/v1`

## Suggested local run order

### Terminal 1
```bash
cd backend
docker compose up --build
```

### Terminal 2
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
# run from root dir
docker compose up --build

Then open:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Django admin: `http://localhost:8000/admin`
# If frontend is too slow in Docker, you can still run it locally:
# Disable frontend container temporarily
# Comment out this block in compose:
``` 
# frontend:
#   ...
```
# Then run:

cd frontend
npm install
npm run dev

# If backend starts before DB is ready, you may see errors.
# If that happens, restart:

docker compose restart backend
# Stop and remove this project (safe reset)

## 1. Run this inside your project folder:

docker compose down --volumes --remove-orphans

## 2. Then remove any leftover containers:

docker ps -a
docker rm -f $(docker ps -aq)

# Remove images (clean rebuild)
docker images
docker rmi -f $(docker images -q)

# Remove volumes (important for Django/DB reset)
## This deletes database data
docker volume ls
docker volume rm $(docker volume ls -q)
# Remove networks
docker network prune -f
# One-command full cleanup (recommended)
docker system prune -a --volumes -f
#   docker system prune -a --volumes -f
sudo systemctl stop docker
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
sudo systemctl start docker