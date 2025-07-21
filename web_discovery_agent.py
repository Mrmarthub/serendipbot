#!/usr/bin/env python3
"""
AI Web Discovery Agent
Searches for interesting AI-powered websites, scores them, and stores results in GitHub
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import openai
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import base64
from github import Github

@dataclass
class WebsiteScore:
    url: str
    title: str
    description: str
    creativity_score: float
    quirkiness_score: float
    usefulness_score: float
    overall_score: float
    ai_features: List[str]
    discovered_date: str
    screenshot_url: Optional[str] = None

class WebDiscoveryAgent:
    def __init__(self, 
                 openai_api_key: str,
                 github_token: str,
                 github_repo: str,
                 search_queries: List[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.github = Github(github_token)
        self.repo = self.github.get_repo(github_repo)
        
        self.search_queries = search_queries or [
            "innovative AI tools 2024",
            "creative AI applications",
            "quirky AI websites",
            "useful AI services",
            "AI-powered web apps",
            "experimental AI projects",
            "fun AI tools",
            "productivity AI tools"
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def search_web(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search web using Google Custom Search API or fallback to scraping"""
        # Using DuckDuckGo as a free alternative
        search_url = f"https://duckduckgo.com/html/?q={query}"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='result')[:num_results]:
                title_elem = result.find('a', class_='result__a')
                if title_elem:
                    url = title_elem.get('href')
                    title = title_elem.get_text().strip()
                    
                    snippet_elem = result.find('div', class_='result__snippet')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'snippet': snippet
                    })
            
            return results
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
            return []
    
    def extract_website_content(self, url: str) -> Dict:
        """Extract key information from a website"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Extract description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            if not description:
                # Fallback to first paragraph
                first_p = soup.find('p')
                description = first_p.get_text().strip()[:200] if first_p else ""
            
            # Extract main text content
            for script in soup(["script", "style"]):
                script.decompose()
            
            text_content = soup.get_text()
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)[:1500]
            
            return {
                'title': title_text,
                'description': description,
                'content': text_content,
                'url': url
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return {'title': '', 'description': '', 'content': '', 'url': url}
    
    def analyze_with_ai(self, website_data: Dict) -> WebsiteScore:
        """Use AI to analyze and score the website"""
        prompt = f"""
        Analyze this website and rate it on three dimensions (1-10 scale):

        Website: {website_data['title']}
        URL: {website_data['url']}
        Description: {website_data['description']}
        Content Preview: {website_data['content'][:800]}

        Rate this website on:
        1. CREATIVITY (1-10): How innovative, original, or artistically interesting is it?
        2. QUIRKINESS (1-10): How unique, unconventional, or delightfully weird is it?
        3. USEFULNESS (1-10): How practical and valuable is it for users?

        Also identify AI features present (e.g., "chatbot", "image generation", "text analysis", "recommendation engine").

        Respond in this exact JSON format:
        {{
            "creativity_score": 7.5,
            "quirkiness_score": 6.0,
            "usefulness_score": 8.5,
            "ai_features": ["chatbot", "text analysis"],
            "reasoning": "Brief explanation of scores"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            overall_score = (
                result['creativity_score'] + 
                result['quirkiness_score'] + 
                result['usefulness_score']
            ) / 3
            
            return WebsiteScore(
                url=website_data['url'],
                title=website_data['title'],
                description=website_data['description'],
                creativity_score=result['creativity_score'],
                quirkiness_score=result['quirkiness_score'],
                usefulness_score=result['usefulness_score'],
                overall_score=overall_score,
                ai_features=result['ai_features'],
                discovered_date=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"AI analysis error for {website_data['url']}: {e}")
            return WebsiteScore(
                url=website_data['url'],
                title=website_data['title'],
                description=website_data['description'],
                creativity_score=5.0,
                quirkiness_score=5.0,
                usefulness_score=5.0,
                overall_score=5.0,
                ai_features=[],
                discovered_date=datetime.now().isoformat()
            )
    
    def load_existing_data(self) -> Dict:
        """Load existing discoveries from GitHub"""
        try:
            file = self.repo.get_contents("ai_discoveries.json")
            content = base64.b64decode(file.content).decode('utf-8')
            return json.loads(content)
        except:
            return {"discoveries": [], "last_updated": ""}
    
    def save_to_github(self, data: Dict):
        """Save discoveries to GitHub repository"""
        try:
            content = json.dumps(data, indent=2, ensure_ascii=False)
            
            try:
                # Try to get existing file
                file = self.repo.get_contents("ai_discoveries.json")
                self.repo.update_file(
                    path="ai_discoveries.json",
                    message=f"Update AI discoveries - {datetime.now().strftime('%Y-%m-%d')}",
                    content=content,
                    sha=file.sha
                )
            except:
                # File doesn't exist, create it
                self.repo.create_file(
                    path="ai_discoveries.json",
                    message=f"Create AI discoveries - {datetime.now().strftime('%Y-%m-%d')}",
                    content=content
                )
                
            print("Data saved to GitHub successfully!")
            
        except Exception as e:
            print(f"Error saving to GitHub: {e}")
    
    def discover_websites(self) -> List[WebsiteScore]:
        """Main discovery process"""
        print("🚀 Starting AI website discovery...")
        
        all_websites = []
        seen_urls = set()
        
        for query in self.search_queries:
            print(f"🔍 Searching: {query}")
            
            search_results = self.search_web(query, num_results=5)
            
            for result in search_results:
                url = result['url']
                
                # Skip duplicates and non-http URLs
                if url in seen_urls or not url.startswith('http'):
                    continue
                    
                seen_urls.add(url)
                
                print(f"📝 Analyzing: {result['title']}")
                
                # Extract website content
                website_data = self.extract_website_content(url)
                
                if not website_data['title']:
                    continue
                
                # Analyze with AI
                score = self.analyze_with_ai(website_data)
                
                # Only include sites with decent overall scores
                if score.overall_score >= 6.0:
                    all_websites.append(score)
                    print(f"✅ Added: {score.title} (Score: {score.overall_score:.1f})")
                
                # Rate limiting
                time.sleep(2)
        
        return sorted(all_websites, key=lambda x: x.overall_score, reverse=True)
    
    def run_daily_discovery(self):
        """Run the daily discovery process"""
        print("🤖 AI Web Discovery Agent Starting...")
        
        # Load existing data
        existing_data = self.load_existing_data()
        existing_urls = {item['url'] for item in existing_data.get('discoveries', [])}
        
        # Discover new websites
        new_discoveries = self.discover_websites()
        
        # Filter out already discovered sites
        truly_new = [site for site in new_discoveries if site.url not in existing_urls]
        
        if truly_new:
            print(f"🎉 Found {len(truly_new)} new interesting websites!")
            
            # Add to existing data
            all_discoveries = existing_data.get('discoveries', [])
            for discovery in truly_new:
                all_discoveries.append(asdict(discovery))
            
            # Sort by overall score
            all_discoveries.sort(key=lambda x: x['overall_score'], reverse=True)
            
            # Keep only top 100 to avoid file getting too large
            all_discoveries = all_discoveries[:100]
            
            updated_data = {
                'discoveries': all_discoveries,
                'last_updated': datetime.now().isoformat(),
                'total_discoveries': len(all_discoveries)
            }
            
            # Save to GitHub
            self.save_to_github(updated_data)
            
        else:
            print("🔍 No new discoveries today, but that's okay!")

# Example usage and configuration
def main():
    # Configuration - set these as environment variables
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')  # format: "username/repo-name"
    
    if not all([OPENAI_API_KEY, GITHUB_TOKEN, GITHUB_REPO]):
        print("❌ Missing required environment variables:")
        print("- OPENAI_API_KEY")
        print("- GITHUB_TOKEN")
        print("- GITHUB_REPO")
        return
    
    # Create agent
    agent = WebDiscoveryAgent(
        openai_api_key=OPENAI_API_KEY,
        github_token=GITHUB_TOKEN,
        github_repo=GITHUB_REPO
    )
    
    # Run discovery
    agent.run_daily_discovery()

if __name__ == "__main__":
    main()