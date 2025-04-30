.PHONY: build run stop clean

build:
	@echo "Сборка Docker-образа..."
	@./scripts/build.sh

run:
	@echo "Запуск контейнера..."
	@./scripts/run.sh

stop:
	@echo "Остановка контейнера..."
	@./scripts/stop.sh

clean: stop
	@echo "Очистка..."
	@./scripts/clean.sh
