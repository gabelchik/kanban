test:
	docker compose exec backend pytest

migrate:
	docker compose exec backend python manage.py migrate

dev-up:
	docker compose -f docker-compose.yml up

prod-up:
	docker compose -f docker-compose.prod.yml up