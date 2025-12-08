"""
Script CLI para análise de resultados.
"""

import argparse
import sys
from .analysis import analyze_results, print_analysis


def main():
    parser = argparse.ArgumentParser(description='Analisa resultados do Clarify-Verify')
    parser.add_argument('results_file', type=str,
                       help='Arquivo JSON com resultados')
    parser.add_argument('--output', type=str,
                       help='Arquivo de saída para análise (opcional)')
    
    args = parser.parse_args()
    
    try:
        analysis = analyze_results(args.results_file)
        print_analysis(analysis)
        
        if args.output:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"\nAnálise salva em: {args.output}")
    
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

