#!/bin/bash
# =============================================================================
# Script de Diagnostico de Portas e Servicos - Servidor 10.2.1.208
# Projeto RADAR - Roraima Energia
# =============================================================================

echo "=============================================="
echo "  DIAGNOSTICO DE PORTAS E SERVICOS"
echo "  Servidor: $(hostname) - $(hostname -I | awk '{print $1}')"
echo "  Data: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# 1. PORTAS EM USO (TCP)
# -----------------------------------------------------------------------------
echo ">>> [1/6] PORTAS TCP EM USO (LISTENING)"
echo "----------------------------------------------"
ss -tlnp 2>/dev/null | grep LISTEN | sort -t: -k2 -n || \
netstat -tlnp 2>/dev/null | grep LISTEN | sort -t: -k4 -n
echo ""

# -----------------------------------------------------------------------------
# 2. PORTAS CRITICAS PARA O RADAR
# -----------------------------------------------------------------------------
echo ">>> [2/6] STATUS DAS PORTAS DO RADAR"
echo "----------------------------------------------"
PORTAS_RADAR="80 443 3000 6379 8000 9090"

for porta in $PORTAS_RADAR; do
    resultado=$(ss -tlnp 2>/dev/null | grep ":$porta " || netstat -tlnp 2>/dev/null | grep ":$porta ")
    if [ -n "$resultado" ]; then
        servico=$(echo "$resultado" | awk '{print $NF}' | sed 's/.*"\(.*\)".*/\1/' | head -1)
        echo "  Porta $porta: EM USO - $servico"
    else
        echo "  Porta $porta: LIVRE"
    fi
done
echo ""

# -----------------------------------------------------------------------------
# 3. CONTAINERS DOCKER EM EXECUCAO
# -----------------------------------------------------------------------------
echo ">>> [3/6] CONTAINERS DOCKER EM EXECUCAO"
echo "----------------------------------------------"
if command -v docker &> /dev/null; then
    docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" 2>/dev/null || echo "  Erro ao listar containers"
else
    echo "  Docker nao instalado"
fi
echo ""

# -----------------------------------------------------------------------------
# 4. REDES DOCKER
# -----------------------------------------------------------------------------
echo ">>> [4/6] REDES DOCKER"
echo "----------------------------------------------"
if command -v docker &> /dev/null; then
    docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" 2>/dev/null || echo "  Erro ao listar redes"
else
    echo "  Docker nao instalado"
fi
echo ""

# -----------------------------------------------------------------------------
# 5. MAPEAMENTO COMPLETO DE PORTAS DOS CONTAINERS
# -----------------------------------------------------------------------------
echo ">>> [5/6] MAPEAMENTO DE PORTAS DOS CONTAINERS"
echo "----------------------------------------------"
if command -v docker &> /dev/null; then
    docker ps -q 2>/dev/null | while read container_id; do
        nome=$(docker inspect --format '{{.Name}}' $container_id | sed 's/\///')
        portas=$(docker inspect --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}{{$p}} -> {{(index $conf 0).HostPort}}{{end}} {{end}}' $container_id)
        if [ -n "$portas" ]; then
            echo "  $nome: $portas"
        fi
    done
else
    echo "  Docker nao instalado"
fi
echo ""

# -----------------------------------------------------------------------------
# 6. SERVICOS SYSTEMD RELACIONADOS
# -----------------------------------------------------------------------------
echo ">>> [6/6] SERVICOS SYSTEMD (web/db/cache)"
echo "----------------------------------------------"
systemctl list-units --type=service --state=running 2>/dev/null | grep -E "nginx|apache|httpd|docker|redis|oracle|postgres|mysql|mongo" || echo "  Nenhum servico relevante encontrado"
echo ""

# -----------------------------------------------------------------------------
# RESUMO - PORTAS PARA O RADAR
# -----------------------------------------------------------------------------
echo "=============================================="
echo "  RESUMO - PORTAS NECESSARIAS PARA O RADAR"
echo "=============================================="
echo ""
echo "  Porta  | Servico           | Uso"
echo "  -------|-------------------|------------------"
echo "  80     | NGINX             | HTTP Redirect"
echo "  443    | NGINX             | HTTPS (SSL)"
echo "  3000   | Grafana           | Dashboards"
echo "  6379   | Redis             | Cache (interno)"
echo "  8000   | FastAPI           | API (interno)"
echo "  9090   | Prometheus        | Metricas"
echo ""
echo "=============================================="
echo "  COMANDOS UTEIS"
echo "=============================================="
echo ""
echo "  # Ver processo em porta especifica:"
echo "  sudo lsof -i :PORTA"
echo ""
echo "  # Ver todos os containers e portas:"
echo "  docker ps -a --format 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'"
echo ""
echo "  # Ver logs de container:"
echo "  docker logs -f NOME_CONTAINER"
echo ""
echo "  # Parar container que usa porta:"
echo "  docker stop NOME_CONTAINER"
echo ""
echo "=============================================="
