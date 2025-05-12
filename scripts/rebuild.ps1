# run.ps1 - Запуск GLPI бота в Docker


docker stop gbc
docker rm gbc

# Собираем образ с тегом 'glpi_bot'
docker build -t glpi_bot .


# Переменные для путей
$SETTINGS_PATH = "$env:CONFIGS\settings.ini"
$LOGGING_CONFIG = "$env:CONFIGS\logging_config.json"
$MAIL_CONFIG = "$env:CONFIGS\mail_config.ini"


# Проверка существования файлов
if (-not (Test-Path $SETTINGS_PATH)) {
    Write-Host "Error: Not found file configuration to path $SETTINGS_PATH" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LOGGING_CONFIG)) {
    Write-Host "Error: Not found file configuration to path $LOGGING_CONFIG" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $MAIL_CONFIG)) {
    Write-Host "Error: Not found file configuration to path $LOGGING_CONFIG" -ForegroundColor Red
    exit 1
}


# Запуск контейнера
docker run -d `
    -v "${SETTINGS_PATH}:/glpi_bot/settings.ini" `
    -e GLPI_TG_SETTINGS_CONF="/glpi_bot/settings.ini" `
    -v "${LOGGING_CONFIG}:/glpi_bot/logging_config.json" `
    -e GLPI_TG_LOG_CONF="/glpi_bot/logging_config.json" `
    -v "${MAIL_CONFIG}:/glpi_bot/mail_config.ini" `
    -e GLPI_TG_MAIL_CONFIG="/glpi_bot/mail_config.ini" `
    --name gbc `
    glpi_bot


# Проверка статуса
Write-Host "The container is running. Status:" -ForegroundColor Green
docker ps -f name=gbc
