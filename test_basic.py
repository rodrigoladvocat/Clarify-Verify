#!/usr/bin/env python3
"""
Teste básico para validar a implementação.
"""

import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm_client import MockLLMClient
from src.clarifier import Clarifier
from src.uml_generator import UMLGenerator
from src.code_generator import CodeGenerator
from src.verifier import Verifier


def test_clarifier():
    """Testa o módulo de clarificação."""
    print("Testando Clarifier...")
    client = MockLLMClient()
    clarifier = Clarifier(client, max_questions=3)
    
    requirement = "Sort a list"
    questions = clarifier.generate_questions(requirement)
    
    assert len(questions) > 0, "Deveria gerar pelo menos uma pergunta"
    print(f"  ✓ Gerou {len(questions)} pergunta(s)")
    
    refined = clarifier.refine_requirement(
        requirement,
        questions,
        {q.question: "ascending order" for q in questions}
    )
    
    assert len(refined) > 0, "Deveria gerar requisito refinado"
    print(f"  ✓ Refinou requisito ({len(refined)} caracteres)")
    return True


def test_uml_generator():
    """Testa o gerador UML."""
    print("Testando UMLGenerator...")
    client = MockLLMClient()
    generator = UMLGenerator(client)
    
    requirement = "User logs in and views dashboard"
    diagram = generator.generate_sequence_diagram(requirement)
    
    assert diagram.diagram_type == "sequence"
    assert "@startuml" in diagram.plantuml_code or len(diagram.plantuml_code) > 0
    print(f"  ✓ Gerou diagrama de sequência ({len(diagram.plantuml_code)} caracteres)")
    return True


def test_code_generator():
    """Testa o gerador de código."""
    print("Testando CodeGenerator...")
    client = MockLLMClient()
    generator = CodeGenerator(client, language="python")
    
    requirement = "Calculate factorial of n"
    generated = generator.generate(requirement)
    
    assert len(generated.code) > 0, "Deveria gerar código"
    print(f"  ✓ Gerou código ({len(generated.code)} caracteres)")
    print(f"  ✓ Gerou testes ({len(generated.tests)} caracteres)")
    return True


def test_verifier():
    """Testa o verificador."""
    print("Testando Verifier...")
    verifier = Verifier(run_tests=True, run_linter=False, run_formal=False)
    
    code = """
def add(a, b):
    return a + b
"""
    
    tests = """
def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
"""
    
    results = verifier.verify(code, tests, language="python")
    
    assert len(results) > 0, "Deveria executar verificações"
    print(f"  ✓ Executou {len(results)} verificação(ões)")
    return True


def main():
    """Executa todos os testes."""
    print("="*60)
    print("TESTES BÁSICOS - Clarify-Verify")
    print("="*60)
    print()
    
    tests = [
        test_clarifier,
        test_uml_generator,
        test_code_generator,
        test_verifier
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ Falhou: {e}")
            failed += 1
        print()
    
    print("="*60)
    print(f"Resultado: {passed} passou, {failed} falhou")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

