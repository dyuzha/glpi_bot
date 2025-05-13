.PHONY: build run stop clean clean-containe rebuild

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
	@echo "Удаление только контейнера"
	@./scripts/clean.sh

full-clean: stop
	@echo "Полная очистка (контейнер + образ)..."
	@./scripts/clean-full.sh

rebuild: clean build run
