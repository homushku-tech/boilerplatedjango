run:
    docker-compose up

build:
    docker-compose build

migrations:
    docker-compose run web python manage.py makemigrations

migrate:
    docker-compose run web python manage.py migrate

shell:
    docker-compose run web python manage.py shell

superuser:
    docker-compose run web python manage.py createsuperuser

test:
    docker-compose run web python manage.py test