# Guia Rápido - Clarify-Verify

## Instalação

1. **Clone o repositório** (se aplicável)

2. **Ative o ambiente virtual** (se usar):
```bash
source ClarifyVerify/bin/activate
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure a API Key** (opcional, para usar API real):
```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

## Uso Básico

### 1. Processar um requisito único

```bash
python -m src.pipeline \
    --config experiments/experiment_config.yaml \
    --outdir results/teste \
    --requirement "Write a function to sort a list of elements"
```

### 2. Processar um dataset

```bash
python -m src.pipeline \
    --config experiments/experiment_config.yaml \
    --outdir results/experimento_001 \
    --dataset data/processed/sample_50.json
```

### 3. Usar o script de experimento

```bash
./experiments/run_experiment.sh experiments/experiment_config.yaml
```

### 4. Analisar resultados

```bash
python -m src.eval results/experimento_001/results.json
```

## Estrutura de Saída

Cada execução gera:

- `result_*.json` ou `results.json`: Resultados completos do pipeline
- `run.log`: Log da execução
- `analysis.txt`: Análise estatística (se gerado)

## Exemplo de Resultado

```json
{
  "requirement_id": "req_001",
  "original_requirement": "...",
  "refined_requirement": "...",
  "clarification_questions": [...],
  "uml_diagrams": [...],
  "generated_code": "...",
  "generated_tests": "...",
  "verification_results": [...],
  "iterations": 2,
  "final_status": "success",
  "metrics": {
    "iterations": 2,
    "tests_passed": true,
    "linter_passed": true,
    "total_verifications": 2,
    "passed_verifications": 2
  }
}
```

## Configuração

Edite `experiments/experiment_config.yaml` para:

- Mudar modelo LLM
- Ajustar número de iterações
- Habilitar/desabilitar verificações
- Configurar clarificação e geração UML

## Troubleshooting

### Erro: "OPENAI_API_KEY não está definida"
- Configure a variável de ambiente ou use MockLLMClient para testes

### Erro: "pylint não encontrado"
- Instale: `pip install pylint` ou o sistema usará flake8 como fallback

### Erro: "pytest não encontrado"
- Instale: `pip install pytest`

## Próximos Passos

1. Adicione mais requisitos em `data/processed/`
2. Experimente diferentes modelos LLM
3. Configure verificação formal (requer ferramentas adicionais)
4. Visualize diagramas UML gerados (use PlantUML online ou local)

