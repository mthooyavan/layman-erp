build:
	docker-compose build --compress

clean:
	docker system prune -f -a --filter "until=24h"

start:
	docker-compose up web

down:
	docker-compose down --remove-orphans

migrate:
	docker-compose run --rm web python3 manage.py migrate

makemigrations:
	docker-compose run --rm web python3 manage.py makemigrations

mergemigrations:
	docker-compose run --rm web python3 manage.py makemigrations --merge

console:
	docker-compose run web python3 manage.py shell_plus

pip-update:
	docker-compose run web pip-compile

pip-install:
	docker-compose run web pip install -r requirements.txt
