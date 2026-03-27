

# Lending App Setup Guide

##  1. Clone the repository

git clone https://github.com/waboke/lending-app.git

## 2. Navigate into the project

cd lending-app

##  3. Create environment file inside the backend folder

Copy the example file:
cp .env .env

##  4. Make sure Docker is installed

Check:
docker --version
docker-compose --version
# If not installed, install Docker first.
# start docker deamon
# Check if Docker is running
docker info
# Start Docker

sudo systemctl start docker
# Then enable it:
sudo systemctl enable docker
# If Docker is running but still failing:
sudo usermod -aG docker $USER
# Then log out and log back in, or run:
newgrp docker
# Point to correct socket
export DOCKER_HOST=unix:///var/run/docker.sock
# try this
docker ps
# Verify everything works
docker run hello-world
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

#
# Setup the repository
#

# Install the public key for the repository (if not done previously):
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

# Create the repository configuration file:
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

#
# Install pgAdmin
#

# Install for both desktop and web modes:
sudo apt install pgadmin4

# Install for desktop mode only:
sudo apt install pgadmin4-desktop

# Install for web mode only: 
sudo apt install pgadmin4-web 

# Configure the webserver, if you installed pgadmin4-web:
sudo /usr/pgadmin4/bin/setup-web.sh