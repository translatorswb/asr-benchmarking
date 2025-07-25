#!/usr/bin/env python3
"""
Simple script to get ASR models for African languages using HuggingFace API
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import Dict, List

# Target languages with their HF language codes
LANGUAGES = {
    'Zulu': ['zu', 'zul'],
    'Luo': ['luo'],
    'Kikuyu': ['ki', 'kik'],
    'Yoruba': ['yo', 'yor'],
    'Igbo': ['ig', 'ibo'],
    'Hausa': ['ha', 'hau'],
    'Amharic': ['am', 'amh'],
    'Tigrinya': ['ti', 'tir'],
    'Sidoma': ['sid'],
    'Oromo': ['om'],
    'Wolaytta': ['wal'],
    
}

class HuggingFaceASRScraper:
    def __init__(self):
        self.base_url = "https://huggingface.co/models"
        self.api_base = "https://huggingface.co/api/models"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.model_cache = {}  # Cache for model stats
        
    def get_model_names_for_language(self, language_code: str, max_pages: int = 3) -> List[str]:
        """Get model names for a specific language code"""
        model_names = []
        
        for page in range(max_pages):
            url = f"{self.base_url}?pipeline_tag=automatic-speech-recognition&language={language_code}&sort=trending"
            if page > 0:
                url += f"&p={page}"
                
            try:
                print(f"Fetching page {page+1} for language: {language_code}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_models = self.parse_model_names_from_page(soup)
                
                if not page_models:
                    break
                    
                model_names.extend(page_models)
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                break
                
        return model_names
    
    def parse_model_names_from_page(self, soup: BeautifulSoup) -> List[str]:
        """Parse model names from search results page"""
        model_names = []
        
        # Find all model cards
        model_cards = soup.find_all('article', class_='overview-card-wrapper')
        
        for card in model_cards:
            try:
                link = card.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    model_name = href.lstrip('/')
                    if model_name and model_name != '#':
                        model_names.append(model_name)
            except Exception:
                continue
                
        return model_names
    
    def get_model_stats(self, model_name: str) -> Dict:
        """Get download and like counts for a model using HF API (with caching)"""
        
        # Check cache first
        if model_name in self.model_cache:
            print(f"Using cached stats for: {model_name}")
            return self.model_cache[model_name]
        
        try:
            print(f"Getting stats for: {model_name}")
            
            # Get downloads
            downloads_url = f"{self.api_base}/{model_name}?expand[]=downloads&expand[]=downloadsAllTime"
            downloads_response = self.session.get(downloads_url, timeout=10)
            downloads_data = downloads_response.json() if downloads_response.status_code == 200 else {}
            
            time.sleep(0.1)  # Brief pause between API calls
            
            # Get likes
            likes_url = f"{self.api_base}/{model_name}?expand[]=likes"
            likes_response = self.session.get(likes_url, timeout=10)
            likes_data = likes_response.json() if likes_response.status_code == 200 else {}
            
            downloads = downloads_data.get('downloads', 0)
            downloads_all_time = downloads_data.get('downloadsAllTime', 0)
            likes = likes_data.get('likes', 0)
            
            model_stats = {
                'name': model_name,
                'url': f"https://huggingface.co/{model_name}",
                'downloads': downloads,
                'downloads_all_time': downloads_all_time,
                'likes': likes
            }
            
            # Cache the result
            self.model_cache[model_name] = model_stats
            return model_stats
            
        except Exception as e:
            print(f"Error getting stats for {model_name}: {e}")
            model_stats = {
                'name': model_name,
                'url': f"https://huggingface.co/{model_name}",
                'downloads': 0,
                'downloads_all_time': 0,
                'likes': 0
            }
            # Cache even failed results to avoid retrying
            self.model_cache[model_name] = model_stats
            return model_stats
    
    def scrape_all_languages(self) -> Dict[str, List[Dict]]:
        """Get models for all target languages"""
        results = {}
        
        # First, collect all unique model names across all languages
        print("=== Collecting all model names ===")
        all_unique_models = set()
        
        for language_name, codes in LANGUAGES.items():
            print(f"Searching for {language_name} models...")
            for code in codes:
                model_names = self.get_model_names_for_language(code, max_pages=2)
                all_unique_models.update(model_names)
        
        print(f"Found {len(all_unique_models)} unique models total")
        
        # Get stats for all unique models once
        print("\n=== Getting model stats ===")
        for model_name in all_unique_models:
            self.get_model_stats(model_name)
            time.sleep(0.2)
        
        # Now organize by language using cached data
        print("\n=== Organizing by language ===")
        for language_name, codes in LANGUAGES.items():
            print(f"Processing {language_name}...")
            
            language_models = set()
            for code in codes:
                model_names = self.get_model_names_for_language(code, max_pages=2)
                language_models.update(model_names)
            
            # Get cached stats for this language's models
            models = []
            for model_name in language_models:
                model_stats = self.model_cache[model_name]  # Already cached
                models.append(model_stats)
            
            results[language_name] = models
            print(f"Found {len(models)} models for {language_name}")
            
        return results
    
    def create_language_matrix(self, results: Dict[str, List[Dict]]) -> pd.DataFrame:
        """Create matrix showing which models support which languages"""
        
        # Build model database
        all_models = {}
        
        for language, models in results.items():
            for model in models:
                model_name = model['name']
                if model_name not in all_models:
                    all_models[model_name] = {
                        'name': model_name,
                        'url': model['url'],
                        'downloads': model['downloads'],
                        'downloads_all_time': model['downloads_all_time'],
                        'likes': model['likes'],
                        'supported_languages': set()
                    }
                all_models[model_name]['supported_languages'].add(language)
        
        # Create matrix
        languages = list(LANGUAGES.keys())
        matrix_data = []
        
        for model_name, model_info in all_models.items():
            row = {
                'Model': model_name,
                'URL': model_info['url'],
                'Downloads': model_info['downloads'],
                'Downloads_All_Time': model_info['downloads_all_time'],
                'Likes': model_info['likes'],
                'Languages_Supported': len(model_info['supported_languages'])
            }
            
            # Add language columns
            for language in languages:
                row[language] = 'Yes' if language in model_info['supported_languages'] else 'No'
            
            matrix_data.append(row)
        
        # Create DataFrame and sort
        df = pd.DataFrame(matrix_data)
        df = df.sort_values(['Languages_Supported', 'Likes'], ascending=[False, False])
        
        return df
    
    def save_results(self, results: Dict[str, List[Dict]], matrix: pd.DataFrame):
        """Save results to CSV files"""
        
        # Save individual language files
        for language, models in results.items():
            if models:
                df = pd.DataFrame(models)
                filename = f"asr_models_{language.lower()}.csv"
                df.to_csv(filename, index=False)
                print(f"Saved {len(models)} {language} models to {filename}")
        
        # Save matrix
        matrix.to_csv("asr_language_support_matrix.csv", index=False)
        print(f"Saved language support matrix to asr_language_support_matrix.csv")
        
        # Show preview
        print("\n=== Top 10 Models by Language Support ===")
        preview_columns = ['Model', 'Languages_Supported', 'Downloads', 'Likes'] + list(LANGUAGES.keys())
        print(matrix.head(10)[preview_columns].to_string(index=False, max_colwidth=40))


def main():
    scraper = HuggingFaceASRScraper()
    
    print("Starting ASR model search for African languages...")
    print(f"Target languages: {list(LANGUAGES.keys())}")
    
    # Get all models
    results = scraper.scrape_all_languages()
    
    # Create matrix
    matrix = scraper.create_language_matrix(results)
    
    # Save results
    scraper.save_results(results, matrix)
    
    # Summary
    print(f"\n=== Summary ===")
    total_models = len(set(model['name'] for models in results.values() for model in models))
    print(f"Total unique models found: {total_models}")
    
    for language, models in results.items():
        print(f"{language}: {len(models)} models")


if __name__ == "__main__":
    main()
