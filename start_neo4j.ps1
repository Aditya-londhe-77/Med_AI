$dockerBin = "C:\Users\shlok\AppData\Local\Programs\DockerDesktop\resources\bin"
$env:PATH = "$dockerBin;$env:PATH"

$running = docker ps --filter "name=aegis-neo4j-1" --format "{{.Names}}"
if ($running -match "aegis-neo4j-1") {
    Write-Host "Neo4j container is ALREADY RUNNING and ready at http://localhost:7474!" -ForegroundColor Green
    exit 0
}

Write-Host "Launching Neo4j container via Docker Desktop..." -ForegroundColor Cyan
docker compose up -d neo4j
