#!/bin/bash
# Script para liberar puertos comunes
# Uso: bash free_port.sh [puerto]

PORT=${1:-5000}

echo "🔍 Buscando procesos en puerto $PORT..."

# Detectar el sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PIDS=$(lsof -i :$PORT | awk 'NR!=1 {print $2}')
    
    if [ -z "$PIDS" ]; then
        echo "✅ Puerto $PORT está libre"
        exit 0
    fi
    
    echo "⚠️  Procesos encontrados:"
    lsof -i :$PORT
    
    echo ""
    read -p "¿Deseas terminar estos procesos? (s/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        for PID in $PIDS; do
            echo "❌ Terminando proceso $PID..."
            kill -9 $PID 2>/dev/null && echo "✅ Proceso $PID terminado" || echo "⚠️  No se pudo terminar $PID"
        done
    fi
else
    # Linux
    PIDS=$(netstat -tuln 2>/dev/null | grep ":$PORT " | awk '{print $NF}' | cut -d'/' -f1)
    
    if [ -z "$PIDS" ]; then
        echo "✅ Puerto $PORT está libre"
        exit 0
    fi
    
    echo "⚠️  Procesos encontrados:"
    sudo netstat -tuln | grep ":$PORT "
    
    echo ""
    read -p "¿Deseas terminar estos procesos? (s/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        for PID in $PIDS; do
            echo "❌ Terminando proceso $PID..."
            sudo kill -9 $PID 2>/dev/null && echo "✅ Proceso $PID terminado" || echo "⚠️  No se pudo terminar $PID"
        done
    fi
fi

echo ""
sleep 1
echo "✅ Puerto $PORT liberado"
