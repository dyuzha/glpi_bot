# run.ps1 - Запуск GLPI бота в Docker

docker stop gbc
docker rm gbc

# Собираем образ с тегом 'glpi_bot'
docker build -t glpi_bot .

# Проверка существования файлов
if ($GLPI_TG_CONFIG_DIR -ne $null) {
    Write-Host "Error: Not found varible: $GLPI_TG_CONFIG_DIR" -ForegroundColor Red
    exit 1
}

# Запуск контейнера
docker run -d `
    -v "${env:GLPI_TG_CONFIG_DIR}:/configs" `
    -v "${env:GLPI_TG_DATA_DIR}:/data" `
    --name gbc `
    glpi_bot

# Проверка статуса
Write-Host "The container is running. Status:" -ForegroundColor Green
docker ps -f name=gbc
