# Documentação de Implementação - Clarify-Verify

## Visão Geral

Esta implementação estende o framework ClarifyGPT com:
1. **Geração de diagramas UML** a partir de requisitos refinados
2. **Laço de verificação automática** (testes + análise estática + verificação formal)

## Arquitetura

### Componentes Principais

#### 1. `src/clarifier.py` - Clarificação de Requisitos
- **Clarifier**: Classe principal para geração de perguntas de clarificação
- **Métodos principais**:
  - `detect_ambiguity()`: Detecta se um requisito é ambíguo
  - `generate_questions()`: Gera perguntas de clarificação
  - `refine_requirement()`: Refina requisito com base em respostas

#### 2. `src/uml_generator.py` - Geração UML
- **UMLGenerator**: Gera diagramas UML em formato PlantUML
- **Métodos principais**:
  - `generate_sequence_diagram()`: Gera diagrama de sequência
  - `generate_class_diagram()`: Gera diagrama de classes (quando aplicável)
  - `save_uml()`: Salva diagrama em arquivo

#### 3. `src/code_generator.py` - Geração de Código
- **CodeGenerator**: Gera código e testes unitários
- **Métodos principais**:
  - `generate()`: Gera código a partir de requisito refinado
  - `repair_code()`: Corrige código com base em erros de verificação

#### 4. `src/verifier.py` - Verificação Automática
- **Verifier**: Executa verificações automáticas
- **Métodos principais**:
  - `verify()`: Executa todas as verificações configuradas
  - `_run_tests()`: Executa testes unitários (pytest)
  - `_run_linter()`: Executa análise estática (pylint/flake8)
  - `_run_formal_verification()`: Verificação formal (placeholder)

#### 5. `src/pipeline.py` - Orquestrador Principal
- **Pipeline**: Orquestra todo o fluxo
- **Fluxo**:
  1. Clarificação (se habilitado)
  2. Geração UML (se habilitado)
  3. Geração de código
  4. Verificação (loop até passar ou max_iterations)

#### 6. `src/llm_client.py` - Cliente LLM
- **LLMClient**: Interface abstrata
- **OpenAIClient**: Implementação para OpenAI API
- **MockLLMClient**: Cliente mock para testes

#### 7. `src/eval/` - Avaliação
- **metrics.py**: Cálculo de métricas (Pass@1, cobertura, etc.)
- **analysis.py**: Análise e visualização de resultados

## Fluxo de Execução

```
Requisito Original
    ↓
[Clarificação] → Perguntas → Respostas → Requisito Refinado
    ↓
[Geração UML] → Diagrama PlantUML
    ↓
[Geração Código] → Código + Testes
    ↓
[Verificação] → Testes + Linter + Formal
    ↓
    ├─ Passou? → Sucesso ✓
    └─ Falhou? → [Reparo] → Loop (até max_iterations)
```

## Configuração

### Arquivo de Configuração (`experiment_config.yaml`)

```yaml
model:
  provider: openai
  name: gpt-4o-mini
  temperature: 0.0

pipeline:
  use_clarification: true
  generate_uml: true
  clarifier_max_questions: 5
  max_iterations: 3
  language: python

verify:
  run_tests: true
  run_linter: true
  run_formal: false
```

## Uso

### CLI

```bash
python -m src.pipeline \
    --config experiments/experiment_config.yaml \
    --outdir results/exp001 \
    --dataset data/processed/sample_50.json
```

### Programático

```python
from src.llm_client import OpenAIClient
from src.pipeline import Pipeline

llm_client = OpenAIClient(model='gpt-4o-mini')
pipeline = Pipeline(llm_client, config)
result = pipeline.run(requirement="...")
```

## Extensões Futuras

### Verificação Formal
- Integração com TLA+ / Alloy / SMT solvers
- Tradução automática de propriedades para formatos formais
- Geração de contra-exemplos

### Mais Tipos de Diagramas UML
- Diagrama de classes
- Diagrama de componentes
- Diagrama de estados

### Suporte a Mais Linguagens
- Java
- JavaScript/TypeScript
- C/C++

## Testes

Execute testes básicos:
```bash
python test_basic.py
```

## Estrutura de Dados

### PipelineResult
```python
{
    "requirement_id": str,
    "original_requirement": str,
    "refined_requirement": str,
    "clarification_questions": List[Dict],
    "uml_diagrams": List[Dict],
    "generated_code": str,
    "generated_tests": str,
    "verification_results": List[Dict],
    "iterations": int,
    "final_status": str,  # "success", "failed", "unknown"
    "metrics": Dict
}
```

## Dependências Principais

- `openai`: Cliente OpenAI API
- `pytest`: Execução de testes
- `pylint`/`flake8`: Análise estática
- `pyyaml`: Parsing de configuração
- `python-dotenv`: Gerenciamento de variáveis de ambiente

## Notas de Implementação

1. **MockLLMClient**: Útil para desenvolvimento sem API key
2. **Fallback de Linters**: Se pylint não estiver disponível, tenta flake8
3. **Parsing de Respostas LLM**: Tenta extrair JSON, com fallback para parsing simples
4. **Compatibilidade Python**: Testado para Python 3.8+

## Limitações Atuais

1. Verificação formal ainda não implementada (placeholder)
2. Suporte apenas para Python na verificação automática
3. Geração UML limitada a diagramas de sequência
4. Parsing de respostas LLM pode falhar em casos complexos

