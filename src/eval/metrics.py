"""
Métricas de avaliação do pipeline.
"""

from typing import List, Dict
import statistics


def calculate_pass_rate(results: List[Dict]) -> float:
    """
    Calcula taxa de sucesso (Pass@1).
    
    Args:
        results: Lista de resultados do pipeline
        
    Returns:
        Taxa de sucesso (0.0 a 1.0)
    """
    if not results:
        return 0.0
    
    passed = sum(1 for r in results if r.get('final_status') == 'success')
    return passed / len(results)


def calculate_average_iterations(results: List[Dict]) -> float:
    """Calcula número médio de iterações até sucesso."""
    if not results:
        return 0.0
    
    iterations = [r.get('iterations', 0) for r in results]
    return statistics.mean(iterations)


def calculate_test_pass_rate(results: List[Dict]) -> float:
    """Calcula taxa de testes passados."""
    if not results:
        return 0.0
    
    passed = sum(
        1 for r in results
        if r.get('metrics', {}).get('tests_passed', False)
    )
    return passed / len(results)


def calculate_linter_pass_rate(results: List[Dict]) -> float:
    """Calcula taxa de linter passado."""
    if not results:
        return 0.0
    
    passed = sum(
        1 for r in results
        if r.get('metrics', {}).get('linter_passed', False)
    )
    return passed / len(results)


def calculate_verification_coverage(results: List[Dict]) -> Dict[str, float]:
    """Calcula cobertura de verificação."""
    if not results:
        return {}
    
    total_verifications = 0
    passed_verifications = 0
    
    for r in results:
        metrics = r.get('metrics', {})
        total_verifications += metrics.get('total_verifications', 0)
        passed_verifications += metrics.get('passed_verifications', 0)
    
    coverage = passed_verifications / total_verifications if total_verifications > 0 else 0.0
    
    return {
        'total': total_verifications,
        'passed': passed_verifications,
        'coverage': coverage
    }


def generate_summary(results: List[Dict]) -> Dict:
    """Gera resumo estatístico dos resultados."""
    return {
        'total_requirements': len(results),
        'pass_rate': calculate_pass_rate(results),
        'average_iterations': calculate_average_iterations(results),
        'test_pass_rate': calculate_test_pass_rate(results),
        'linter_pass_rate': calculate_linter_pass_rate(results),
        'verification_coverage': calculate_verification_coverage(results)
    }

