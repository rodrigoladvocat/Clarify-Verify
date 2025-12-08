"""
Módulo de geração de diagramas UML a partir de requisitos refinados.
Gera especificações UML em PlantUML.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class UMLDiagram:
    """Representa um diagrama UML."""
    diagram_type: str  # "sequence", "class", "component", etc.
    plantuml_code: str
    description: str


class UMLGenerator:
    """Gera diagramas UML a partir de requisitos refinados."""
    
    def __init__(self, llm_client):
        """
        Inicializa o gerador UML.
        
        Args:
            llm_client: Cliente LLM
        """
        self.llm_client = llm_client
    
    def generate_sequence_diagram(self, refined_requirement: str) -> UMLDiagram:
        """
        Gera um diagrama de sequência a partir do requisito refinado.
        
        Args:
            refined_requirement: Requisito refinado após clarificação
            
        Returns:
            Diagrama UML de sequência
        """
        prompt = f"""Com base no requisito final (após respostas às perguntas), gere uma especificação em PlantUML de um diagrama de sequência que represente:
- A sequência principal do fluxo de eventos
- Os principais atores/componentes envolvidos
- As mensagens trocadas entre os componentes
- Adicione anotações breves sobre invariantes e pré-condições quando relevante

Requisito final:
\"\"\"{refined_requirement}\"\"\"

Formato de resposta:
```plantuml
@startuml
[seu código PlantUML aqui]
@enduml
```

Inclua também uma breve descrição do diagrama após o código."""
        
        response = self.llm_client.generate(prompt)
        
        # Extrai código PlantUML
        plantuml_code = self._extract_plantuml(response)
        description = self._extract_description(response)
        
        return UMLDiagram(
            diagram_type="sequence",
            plantuml_code=plantuml_code,
            description=description
        )
    
    def generate_class_diagram(self, refined_requirement: str) -> Optional[UMLDiagram]:
        """
        Gera um diagrama de classes quando aplicável.
        
        Args:
            refined_requirement: Requisito refinado
            
        Returns:
            Diagrama UML de classes ou None se não aplicável
        """
        prompt = f"""Com base no requisito final, gere uma especificação em PlantUML de um diagrama de classes se o requisito envolver múltiplas entidades ou classes.

Requisito final:
\"\"\"{refined_requirement}\"\"\"

Se o requisito não envolver múltiplas classes, responda apenas "NÃO APLICÁVEL".

Formato de resposta (se aplicável):
```plantuml
@startuml
[seu código PlantUML aqui]
@enduml
```"""
        
        response = self.llm_client.generate(prompt)
        
        if "NÃO APLICÁVEL" in response.upper() or "NOT APPLICABLE" in response.upper():
            return None
        
        plantuml_code = self._extract_plantuml(response)
        description = self._extract_description(response)
        
        return UMLDiagram(
            diagram_type="class",
            plantuml_code=plantuml_code,
            description=description
        )
    
    def _extract_plantuml(self, response: str) -> str:
        """Extrai código PlantUML da resposta do LLM."""
        # Procura por blocos de código PlantUML
        start_markers = ['@startuml', '```plantuml', '```']
        end_markers = ['@enduml', '```']
        
        start_idx = -1
        for marker in start_markers:
            idx = response.find(marker)
            if idx >= 0:
                start_idx = idx + len(marker)
                break
        
        if start_idx < 0:
            return response  # Retorna tudo se não encontrar marcadores
        
        # Remove o marcador de início se for ```
        if response[start_idx:start_idx+1] == '\n':
            start_idx += 1
        
        # Procura pelo fim
        end_idx = len(response)
        for marker in end_markers:
            idx = response.find(marker, start_idx)
            if idx >= 0:
                end_idx = idx
                break
        
        return response[start_idx:end_idx].strip()
    
    def _extract_description(self, response: str) -> str:
        """Extrai descrição do diagrama da resposta."""
        # Procura por texto após o código PlantUML
        end_markers = ['@enduml', '```']
        
        end_idx = len(response)
        for marker in end_markers:
            idx = response.find(marker)
            if idx >= 0:
                end_idx = idx + len(marker)
                break
        
        description = response[end_idx:].strip()
        # Remove marcadores de código restantes
        description = description.replace('```', '').strip()
        
        return description if description else "Diagrama gerado automaticamente."
    
    def save_uml(self, diagram: UMLDiagram, output_path: str):
        """
        Salva o diagrama UML em um arquivo.
        
        Args:
            diagram: Diagrama UML a ser salvo
            output_path: Caminho do arquivo de saída
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(diagram.plantuml_code)
        
        # Também salva a descrição em um arquivo separado
        desc_path = output_path.replace('.puml', '_desc.txt')
        with open(desc_path, 'w', encoding='utf-8') as f:
            f.write(f"Tipo: {diagram.diagram_type}\n\n")
            f.write(diagram.description)

