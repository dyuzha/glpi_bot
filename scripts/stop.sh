#!/bin/bash

docker stop gbc 2>/dev/null && echo "Контейнер остановлен" || \
    echo "Контейнер не найден"
