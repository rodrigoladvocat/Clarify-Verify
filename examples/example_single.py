#!/usr/bin/env python3
"""
Exemplo de uso do Clarify-Verify para um requisito único.
"""

import os
import sys
import json

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_client import MockLLMClient, OpenAIClient
from src.pipeline import Pipeline


def main():
    # Configuração
    config = {
        'use_clarification': True,
        'generate_uml': True,
        'clarifier_max_questions': 5,
        'max_iterations': 3,
        'language': 'python',
        'verify': {
            'run_tests': True,
            'run_linter': False,  # Desabilita para exemplo rápido
            'run_formal': False
        }
    }
    
    # Escolhe cliente LLM
    if os.getenv('OPENAI_API_KEY'):
        print("Usando OpenAI API...")
        llm_client = OpenAIClient(
            model='gpt-4o-mini',
            api_key=os.getenv('OPENAI_API_KEY')
        )
    else:
        print("Usando MockLLMClient (configure OPENAI_API_KEY para usar API real)...")
        llm_client = MockLLMClient()
    
    # Cria pipeline
    pipeline = Pipeline(llm_client, config)
    
    # Requisito de exemplo
    requirement = "Write a function to sort a list of elements"
    
    print(f"\nRequisito: {requirement}")
    print("="*60)
    
    # Executa pipeline
    result = pipeline.run(
        requirement=requirement,
        requirement_id="example_001",
        simulate_answers=True
    )
    
    # Exibe resultados
    print("\n" + "="*60)
    print("RESULTADOS")
    print("="*60)
    print(f"Status final: {result.final_status}")
    print(f"Iterações: {result.iterations}")
    print(f"\nMétricas:")
    for key, value in result.metrics.items():
        print(f"  {key}: {value}")
    
    if result.clarification_questions:
        print(f"\nPerguntas de clarificação: {len(result.clarification_questions)}")
        for i, q in enumerate(result.clarification_questions[:3], 1):
            print(f"  {i}. [{q['priority']}] {q['question']}")
    
    if result.uml_diagrams:
        print(f"\nDiagramas UML gerados: {len(result.uml_diagrams)}")
    
    print(f"\nCódigo gerado ({len(result.generated_code)} caracteres)")
    print(f"Testes gerados ({len(result.generated_tests)} caracteres)")
    
    # Salva resultado
    output_dir = "results/example"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "example_result.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'requirement_id': result.requirement_id,
            'original_requirement': result.original_requirement,
            'refined_requirement': result.refined_requirement,
            'final_status': result.final_status,
            'iterations': result.iterations,
            'metrics': result.metrics
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultado salvo em: {output_file}")


if __name__ == '__main__':
    main()

