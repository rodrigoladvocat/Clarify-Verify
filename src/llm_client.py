"""
Cliente LLM abstrato para diferentes provedores (OpenAI, Anthropic, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional
import os


class LLMClient(ABC):
    """Interface abstrata para clientes LLM."""
    
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Gera uma resposta do LLM para o prompt dado.
        
        Args:
            prompt: Prompt de entrada
            temperature: Temperatura para geração (0.0 = determinístico)
            
        Returns:
            Resposta do LLM
        """
        pass


class OpenAIClient(LLMClient):
    """Cliente para OpenAI API."""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        Inicializa cliente OpenAI.
        
        Args:
            model: Nome do modelo (gpt-4, gpt-4o-mini, etc.)
            api_key: Chave da API (ou usa OPENAI_API_KEY do ambiente)
        """
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        except ImportError:
            raise ImportError("Instale openai: pip install openai")
        
        self.model = model
    
    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Gera resposta usando OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Erro ao chamar OpenAI API: {str(e)}")

# Disposabke function
class MockLLMClient(LLMClient):
    """Cliente mock para testes sem API real."""
    
    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Retorna resposta mock baseada no prompt."""
        if "clarificação" in prompt.lower() or "pergunta" in prompt.lower():
            return """{
                "questions": [
                    {
                        "question": "Qual o tipo de dados esperado?",
                        "priority": "Obrigatória",
                        "reason": "Necessário para implementação correta"
                    }
                ]
            }"""
        elif "uml" in prompt.lower() or "diagrama" in prompt.lower():
            return """```plantuml
            @startuml
            User -> System : request
            System -> Database : query
            Database --> System : result
            System --> User : response
            @enduml
            ```

            Diagrama de sequência básico."""
        elif "código" in prompt.lower() or "implemente" in prompt.lower():
            return """```python
            def function():
                pass
            ```

            ```python
            def test_function():
                assert function() is None
            ```

            Implementação básica."""
        else:
            return "Resposta mock do LLM"

