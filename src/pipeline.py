"""
Pipeline principal: orquestra Clarify -> Generate -> Verify -> Feedback loop.
"""t

import json
import os
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from daetime import datetime

from .clarifier import Clarifier
from .uml_generator import UMLGenerator
from .code_generator import CodeGenerator
from .verifier import Verifier, VerificationResult
from .llm_client import LLMClient, OpenAIClient, MockLLMClient


@dataclass
class PipelineResult:
    """Resultado completo do pipeline."""
    requirement_id: str
    original_requirement: str
    refined_requirement: str
    clarification_questions: List[Dict]
    uml_diagrams: List[Dict]
    generated_code: str
    generated_tests: str
    verification_results: List[Dict]
    iterations: int
    final_status: str
    metrics: Dict


class Pipeline:
    """Pipeline principal do Clarify-Verify."""
    
    def __init__(self, llm_client: LLMClient, config: Dict):
        """
        Inicializa o pipeline.
        
        Args:
            llm_client: Cliente LLM
            config: Configuração do pipeline
        """
        self.llm_client = llm_client
        self.config = config
        
        # Inicializa componentes
        self.clarifier = Clarifier(
            llm_client=llm_client,
            max_questions=config.get('clarifier_max_questions', 7)
        )
        self.uml_generator = UMLGenerator(llm_client=llm_client)
        self.code_generator = CodeGenerator(
            llm_client=llm_client,
            language=config.get('language', 'python')
        )
        self.verifier = Verifier(
            run_tests=config.get('verify', {}).get('run_tests', True),
            run_linter=config.get('verify', {}).get('run_linter', True),
            run_formal=config.get('verify', {}).get('run_formal', False)
        )
        
        self.max_iterations = config.get('max_iterations', 3)
    
    def run(self, requirement: str, requirement_id: str = "req_001",
            simulate_answers: bool = True) -> PipelineResult:
        """
        Executa o pipeline completo para um requisito.
        
        Args:
            requirement: Requisito textual original
            requirement_id: ID único do requisito
            simulate_answers: Se True, simula respostas automaticamente
            
        Returns:
            Resultado completo do pipeline
        """
        original_requirement = requirement
        refined_requirement = requirement
        clarification_questions = []
        uml_diagrams = []
        iterations = 0
        
        # Etapa 1: Clarificação
        if self.config.get('use_clarification', True):
            is_ambiguous = self.clarifier.detect_ambiguity(requirement)
            
            if is_ambiguous:
                questions = self.clarifier.generate_questions(requirement)
                clarification_questions = [
                    {
                        'question': q.question,
                        'priority': q.priority,
                        'reason': q.reason
                    }
                    for q in questions
                ]
                
                # Simula ou obtém respostas
                if simulate_answers:
                    answers = self._simulate_answers(questions, requirement)
                else:
                    answers = self._get_user_answers(questions)
                
                refined_requirement = self.clarifier.refine_requirement(
                    requirement, questions, answers
                )
        
        # Etapa 2: Geração UML
        uml_diagram = None
        if self.config.get('generate_uml', True):
            try:
                uml_diagram = self.uml_generator.generate_sequence_diagram(refined_requirement)
                uml_diagrams.append({
                    'type': uml_diagram.diagram_type,
                    'plantuml_code': uml_diagram.plantuml_code,
                    'description': uml_diagram.description
                })
            except Exception as e:
                print(f"Erro ao gerar UML: {e}")
        
        # Etapa 3: Geração de código e verificação (loop)
        current_code = ""
        current_tests = ""
        verification_results = []
        final_status = "unknown"
        
        for iteration in range(self.max_iterations):
            iterations = iteration + 1
            
            # Gera código
            try:
                generated = self.code_generator.generate(
                    refined_requirement,
                    uml_diagram.plantuml_code if uml_diagram else None
                )
                current_code = generated.code
                current_tests = generated.tests
            except Exception as e:
                print(f"Erro ao gerar código: {e}")
                break
            
            # Verifica código
            results = self.verifier.verify(
                current_code,
                current_tests,
                language=self.config.get('language', 'python')
            )
            
            verification_results.append({
                'iteration': iteration + 1,
                'results': [
                    {
                        'tool': r.tool,
                        'status': r.status.value,
                        'output': r.output,
                        'errors': r.errors,
                        'warnings': r.warnings
                    }
                    for r in results
                ]
            })
            
            # Verifica se passou em todas as verificações
            all_passed = all(r.status.value == 'pass' for r in results)
            if all_passed:
                final_status = "success"
                break
            
            # Se não passou e ainda há iterações, tenta corrigir
            if iteration < self.max_iterations - 1:
                error_summary = self.verifier.get_error_summary(results)
                try:
                    current_code = self.code_generator.repair_code(
                        current_code,
                        error_summary
                    )
                except Exception as e:
                    print(f"Erro ao corrigir código: {e}")
                    break
            else:
                final_status = "failed"
        
        # Calcula métricas
        metrics = self._calculate_metrics(verification_results, iterations)
        
        return PipelineResult(
            requirement_id=requirement_id,
            original_requirement=original_requirement,
            refined_requirement=refined_requirement,
            clarification_questions=clarification_questions,
            uml_diagrams=uml_diagrams,
            generated_code=current_code,
            generated_tests=current_tests,
            verification_results=verification_results,
            iterations=iterations,
            final_status=final_status,
            metrics=metrics
        )
    
    def _simulate_answers(self, questions, requirement: str) -> Dict[str, str]:
        """Simula respostas às perguntas de clarificação."""
        answers = {}
        
        for q in questions:
            # Gera resposta simulada usando LLM
            prompt = f"""Com base no requisito abaixo, forneça uma resposta curta e direta para a seguinte pergunta de clarificação.

Requisito original:
\"\"\"{requirement}\"\"\"

Pergunta: {q.question}

Responda de forma concisa (1-2 frases):"""
            
            answer = self.llm_client.generate(prompt)
            answers[q.question] = answer.strip()
        
        return answers
    
    def _get_user_answers(self, questions) -> Dict[str, str]:
        """Obtém respostas do usuário (interativo)."""
        answers = {}
        print("\n=== Perguntas de Clarificação ===")
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. [{q.priority}] {q.question}")
            print(f"   Motivo: {q.reason}")
            answer = input("Resposta: ")
            answers[q.question] = answer
        return answers
    
    def _calculate_metrics(self, verification_results: List[Dict], iterations: int) -> Dict:
        """Calcula métricas do pipeline."""
        if not verification_results:
            return {}
        
        last_iteration = verification_results[-1]
        results = last_iteration['results']
        
        tests_passed = any(
            r['tool'] == 'tests' and r['status'] == 'pass'
            for r in results
        )
        linter_passed = any(
            r['tool'] == 'linter' and r['status'] == 'pass'
            for r in results
        )
        
        return {
            'iterations': iterations,
            'tests_passed': tests_passed,
            'linter_passed': linter_passed,
            'total_verifications': len(results),
            'passed_verifications': sum(
                1 for r in results if r['status'] == 'pass'
            )
        }


def load_config(config_path: str) -> Dict:
    """Carrega configuração de arquivo YAML."""
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback para JSON
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar config: {e}")
        return {}


def main():
    """Função principal para execução via CLI."""
    parser = argparse.ArgumentParser(description='Clarify-Verify Pipeline')
    parser.add_argument('--config', type=str, required=True,
                       help='Caminho para arquivo de configuração')
    parser.add_argument('--outdir', type=str, required=True,
                       help='Diretório de saída para resultados')
    parser.add_argument('--requirement', type=str,
                       help='Requisito único para processar')
    parser.add_argument('--dataset', type=str,
                       help='Caminho para dataset JSON com múltiplos requisitos')
    
    args = parser.parse_args()
    
    # Carrega configuração
    config = load_config(args.config)
    
    # Inicializa cliente LLM
    model_config = config.get('model', {})
    provider = model_config.get('provider', 'openai')
    
    if provider == 'openai':
        llm_client = OpenAIClient(
            model=model_config.get('name', 'gpt-4o-mini'),
            api_key=os.getenv('OPENAI_API_KEY')
        )
    else:
        # Fallback para mock em desenvolvimento
        print("Usando MockLLMClient (configure OPENAI_API_KEY para usar API real)")
        llm_client = MockLLMClient()
    
    # Cria pipeline
    pipeline = Pipeline(llm_client, config)
    
    # Cria diretório de saída
    os.makedirs(args.outdir, exist_ok=True)
    
    # Processa requisito(s)
    if args.requirement:
        # Processa requisito único
        result = pipeline.run(args.requirement, requirement_id="req_001")
        
        # Salva resultado
        output_file = os.path.join(args.outdir, f"result_{result.requirement_id}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False)
        
        print(f"Resultado salvo em: {output_file}")
    
    elif args.dataset:
        # Processa dataset
        with open(args.dataset, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        results = []
        for item in dataset:
            req_id = item.get('id', f"req_{len(results)+1:03d}")
            requirement = item.get('requirement', item.get('text', ''))
            
            print(f"\nProcessando {req_id}...")
            result = pipeline.run(requirement, requirement_id=req_id)
            results.append(asdict(result))
        
        # Salva todos os resultados
        output_file = os.path.join(args.outdir, "results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{len(results)} resultados salvos em: {output_file}")
    
    else:
        parser.error("Forneça --requirement ou --dataset")


if __name__ == '__main__':
    main()

