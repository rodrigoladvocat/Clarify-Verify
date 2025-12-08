"""
Análise e visualização de resultados.
"""

import json
from typing import List, Dict
from .metrics import generate_summary


def analyze_results(results_file: str) -> Dict:
    """
    Analisa resultados de um arquivo JSON.
    
    Args:
        results_file: Caminho para arquivo de resultados
        
    Returns:
        Dicionário com análise completa
    """
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    summary = generate_summary(results)
    
    # Análise adicional
    failed_cases = [
        r for r in results
        if r.get('final_status') != 'success'
    ]
    
    analysis = {
        'summary': summary,
        'failed_cases': len(failed_cases),
        'failed_case_ids': [
            r.get('requirement_id') for r in failed_cases
        ],
        'success_cases': [
            r.get('requirement_id') for r in results
            if r.get('final_status') == 'success'
        ]
    }
    
    return analysis


def print_analysis(analysis: Dict):
    """Imprime análise formatada."""
    print("\n" + "="*60)
    print("ANÁLISE DE RESULTADOS")
    print("="*60)
    
    summary = analysis['summary']
    print(f"\nTotal de requisitos: {summary['total_requirements']}")
    print(f"Taxa de sucesso (Pass@1): {summary['pass_rate']:.2%}")
    print(f"Iterações médias: {summary['average_iterations']:.2f}")
    print(f"Taxa de testes passados: {summary['test_pass_rate']:.2%}")
    print(f"Taxa de linter passado: {summary['linter_pass_rate']:.2%}")
    
    vc = summary['verification_coverage']
    print(f"\nCobertura de verificação:")
    print(f"  Total: {vc.get('total', 0)}")
    print(f"  Passou: {vc.get('passed', 0)}")
    print(f"  Cobertura: {vc.get('coverage', 0):.2%}")
    
    print(f"\nCasos falhados: {analysis['failed_cases']}")
    if analysis['failed_case_ids']:
        print(f"IDs: {', '.join(analysis['failed_case_ids'][:10])}")
        if len(analysis['failed_case_ids']) > 10:
            print(f"... e mais {len(analysis['failed_case_ids']) - 10} casos")
    
    print("\n" + "="*60)

