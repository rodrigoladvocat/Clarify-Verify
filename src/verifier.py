"""
Módulo de verificação automática.
Executa testes, análise estática e verificação formal quando aplicável.
"""

import subprocess
import os
import tempfile
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging


class VerificationStatus(Enum):
    """Status de verificação."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class VerificationResult:
    """Resultado de uma verificação."""
    status: VerificationStatus
    tool: str  # "tests", "linter", "formal"
    output: str
    errors: List[str]
    warnings: List[str]


class Verifier:
    """Executa verificações automáticas no código gerado."""
    
    def __init__(self, run_tests: bool = True, 
                 run_linter: bool = True,
                 run_formal: bool = False):
        """
        Inicializa o verificador.
        
        Args:
            run_tests: Se deve executar testes unitários
            run_linter: Se deve executar análise estática
            run_formal: Se deve executar verificação formal
        """
        self.run_tests = run_tests
        self.run_linter = run_linter
        self.run_formal = run_formal
        self.logger = logging.getLogger(__name__)
    
    def verify(self, code: str, tests: str, language: str = "python") -> List[VerificationResult]:
        """
        Executa todas as verificações configuradas.
        
        Args:
            code: Código a ser verificado
            tests: Código dos testes
            language: Linguagem de programação
            
        Returns:
            Lista de resultados de verificação
        """
        results = []
        
        if self.run_tests:
            self.logger.debug("Running tests")
            test_result = self._run_tests(code, tests, language)
            results.append(test_result)
        
        if self.run_linter:
            self.logger.debug("Running linter")
            linter_result = self._run_linter(code, language)
            results.append(linter_result)
        
        if self.run_formal:
            self.logger.debug("Running formal verification")
            formal_result = self._run_formal_verification(code, language)
            results.append(formal_result)
        
        return results
    
    def _run_tests(self, code: str, tests: str, language: str) -> VerificationResult:
        """Executa testes unitários."""
        if language == "python":
            return self._run_python_tests(code, tests)
        else:
            return VerificationResult(
                status=VerificationStatus.SKIPPED,
                tool="tests",
                output="Testes não suportados para esta linguagem",
                errors=[],
                warnings=[]
            )
    
    def _run_python_tests(self, code: str, tests: str) -> VerificationResult:
        """Executa testes Python usando pytest."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Salva código e testes em arquivos temporários
                code_file = os.path.join(tmpdir, "code.py")
                test_file = os.path.join(tmpdir, "test_code.py")
                
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(tests)
                
                try:
                    # Executa pytest
                    result = subprocess.run(
                        ['python', '-m', 'pytest', test_file, '-v', '--tb=short'],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=tmpdir
                    )
                    
                    self.logger.info("Pytest return: %d", result.returncode + result.stderr)
                    
                    if result.returncode == 0:
                        status = VerificationStatus.PASS
                        errors = []
                    else:
                        status = VerificationStatus.FAIL
                        errors = [result.stderr] if result.stderr else []
                        
                    verification_result = VerificationResult(
                        status=status,
                        tool="tests",
                        output=result.stdout + result.stderr,
                        errors=errors,
                        warnings=[]
                    )
                    self.logger.info("Test verification result: %s", verification_result)
                    return
                except subprocess.TimeoutExpired:
                    verification_result = VerificationResult(
                        status=VerificationStatus.ERROR,
                        tool="tests",
                        output="Timeout ao executar testes",
                        errors=["Timeout"],
                        warnings=[]
                    )
                    self.logger.info("Test verification result (timeout): %s", verification_result)
                    return
                except Exception as e:
                    self.logger.error("Error running tests: %s", str(e))
                    verification_result = VerificationResult(
                        status=VerificationStatus.ERROR,
                        tool="tests",
                        output=f"Erro ao executar testes: {str(e)}",
                        errors=[str(e)],
                        warnings=[]
                    )
                    self.logger.info("Test verification result (error): %s", verification_result)
                    return
        except Exception as e:
            logging.error("Erro ao criar diretório temporário para testes: %s", str(e))
            verification_result = VerificationResult(
                status=VerificationStatus.ERROR,
                tool="tests",
                output=f"Erro ao preparar ambiente de testes: {str(e)}",
                errors=[str(e)],
                warnings=[]
            )
        finally:
            if 'verification_result' in locals():
                return verification_result
            return VerificationResult(
                status=VerificationStatus.ERROR,
                tool="tests",
                output="Erro desconhecido ao executar testes",
                errors=[],
                warnings=[]
            )

    def _run_linter(self, code: str, language: str) -> VerificationResult:
        """Executa análise estática (linter)."""
        if language == "python":
            return self._run_pylint(code)
        else:
            return VerificationResult(
                status=VerificationStatus.SKIPPED,
                tool="linter",
                output="Linter não suportado para esta linguagem",
                errors=[],
                warnings=[]
            )
    
    def _run_pylint(self, code: str) -> VerificationResult:
        """Executa pylint no código Python."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['pylint', '--disable=all', '--enable=E,F', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Pylint retorna código 0 se não houver erros, mas pode ter warnings
            errors = []
            warnings = []
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if 'error' in line.lower() or 'E:' in line:
                        errors.append(line)
                    elif 'warning' in line.lower() or 'W:' in line:
                        warnings.append(line)
            
            status = VerificationStatus.PASS if not errors else VerificationStatus.FAIL
            
            return VerificationResult(
                status=status,
                tool="linter",
                output=result.stdout + result.stderr,
                errors=errors,
                warnings=warnings
            )
        except FileNotFoundError:
            # Pylint não instalado, tenta flake8
            return self._run_flake8(code)
        except Exception as e:
            return VerificationResult(
                status=VerificationStatus.ERROR,
                tool="linter",
                output=f"Erro ao executar linter: {str(e)}",
                errors=[str(e)],
                warnings=[]
            )
        finally:
            os.unlink(temp_file)
    
    def _run_flake8(self, code: str) -> VerificationResult:
        """Executa flake8 como fallback."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['flake8', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            errors = result.stdout.split('\n') if result.stdout else []
            status = VerificationStatus.PASS if result.returncode == 0 else VerificationStatus.FAIL
            
            return VerificationResult(
                status=status,
                tool="linter",
                output=result.stdout + result.stderr,
                errors=errors,
                warnings=[]
            )
        except FileNotFoundError:
            return VerificationResult(
                status=VerificationStatus.SKIPPED,
                tool="linter",
                output="Nenhum linter disponível (pylint ou flake8)",
                errors=[],
                warnings=[]
            )
        except Exception as e:
            return VerificationResult(
                status=VerificationStatus.ERROR,
                tool="linter",
                output=f"Erro ao executar linter: {str(e)}",
                errors=[str(e)],
                warnings=[]
            )
        finally:
            os.unlink(temp_file)
    
    def _run_formal_verification(self, code: str, language: str) -> VerificationResult:
        """
        Executa verificação formal quando aplicável.
        Por enquanto, apenas detecta se é aplicável e retorna status.
        """
        # Verificação formal requer tradução para formatos específicos
        # (TLA+, Alloy, SMT, etc.) - implementação futura
        
        return VerificationResult(
            status=VerificationStatus.SKIPPED,
            tool="formal",
            output="Verificação formal não implementada ainda",
            errors=[],
            warnings=["Verificação formal requer configuração adicional"]
        )
    
    def get_error_summary(self, results: List[VerificationResult]) -> str:
        """Gera um resumo de erros para feedback ao LLM."""
        errors = []
        for result in results:
            if result.status == VerificationStatus.FAIL:
                errors.append(f"[{result.tool}] {chr(10).join(result.errors[:3])}")
        
        summary = '\n\n'.join(errors) if errors else ""
        self.logger.debug("Error summary length=%d", len(summary))
        return summary

