
docker-compose down --volumes --remove-orphans
docker system prune -f
docker-compose up --build

# Run server
docker-compose up

docker-compose up --build

docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Create New App
docker-compose exec web python manage.py startapp loans
# Run migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# github

git init
git add .
git commit -m "Initial commit"

# Clone and build 
git clone https://github.com/waboke/lending-app.git
cd lending-app/backend
docker-compose up --build

# Lending App Setup Guide

##  1. Clone the repository

git clone https://github.com/waboke/lending-app.git

## 2. Navigate into the project

cd lending-app/backend

##  3. Create environment file

Copy the example file:
cp .env.example .env

##  4. Make sure Docker is installed

Check:
docker --version
docker-compose --version

If not installed, install Docker first.

##  5. Run the application

docker-compose up --build

## stop only react container
docker-compose stop react
## stop everthing
docker-compose down
## Start only the backend
docker-compose up web

##  6. Run database migrations (first time only)

Open a new terminal and run:
docker-compose exec web python manage.py migrate 


##  7. Create admin user (optional)

docker-compose exec web python manage.py createsuperuser

##  8. Access the application

http://localhost:8080


##  9. Running commands (IMPORTANT)

Always run Django commands like this:

docker-compose exec web python manage.py <command>

Example:
docker-compose exec web python manage.py makemigrations

##  10. Stop the application

Press CTRL + C or run:
docker-compose down

##  11. If something breaks

Try:

docker-compose down
docker-compose up --build

##  Notes

* Do NOT commit the `.env` file
* Use `.env.example` as a reference
* Make sure ports like 8080 are free
* First run may take a few minutes

##  Team Workflow (IMPORTANT)

### Create a new branch before working

git checkout -b feature-your-feature-name

### Push your branch

git push origin feature-your-feature-name

### Then create a Pull Request on GitHub
