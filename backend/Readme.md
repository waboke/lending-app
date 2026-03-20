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