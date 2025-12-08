#!/usr/bin/env bash
set -euo pipefail

# Script para executar experimentos do Clarify-Verify

CONFIG=${1:-experiments/experiment_config.yaml}
EXP_DIR=results/$(date +%Y%m%d_%H%M%S)
mkdir -p "$EXP_DIR"

echo "=========================================="
echo "Clarify-Verify: Executando Experimento"
echo "=========================================="
echo "Configuração: $CONFIG"
echo "Diretório de saída: $EXP_DIR"
echo ""

# Verifica se a API key está configurada
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "AVISO: OPENAI_API_KEY não está definida."
    echo "O sistema usará MockLLMClient para testes."
    echo ""
fi

# Executa o pipeline
python -m src.pipeline \
    --config "$CONFIG" \
    --outdir "$EXP_DIR" \
    --dataset "$(python -c "import yaml; print(yaml.safe_load(open('$CONFIG'))['dataset']['path'])")" 2>&1 | tee "$EXP_DIR/run.log"

echo ""
echo "=========================================="
echo "Experimento concluído!"
echo "Resultados em: $EXP_DIR"
echo "=========================================="

# Gera análise se houver resultados
if [ -f "$EXP_DIR/results.json" ]; then
    echo ""
    echo "Gerando análise..."
    python -m src.eval.analysis "$EXP_DIR/results.json" > "$EXP_DIR/analysis.txt"
    cat "$EXP_DIR/analysis.txt"
fi

