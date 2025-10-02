"""
Analisador de Dados das Citações Coletadas
Gera gráficos e relatórios a partir dos dados do CSV
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

class QuotesAnalyzer:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """
        Carrega dados do CSV em um DataFrame pandas
        """
        try:
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            print(f"✓ Dados carregados: {len(self.df)} registros")
            return True
        except FileNotFoundError:
            print(f"Erro: Arquivo {self.csv_path} não encontrado!")
            print("Execute primeiro o scraper.py para coletar os dados.")
            return False
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def generate_author_chart(self):
        """
        Gera gráfico de autores mais citados
        """
        if self.df is None:
            return
        
        # Conta citações por autor
        author_counts = self.df['autor'].value_counts().head(10)
        
        plt.figure(figsize=(12, 6))
        colors = plt.cm.viridis(range(len(author_counts)))
        
        bars = plt.barh(author_counts.index, author_counts.values, color=colors)
        
        plt.xlabel('Número de Citações', fontsize=12, fontweight='bold')
        plt.ylabel('Autor', fontsize=12, fontweight='bold')
        plt.title('Top 10 Autores Mais Citados', fontsize=14, fontweight='bold', pad=20)
        plt.gca().invert_yaxis()
        
        # Adiciona valores nas barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2, 
                    f' {int(width)}', 
                    ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        
        # Salva gráfico
        os.makedirs('graficos', exist_ok=True)
        plt.savefig('graficos/autores_mais_citados.png', dpi=300, bbox_inches='tight')
        print("✓ Gráfico salvo: graficos/autores_mais_citados.png")
        plt.close()
    
    def generate_words_distribution(self):
        """
        Gera gráfico de distribuição de tamanho das citações
        """
        if self.df is None:
            return
        
        plt.figure(figsize=(10, 6))
        
        # Histogram com densidade
        plt.hist(self.df['num_palavras'], bins=20, color='#3498db', 
                edgecolor='black', alpha=0.7)
        
        # Linha de média
        mean_words = self.df['num_palavras'].mean()
        plt.axvline(mean_words, color='red', linestyle='--', linewidth=2, 
                   label=f'Média: {mean_words:.1f} palavras')
        
        plt.xlabel('Número de Palavras', fontsize=12, fontweight='bold')
        plt.ylabel('Frequência', fontsize=12, fontweight='bold')
        plt.title('Distribuição do Tamanho das Citações', fontsize=14, fontweight='bold', pad=20)
        plt.legend(fontsize=11)
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('graficos/distribuicao_palavras.png', dpi=300, bbox_inches='tight')
        print("✓ Gráfico salvo: graficos/distribuicao_palavras.png")
        plt.close()
    
    def generate_tags_cloud(self):
        """
        Gera gráfico das tags mais populares
        """
        if self.df is None:
            return
        
        # Separa todas as tags (estão em formato "tag1, tag2, tag3")
        all_tags = []
        for tags_str in self.df['tags']:
            if pd.notna(tags_str):
                tags_list = [tag.strip() for tag in tags_str.split(',')]
                all_tags.extend(tags_list)
        
        # Conta frequência das tags
        tag_counts = Counter(all_tags)
        top_tags = dict(tag_counts.most_common(15))
        
        plt.figure(figsize=(12, 6))
        colors = plt.cm.Set3(range(len(top_tags)))
        
        bars = plt.bar(top_tags.keys(), top_tags.values(), color=colors, edgecolor='black', linewidth=1.2)
        
        plt.xlabel('Tags', fontsize=12, fontweight='bold')
        plt.ylabel('Frequência', fontsize=12, fontweight='bold')
        plt.title('Top 15 Tags Mais Usadas', fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Adiciona valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        plt.savefig('graficos/tags_populares.png', dpi=300, bbox_inches='tight')
        print("✓ Gráfico salvo: graficos/tags_populares.png")
        plt.close()
    
    def generate_summary_report(self):
        """
        Gera relatório textual com resumo da análise
        """
        if self.df is None:
            return
        
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE ANÁLISE - CITAÇÕES COLETADAS")
        report.append("=" * 60)
        report.append("")
        
        # Informações gerais
        report.append("📊 INFORMAÇÕES GERAIS")
        report.append("-" * 60)
        report.append(f"Total de citações analisadas: {len(self.df)}")
        report.append(f"Autores únicos: {self.df['autor'].nunique()}")
        report.append(f"Tags únicas identificadas: {len(set(','.join(self.df['tags']).split(', ')))}")
        report.append("")
        
        # Estatísticas de palavras
        report.append("📝 ANÁLISE DE TAMANHO")
        report.append("-" * 60)
        report.append(f"Média de palavras por citação: {self.df['num_palavras'].mean():.1f}")
        report.append(f"Citação mais curta: {self.df['num_palavras'].min()} palavras")
        report.append(f"Citação mais longa: {self.df['num_palavras'].max()} palavras")
        report.append(f"Mediana: {self.df['num_palavras'].median():.1f} palavras")
        report.append("")
        
        # Top autores
        report.append("👤 TOP 5 AUTORES")
        report.append("-" * 60)
        top_authors = self.df['autor'].value_counts().head(5)
        for i, (author, count) in enumerate(top_authors.items(), 1):
            report.append(f"{i}. {author}: {count} citações")
        report.append("")
        
        # Top tags
        all_tags = []
        for tags_str in self.df['tags']:
            if pd.notna(tags_str):
                all_tags.extend([tag.strip() for tag in tags_str.split(',')])
        
        tag_counts = Counter(all_tags)
        report.append("🏷️  TOP 5 TAGS")
        report.append("-" * 60)
        for i, (tag, count) in enumerate(tag_counts.most_common(5), 1):
            report.append(f"{i}. {tag}: {count} ocorrências")
        report.append("")
        
        # Citação exemplo (a mais longa)
        longest_quote = self.df.loc[self.df['num_palavras'].idxmax()]
        report.append("💬 EXEMPLO - CITAÇÃO MAIS LONGA")
        report.append("-" * 60)
        report.append(f"Autor: {longest_quote['autor']}")
        report.append(f"Palavras: {longest_quote['num_palavras']}")
        report.append(f"Texto: \"{longest_quote['texto'][:150]}...\"")
        report.append("")
        
        report.append("=" * 60)
        report.append("Relatório gerado com sucesso!")
        report.append("=" * 60)
        
        # Salva relatório
        report_text = "\n".join(report)
        with open('relatorio_analise.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print("\n" + report_text)
        print("\n✓ Relatório salvo em: relatorio_analise.txt")
    
    def run_full_analysis(self):
        """
        Executa análise completa: gráficos + relatório
        """
        if self.df is None:
            return
        
        print("\nIniciando análise de dados...")
        print("-" * 60)
        
        self.generate_author_chart()
        self.generate_words_distribution()
        self.generate_tags_cloud()
        self.generate_summary_report()
        
        print("-" * 60)
        print("\n✅ Análise completa finalizada!")
        print("Verifique a pasta 'graficos' para visualizar os resultados.")


def main():
    """
    Função principal do analisador
    """
    print("=" * 60)
    print("ANALISADOR DE DADOS - CITAÇÕES")
    print("=" * 60)
    print()
    
    # Caminho do CSV gerado pelo scraper
    csv_path = 'dados/citacoes_coletadas.csv'
    
    # Verifica se arquivo existe
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo {csv_path} não encontrado!")
        print("\nPrimeiro execute: python scraper.py")
        return
    
    # Inicializa analisador
    analyzer = QuotesAnalyzer(csv_path)
    
    # Executa análise completa
    if analyzer.df is not None:
        analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
