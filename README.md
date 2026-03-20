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
