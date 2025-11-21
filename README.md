# Clarify-Verify

**Extensão de ClarifyGPT com Verificação Formal e Geração UML**
Pipeline iterativo: *Requisito → Clarificação → UML → Código → Verificação → Retroalimentação*

---

## Resumo

Este projeto implementa e estuda uma extensão prática do artigo **ClarifyGPT**, adicionando (i) geração de diagramas UML a partir de requisitos refinados e (ii) um laço de verificação automática (testes + análise estática + verificação formal quando aplicável). O objetivo é avaliar vantagens e limitações do uso de LLMs para transformar requisitos em software confiável.

---

## Objetivos específicos

* Reproduzir o fluxo de ClarifyGPT (perguntas de clarificação) e estendê-lo com:

  * geração de UML (sequence/diagramas),
  * verificação automática (testes unitários, análise estática, model checking),
  * reexecução dos experimentos com modelos LLM mais recentes.
* Avaliar empiricamente: correção funcional, aderência ao requisito, custo/token, robustez e tipos de falhas (hallucination / misinterpretation).
* Fornecer código, prompts e datasets versionados e reprodutíveis.

---

## Estrutura do repositório

```
Clarify-Verify/
├─ data/
│  ├─ raw/                 # requisitos originais e pares referência
│  ├─ synthetic/           # casos sintéticos (ambiguidade, borda)
│  └─ refs/                # implementações de referência para avaliação
├─ prompts/                # templates de prompt (clarify, generate, verify)
├─ src/
│  ├─ pipeline.py          # orquestrador Clarify->Generate->Verify
│  ├─ clarifier.py         # gera e processa perguntas de clarificação
│  ├─ uml_generator.py     # gera UML (text->diagram spec)
│  ├─ code_generator.py    # invoca LLMs / gera código
│  ├─ verifier.py          # executa testes, análise estática, model checking
│  ├─ eval/
│  │  ├─ metrics.py
│  │  └─ analysis.py
├─ experiments/
│  ├─ experiment_config.yaml
│  └─ run_experiment.sh
├─ notebooks/
├─ results/
├─ README.md
└─ LICENSE
```

---

## Como o pipeline funciona (visão prática)

1. **Entrada:** requisito textual (user story ou especificação curta).
2. **Clarifier (LLM):** gera 3–7 perguntas de esclarecimento; respostas podem ser humanas, simuladas (gold) ou automáticas.
3. **Generate (LLM):** com requisito refinado, gera:

   * descrição de design e UML (representação textual, p.ex. PlantUML),
   * código (ex.: funções Python ou Java).
4. **Verify:** roda testes unitários de referência; executa análise estática (linters, cobertura básica); quando aplicável, traduz propriedade para formato do verificador (p.ex. TLA+/Alloy/SMT) e tenta provar/checar propriedades.
5. **Retroalimentação:** falhas de verificação são transformadas em instruções para o LLM corrigir o código (loop).
6. **Saída:** versão final do código + relatório de métricas.

---

## Experimentos propostos (mínimo viável)

### Experimento 1 — Qualidade funcional (Métricas primárias)

* **Amostra:** 50 requisitos (mix real + sintético).
* **Estratégias:** Direct (LLM→código), Clarify (LLM gera perguntas + respostas simuladas), Clarify+Verify.
* **Métrica principal:** % testes unitários passados.
* **Saída:** tabela comparativa, análise estatística (p.ex. Wilcoxon), exemplos de falhas.

### Experimento 2 — Economia de iterações

* Medir número médio de iterações humanas necessárias até versão aceitável (comparar Direct vs Clarify).

### Experimento 3 — Robustez a reformulação

* Tomar 20 requisitos e reformulá-los (sinônimos, ordem de frases); medir variação da performance.

### Experimento 4 — Comparativo de modelos

* Testar 3 modelos representativos (ex.: GPT-family fechado, Llama-family aberto grande, modelo aberto menor).
* Métricas de custo (tokens), qualidade e tempo.

---

## Métricas a coletar

* Correção funcional: % de testes passados.
* Aderência ao requisito: avaliação humana (escala 0–2: divergente/parcial/fiel).
* Número de iterações de clarificação.
* Tokens / custo por caso.
* Cobertura de verificação: propriedades provadas/contraprovas.
* Linters / complexidade do código.

---

## Templates de prompt (versão inicial)

> **Prompt: Clarificação (Clarify prompt)**

```
Você é um analista de requisitos. Receba o requisito abaixo e gere até 7 perguntas de esclarecimento necessárias para que um desenvolvedor gere um código correto e não ambíguo. Classifique cada pergunta como [Obrigatória|Desejável]. Dê também um motivo curto para cada pergunta.

Requisito:
"""{requisito_text}"""
```

> **Prompt: Geração UML (UML prompt)**

```
Com base no requisito final (após respostas às perguntas), gere uma especificação em PlantUML de:
- Sequência principal do fluxo de eventos
- Principais atores/componenetes
Adicione anotações breves sobre invariantes e pré-condições.
Requisito final:
"""{requisito_final}"""
```

> **Prompt: Geração de Código (Generate prompt)**

```
Você é um desenvolvedor. Implemente a(s) função(ões) necessárias conforme o requisito final abaixo. Inclua comentários explicativos e escreva testes unitários (pytest/unittest). Evite usar bibliotecas externas exceto as padrão.

Requisito final:
"""{requisito_final}"""
```

> **Prompt: Correção com base em falha (Repair prompt)**

````
O seguinte teste falhou: {erro_resumo}. Mostre uma correção para o código abaixo explicando a causa e a mudança. Forneça apenas o patch (diff) e um breve racional.
Código:
```{codigo_atual}```
````

---

## Exemplo minimal de `experiment_config.yaml`

```yaml
# experiments/experiment_config.yaml
model:
  provider: openai
  name: gpt-4o-mini   # substitua conforme disponibilidade
  temperature: 0.0

dataset:
  path: data/processed/sample_50.json
  seed: 42

pipeline:
  clarifier_max_questions: 5
  max_iterations: 3

verify:
  run_tests: true
  run_linter: true
  run_formal: true
```

---

## Script de execução inicial (`run_experiment.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG=${1:-experiments/experiment_config.yaml}
EXP_DIR=results/$(date +%Y%m%d_%H%M%S)
mkdir -p "$EXP_DIR"

echo "Rodando experimento com config: $CONFIG"
python src/pipeline.py --config "$CONFIG" --outdir "$EXP_DIR"

echo "Resultados em $EXP_DIR"
```

---

## Como começar rápido (MVP)

1. Clonar repo
2. `pip install -r requirements.txt`
3. Colocar API keys no ambiente (ex.: `OPENAI_API_KEY`)
4. Preparar `data/processed/sample_50.json` com 50 requisitos
5. Rodar: `./experiments/run_experiment.sh experiments/experiment_config.yaml`

---

## Contribuições

1. Abra uma issue descrevendo a proposta.
2. Submeta PR com testes e documentação.
3. Documente prompts e seeds de experimento.

---

## Referências

* *ClarifyGPT: A Framework for Enhancing LLM-Based Code Generation via Requirements Clarification*
* *Supporting Software Formal Verification with Large Language Models: An Experimental Study*
* *Model Generation with LLMs: From Requirements to UML Sequence Diagrams*
