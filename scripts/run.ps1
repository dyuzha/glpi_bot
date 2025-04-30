# run.ps1 - Запуск GLPI бота в Docker

# Переменные для путей
$SETTINGS_PATH = "$env:CONFIGS\settings.ini"
$LOGGING_CONFIG = "$env:CONFIGS\logging_config.json"

# Проверка существования файлов
if (-not (Test-Path $SETTINGS_PATH)) {
    Write-Host "Error: Not found file configuration to path $SETTINGS_PATH" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LOGGING_CONFIG)) {
    Write-Host "Error: Not found file configuration to path $LOGGING_CONFIG" -ForegroundColor Red
    exit 1
}

# Запуск контейнера
docker run -d `
    -v "${SETTINGS_PATH}:/glpi_bot/settings.ini" `
    -e GLPI_TG_SETTINGS_CONF="/glpi_bot/settings.ini" `
    -v "${LOGGING_CONFIG}:/glpi_bot/logging_config.json" `
    -e GLPI_TG_LOG_CONF="/glpi_bot/logging_config.json" `
    --name gbc `
    glpi_bot

# Проверка статуса
Write-Host "The container is running. Status:" -ForegroundColor Green
docker ps -f name=gbc
