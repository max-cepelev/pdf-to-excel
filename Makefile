-include .env.deploy

IMAGE_NAME ?= pdf-to-excel
PLATFORM ?= linux/amd64
TAG ?= $(shell date +%Y%m%d-%H%M)
IMAGE = $(REGISTRY)/$(IMAGE_NAME)

.PHONY: run push check-registry

## Локально: http://localhost:8000
run:
	docker compose up --build

## Собрать образ под VPS и загрузить в registry (теги: дата-время и latest)
push: check-registry
	docker buildx build --platform $(PLATFORM) -t $(IMAGE):$(TAG) -t $(IMAGE):latest --push .
	@echo "Загружено: $(IMAGE):$(TAG) и $(IMAGE):latest"
	@if [ -n "$(DOKPLOY_WEBHOOK)" ]; then curl -fsS -X POST "$(DOKPLOY_WEBHOOK)" >/dev/null && echo "Dokploy: деплой запущен"; fi

check-registry:
	@if [ -z "$(REGISTRY)" ]; then echo "Укажите REGISTRY в .env.deploy (см. .env.deploy.example)"; exit 1; fi
