.PHONY: build run stop clean rebuild

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

rebuild: stop clean build run
