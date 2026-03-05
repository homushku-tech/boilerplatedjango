DOCKER_COMPOSE := docker compose --env-file .env
SETUP_CFG := pyproject.toml

.PHONY: run build migrations migrate shell superuser test stop logs

run:
	$(DOCKER_COMPOSE) up

run-d:
	$(DOCKER_COMPOSE) up -d

build:
	$(DOCKER_COMPOSE) build

stop:
	$(DOCKER_COMPOSE) stop

down:
	$(DOCKER_COMPOSE) down -v

migrations:
	$(DOCKER_COMPOSE) exec backend python manage.py makemigrations

migrate:
	$(DOCKER_COMPOSE) exec backend python manage.py migrate

shell:
	$(DOCKER_COMPOSE) exec backend python manage.py shell

superuser:
	$(DOCKER_COMPOSE) exec backend python manage.py init_admin

test:
	$(DOCKER_COMPOSE) exec backend python manage.py test

logs:
	$(DOCKER_COMPOSE) logs -f

restart:
	$(DOCKER_COMPOSE) restart

ps:
	$(DOCKER_COMPOSE) ps

check:
	$(DOCKER_COMPOSE) exec backend ruff check --config $(SETUP_CFG) .

format:
	$(DOCKER_COMPOSE) exec backend ruff format --config $(SETUP_CFG) .

help:
	@echo "Доступные команды:"
	@echo "  make run        - Запустить контейнеры в интерактивном режиме"
	@echo "  make run-d      - Запустить контейнеры в фоне"
	@echo "  make build      - Собрать образы"
	@echo "  make stop       - Остановить контейнеры"
	@echo "  make down       - Остановить и удалить контейнеры"
	@echo "  make migrations - Создать миграции"
	@echo "  make migrate    - Применить миграции"
	@echo "  make shell      - Открыть shell Django"
	@echo "  make superuser  - Создать суперпользователя"
	@echo "  make test       - Запустить тесты"
	@echo "  make logs       - Показать логи"
	@echo "  make restart    - Перезапустить контейнеры"
	@echo "  make ps         - Показать состояние контейнеров"
	@echo "  make lint       - Запустить линтер"
	@echo "  make format     - Запустить форматер"