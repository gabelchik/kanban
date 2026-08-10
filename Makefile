ARGS ?=

test:
	docker compose exec backend pytest $(ARGS)

migrate:
	docker compose exec backend python manage.py migrate

dev-up:
	docker compose -f docker-compose.yml up $(ARGS)

prod-up:
	docker compose -f docker-compose.prod.yml up $(ARGS)