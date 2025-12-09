"""
Módulo de geração de código a partir de requisitos refinados.
Gera código e testes unitários usando LLMs.
"""

from typing import Optional, Dict
from dataclasses import dataclass
import logging


@dataclass
class GeneratedCode:
    """Representa código gerado."""
    code: str
    tests: str
    language: str
    explanation: str


class CodeGenerator:
    """Gera código a partir de requisitos refinados."""
    
    def __init__(self, llm_client, language: str = "python"):
        """
        Inicializa o gerador de código.
        
        Args:
            llm_client: Cliente LLM
            language: Linguagem de programação (python, java, etc.)
        """
        self.llm_client = llm_client
        self.language = language
        self.logger = logging.getLogger(__name__)
    
    def generate(self, refined_requirement: str, 
                 uml_diagram: Optional[str] = None) -> GeneratedCode:
        """
        Gera código a partir do requisito refinado.
        
        Args:
            refined_requirement: Requisito refinado
            uml_diagram: Diagrama UML opcional para referência
            
        Returns:
            Código gerado com testes
        """
        uml_context = ""
        if uml_diagram:
            uml_context = f"""
            Diagrama UML de referência:
            ```plantuml
            {uml_diagram}
            ```
            """
        
        self.logger.info("Generating initial code and tests for language=%s", self.language)
        prompt = f"""Você é um desenvolvedor experiente. Implemente a(s) função(ões) necessárias conforme o requisito final abaixo. 

        Requisito final:
        \"\"\"{refined_requirement}\"\"\"
        {uml_context}

        Instruções:
        1. Inclua comentários explicativos no código
        2. Escreva testes unitários completos (usando pytest para Python ou unittest para outras linguagens)
        3. Evite usar bibliotecas externas exceto as padrão da linguagem
        4. Trate casos de borda e erros apropriadamente
        5. Siga boas práticas de programação
        6. Os blocos de código {self.language} devem ser disponibilizados em blocos diferentes, e não no mesmo bloco de código, para que o parsing seja feito corretamente.

        Formato de resposta:
        <início do formato da resposta>
        Primeiro bloco de código
        ```{self.language}
        [código da implementação aqui]
        ```

        Segundo bloco de código
        ```{self.language}
        # Testes unitários
        [código dos testes aqui]
        ```
        
        Terceira seção
        [Breve explicação do código]
        <fim do formato da resposta>

        Utilize o formato de resposta acima rigidamente.
        
        O código de implementação e o de testes devem estar em blocos ```{self.language}``` diferentes!!!
        """
        
        response = self.llm_client.generate(prompt)
        
        # Extrai código e testes
        code, tests, explanation = self._parse_response(response)
        
        return GeneratedCode(
            code=code,
            tests=tests,
            language=self.language,
            explanation=explanation
        )
    
    def _parse_response(self, response: str):
        """Extrai código, testes e explicação da resposta do LLM."""
        code = ""
        tests = ""
        explanation = ""
        
        lines = response.splitlines()

        # now get the lines between lines that contain ```
        in_code_block = False
        current_block = []
        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    # end of code block
                    block_content = "\n".join(current_block).strip()
                    if code == "":
                        code = block_content
                    else:
                        tests = block_content
                    current_block = []
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)
            else:
                explanation += line + "\n"

        return (code.strip(), tests.strip(), "")

    def repair_code(self, current_code: str, error_summary: str) -> str:
        """
        Corrige código com base em erros de verificação.
        
        Args:
            current_code: Código atual com erro
            error_summary: Resumo do erro encontrado
            
        Returns:
            Código corrigido
        """
        prompt = f"""O seguinte teste/verificação falhou: {error_summary}

        Mostre uma correção para o código abaixo explicando a causa e a mudança. Forneça apenas o código corrigido completo.

        Código atual:
        ```{self.language}
        {current_code}
        ```

        Código corrigido:"""
        
        self.logger.info("Repairing code based on error summary")
        response = self.llm_client.generate(prompt)
        
        # Extrai apenas o código corrigido
        code = self._extract_code_only(response)
        self.logger.info("Repaired code: %s", code)
        return code
    
    def _extract_code_only(self, response: str) -> str:
        """Extrai apenas o código da resposta, removendo explicações."""
        # Procura por blocos de código
        if '```' in response:
            start = response.find('```')
            if start >= 0:
                # Pula a linha do marcador
                start = response.find('\n', start) + 1
                end = response.find('```', start)
                if end >= 0:
                    return response[start:end].strip()
        
        return response.strip()

