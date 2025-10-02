"""
Web Scraper de Citações
Coleta citações, autores e tags de um site público e salva em CSV
Desenvolvido para prática de web scraping e análise de dados
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import os

class CitationScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.quotes_data = []
        self.session = requests.Session()
        # Headers para simular navegador real (evita bloqueios)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page_content(self, url):
        """
        Busca o conteúdo HTML da página
        Inclui tratamento de erros para requisições
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            return None
    
    def parse_quote_page(self, html_content):
        """
        Extrai informações de citações da página
        Retorna lista de dicionários com os dados
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        quotes = []
        
        # Encontra todos os containers de citações
        quote_divs = soup.find_all('div', class_='quote')
        
        for quote_div in quote_divs:
            try:
                # Extrai texto da citação
                text = quote_div.find('span', class_='text').get_text()
                
                # Remove as aspas do início e fim
                text = text.strip('"').strip('"')
                
                # Extrai autor
                author = quote_div.find('small', class_='author').get_text()
                
                # Extrai tags (algumas citações têm múltiplas)
                tags = [tag.get_text() for tag in quote_div.find_all('a', class_='tag')]
                
                # Calcula tamanho da citação (útil pra análise depois)
                word_count = len(text.split())
                
                quotes.append({
                    'texto': text,
                    'autor': author,
                    'tags': ', '.join(tags),
                    'num_tags': len(tags),
                    'num_palavras': word_count,
                    'data_coleta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
            except AttributeError as e:
                # Se algum elemento não for encontrado, pula essa citação
                print(f"Erro ao processar citação: {e}")
                continue
        
        return quotes
    
    def get_next_page_url(self, html_content):
        """
        Verifica se existe próxima página
        Retorna URL da próxima página ou None
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        next_button = soup.find('li', class_='next')
        
        if next_button:
            next_link = next_button.find('a')
            if next_link:
                return self.base_url + next_link['href']
        
        return None
    
    def scrape_all_pages(self, max_pages=5):
        """
        Percorre todas as páginas e coleta dados
        Limita quantidade de páginas pra não sobrecarregar
        """
        current_url = self.base_url + '/page/1/'
        pages_scraped = 0
        
        print("Iniciando coleta de dados...")
        print("-" * 50)
        
        while current_url and pages_scraped < max_pages:
            print(f"Coletando página {pages_scraped + 1}...")
            
            html_content = self.get_page_content(current_url)
            if not html_content:
                break
            
            # Extrai citações da página atual
            page_quotes = self.parse_quote_page(html_content)
            self.quotes_data.extend(page_quotes)
            
            print(f"  → {len(page_quotes)} citações coletadas")
            
            # Busca URL da próxima página
            current_url = self.get_next_page_url(html_content)
            pages_scraped += 1
            
            # Delay entre requisições (boas práticas de scraping)
            if current_url:
                time.sleep(1)
        
        print("-" * 50)
        print(f"Coleta finalizada! Total: {len(self.quotes_data)} citações")
        return self.quotes_data
    
    def save_to_csv(self, filename='citacoes_coletadas.csv'):
        """
        Salva dados coletados em arquivo CSV
        Cria diretório 'dados' se não existir
        """
        # Cria pasta pra organizar os dados
        os.makedirs('dados', exist_ok=True)
        filepath = os.path.join('dados', filename)
        
        if not self.quotes_data:
            print("Nenhum dado para salvar!")
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['texto', 'autor', 'tags', 'num_tags', 'num_palavras', 'data_coleta']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(self.quotes_data)
            
            print(f"\n✓ Dados salvos em: {filepath}")
            return filepath
            
        except IOError as e:
            print(f"Erro ao salvar arquivo: {e}")
            return None
    
    def get_statistics(self):
        """
        Retorna estatísticas básicas dos dados coletados
        Útil pra verificar se a coleta funcionou bem
        """
        if not self.quotes_data:
            return None
        
        total_quotes = len(self.quotes_data)
        unique_authors = len(set(q['autor'] for q in self.quotes_data))
        avg_words = sum(q['num_palavras'] for q in self.quotes_data) / total_quotes
        
        # Encontra autor com mais citações
        author_counts = {}
        for quote in self.quotes_data:
            author = quote['autor']
            author_counts[author] = author_counts.get(author, 0) + 1
        
        most_quoted = max(author_counts.items(), key=lambda x: x[1])
        
        return {
            'total_citacoes': total_quotes,
            'autores_unicos': unique_authors,
            'media_palavras': round(avg_words, 1),
            'autor_mais_citado': most_quoted[0],
            'num_citacoes_autor': most_quoted[1]
        }


def main():
    """
    Função principal - executa o scraper
    """
    print("=" * 50)
    print("WEB SCRAPER DE CITAÇÕES")
    print("=" * 50)
    print()
    
    # URL base do site (quotes.toscrape.com é site público pra prática)
    base_url = 'http://quotes.toscrape.com'
    
    # Inicializa o scraper
    scraper = CitationScraper(base_url)
    
    # Coleta dados (limita a 5 páginas pra não demorar muito)
    scraper.scrape_all_pages(max_pages=5)
    
    # Salva em CSV
    csv_path = scraper.save_to_csv()
    
    # Mostra estatísticas
    if csv_path:
        stats = scraper.get_statistics()
        if stats:
            print("\n" + "=" * 50)
            print("ESTATÍSTICAS DA COLETA")
            print("=" * 50)
            print(f"Total de citações coletadas: {stats['total_citacoes']}")
            print(f"Autores únicos: {stats['autores_unicos']}")
            print(f"Média de palavras por citação: {stats['media_palavras']}")
            print(f"Autor mais citado: {stats['autor_mais_citado']} ({stats['num_citacoes_autor']} citações)")
            print("=" * 50)


if __name__ == "__main__":
    main()
