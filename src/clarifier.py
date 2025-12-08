"""
Módulo de clarificação de requisitos.
Gera perguntas de esclarecimento para requisitos ambíguos usando LLMs.
"""

import json
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass


@dataclass
class ClarificationQuestion:
    """Representa uma pergunta de clarificação."""
    question: str
    priority: str  # "Obrigatória" ou "Desejável"
    reason: str


class Clarifier:
    """Gera e processa perguntas de clarificação de requisitos."""
    
    def __init__(self, llm_client, max_questions: int = 7):
        """
        Inicializa o clarificador.
        
        Args:
            llm_client: Cliente LLM (OpenAI, Anthropic, etc.)
            max_questions: Número máximo de perguntas a gerar
        """
        self.llm_client = llm_client
        self.max_questions = max_questions
        self.logger = logging.getLogger(__name__)
    
    def detect_ambiguity(self, requirement: str) -> bool:
        """
        Detecta se um requisito é ambíguo através de verificação de consistência.
        
        Args:
            requirement: Requisito textual a ser analisado
            
        Returns:
            True se o requisito for considerado ambíguo
        """
        prompt = f"""Analise o seguinte requisito e determine se ele é ambíguo ou insuficiente para gerar código.

        Um requisito é ambíguo se:
        - Faltam detalhes técnicos essenciais (tipos de dados, formatos, comportamentos)
        - Há múltiplas interpretações possíveis
        - Não especifica casos de borda ou tratamento de erros

        Requisito:
        \"\"\"{requirement}\"\"\"

        Responda apenas com "SIM" ou "NÃO"."""
        
        self.logger.debug("Detecting ambiguity for requirement")
        response = self.llm_client.generate(prompt)
        return "SIM" in response.upper()
    
    # Generate clarification questions
    def generate_questions(self, requirement: str) -> List[ClarificationQuestion]:
        """
        Gera perguntas de clarificação para um requisito.
        
        Args:
            requirement: Requisito textual
            
        Returns:
            Lista de perguntas de clarificação
        """
        prompt = f"""Você é um analista de requisitos. Receba o requisito abaixo e gere até {self.max_questions} perguntas de esclarecimento necessárias para que um desenvolvedor gere um código correto e não ambíguo. 

        Classifique cada pergunta como [Obrigatória|Desejável]. Dê também um motivo curto para cada pergunta.

        Requisito:
        \"\"\"{requirement}\"\"\"

        Formato de resposta (JSON):
        {{
            "questions": [
                {{
                    "question": "texto da pergunta",
                    "priority": "Obrigatória ou Desejável",
                    "reason": "motivo breve"
                }}
            ]
        }}"""
        
        self.logger.debug("Generating clarification questions (max=%d)", self.max_questions)
        response = self.llm_client.generate(prompt)
        
        # Tenta extrair JSON da resposta
        questions = self._parse_response(response)
        return questions
    
    # Parse response into a list of ClarificationQuestion objects
    def _parse_response(self, response: str) -> List[ClarificationQuestion]:
        """Extrai perguntas do JSON retornado pelo LLM."""
        questions = []
        
        # Tenta encontrar JSON na resposta
        try:
            # Procura por blocos JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                for q_data in data.get('questions', []):
                    questions.append(ClarificationQuestion(
                        question=q_data.get('question', ''),
                        priority=q_data.get('priority', 'Desejável'),
                        reason=q_data.get('reason', '')
                    ))
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: parsing simples por linhas
            lines = response.split('\n')
            current_question = None
            for line in lines:
                line = line.strip()
                if line.startswith('Pergunta') or line.startswith('Q:'):
                    if current_question:
                        questions.append(current_question)
                    current_question = ClarificationQuestion(
                        question=line,
                        priority='Desejável',
                        reason=''
                    )
                elif line.startswith('Prioridade'):
                    if current_question:
                        current_question.priority = line.split(':')[-1].strip()
                elif line.startswith('Motivo'):
                    if current_question:
                        current_question.reason = line.split(':')[-1].strip()
            
            if current_question:
                questions.append(current_question)
        
        return questions[:self.max_questions]
    
    # Refine requirements after clarification
    def refine_requirement(self, original_requirement: str, 
                          questions: List[ClarificationQuestion],
                          answers: Dict[str, str]) -> str:
        """
        Refina o requisito original com base nas respostas às perguntas.
        
        Args:
            original_requirement: Requisito original
            questions: Lista de perguntas geradas
            answers: Dicionário mapeando perguntas para respostas
            
        Returns:
            Requisito refinado
        """
        qa_pairs = []
        for q in questions:
            if q.question in answers:
                qa_pairs.append(f"Q: {q.question}\nA: {answers[q.question]}")
        
        prompt = f"""Com base no requisito original e nas respostas às perguntas de clarificação, gere um requisito refinado, completo e não ambíguo.

        Requisito original:
        \"\"\"{original_requirement}\"\"\"

        Perguntas e respostas:
        \"\"\"
        {chr(10).join(qa_pairs)}
        \"\"\"

        Requisito refinado:"""
        
        self.logger.debug("Refining requirement using Q/A pairs")
        response = self.llm_client.generate(prompt)
        return response.strip()

