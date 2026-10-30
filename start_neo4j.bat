@echo off
set "DOCKER_BIN=C:\Users\shlok\AppData\Local\Programs\DockerDesktop\resources\bin"
set "PATH=%DOCKER_BIN%;%PATH%"

docker ps | findstr /i "aegis-neo4j-1" >nul
if %ERRORLEVEL% equ 0 (
    echo Neo4j container is ALREADY RUNNING and ready at http://localhost:7474!
    exit /b 0
)

echo Launching Neo4j container via Docker Desktop...
docker compose up -d neo4j
