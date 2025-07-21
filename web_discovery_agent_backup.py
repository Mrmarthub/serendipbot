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
            "innovative AI tools 2025",
            "creative AI applications", 
            "quirky AI websites",
            "useful AI services",
            "AI-powered web apps",
            "experimental AI projects",
            "fun AI tools",
            "productivity AI tools",
            "AI art generators",
            "AI coding assistants",
            "AI music tools",
            "AI writing tools",
            "AI browser extensions",
            "AI startup tools",
            "weird AI experiments"
        ]
        
        # Rotating user agents to avoid blocks
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        self.current_ua_index = 0
        
    def get_headers(self):
        """Get rotating headers to avoid detection"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return {
            'User-Agent': self.user_agents[self.current_ua_index],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def search_web(self, query: str, num_results: int = 15) -> List[Dict]:
        """Search web using multiple sources with anti-detection measures"""
        all_results = []
        seen_urls = set()
        
        # Enhanced fallback with more diverse AI sites
        quality_ai_sites = [
            {'url': 'https://beta.openai.com/playground', 'title': 'OpenAI Playground', 'snippet': 'Interactive AI playground for GPT models'},
            {'url': 'https://huggingface.co/spaces', 'title': 'Hugging Face Spaces', 'snippet': 'Community AI model demos and applications'},
            {'url': 'https://replicate.com/explore', 'title': 'Replicate Explore', 'snippet': 'Discover and run AI models in the cloud'},
            {'url': 'https://runwayml.com/ai-tools', 'title': 'RunwayML AI Tools', 'snippet': 'Creative AI tools for content creators'},
            {'url': 'https://stability.ai/stablediffusion', 'title': 'Stable Diffusion', 'snippet': 'Open source AI image generation'},
            {'url': 'https://claude.ai', 'title': 'Claude AI', 'snippet': 'Anthropic AI assistant for conversations and tasks'},
            {'url': 'https://perplexity.ai', 'title': 'Perplexity AI', 'snippet': 'AI-powered search and research assistant'},
            {'url': 'https://character.ai', 'title': 'Character.AI', 'snippet': 'Chat with AI characters and personalities'},
            {'url': 'https://midjourney.com', 'title': 'Midjourney', 'snippet': 'AI art generation through Discord'},
            {'url': 'https://fireflies.ai', 'title': 'Fireflies AI', 'snippet': 'AI meeting notes and transcription'},
            {'url': 'https://jasper.ai', 'title': 'Jasper AI', 'snippet': 'AI copywriting and content creation'},
            {'url': 'https://copy.ai', 'title': 'Copy.ai', 'snippet': 'AI-powered writing assistant'},
            {'url': 'https://writesonic.com', 'title': 'Writesonic', 'snippet': 'AI content generator for marketing'},
            {'url': 'https://luma.ai', 'title': 'Luma AI', 'snippet': '3D content creation with AI'},
            {'url': 'https://elevenlabs.io', 'title': 'ElevenLabs', 'snippet': 'AI voice synthesis and cloning'},
            {'url': 'https://synthesia.io', 'title': 'Synthesia', 'snippet': 'AI video generation with avatars'},
            {'url': 'https://tavus.io', 'title': 'Tavus', 'snippet': 'Personalized AI video generation'},
            {'url': 'https://murf.ai', 'title': 'Murf AI', 'snippet': 'AI voiceover and text-to-speech'},
            {'url': 'https://descript.com', 'title': 'Descript', 'snippet': 'AI-powered audio and video editing'},
            {'url': 'https://beautiful.ai', 'title': 'Beautiful.ai', 'snippet': 'AI presentation design tool'},
        ]
        
        # Try simple web search with better error handling
        search_sources = [
            f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}",
            f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}+2024",
            f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}+tool+website"
        ]
        
        for search_url in search_sources[:1]:  # Try just one to avoid blocks
            try:
                headers = self.get_headers()
                response = requests.get(search_url, headers=headers, timeout=8)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    count = 0
                    for result in soup.find_all('div', class_='result')[:10]:
                        title_elem = result.find('a', class_='result__a')
                        if title_elem and count < 3:  # Limit to avoid overloading
                            url = title_elem.get('href')
                            if url and url.startswith('http') and url not in seen_urls:
                                title = title_elem.get_text().strip()
                                snippet_elem = result.find('div', class_='result__snippet')
                                snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                                
                                all_results.append({'url': url, 'title': title, 'snippet': snippet})
                                seen_urls.add(url)
                                count += 1
                    
                    if count > 0:
                        print(f"Found {count} results from web search")
                        break  # If we got results, don't try other searches
                        
            except Exception as e:
                print(f"Web search failed: {e}")
                continue
        
        # If web search mostly failed, use curated AI sites
        if len(all_results) < 5:
            # Use query-specific AI sites based on the search term
            relevant_sites = []
            query_lower = query.lower()
            
            if 'art' in query_lower or 'creative' in query_lower or 'image' in query_lower:
                relevant_sites = [s for s in quality_ai_sites if any(term in s['snippet'].lower() for term in ['art', 'image', 'creative', 'video', 'design'])]
            elif 'coding' in query_lower or 'developer' in query_lower:
                relevant_sites = [s for s in quality_ai_sites if any(term in s['snippet'].lower() for term in ['code', 'development', 'programming'])]
            elif 'writing' in query_lower or 'content' in query_lower:
                relevant_sites = [s for s in quality_ai_sites if any(term in s['snippet'].lower() for term in ['writing', 'content', 'copy', 'text'])]
            elif 'music' in query_lower or 'audio' in query_lower or 'voice' in query_lower:
                relevant_sites = [s for s in quality_ai_sites if any(term in s['snippet'].lower() for term in ['voice', 'audio', 'sound', 'music'])]
            else:
                # General AI tools
                relevant_sites = quality_ai_sites[:8]
            
            # Add relevant sites that aren't already included
            for site in relevant_sites[:6]:
                if site['url'] not in seen_urls:
                    all_results.append(site)
                    seen_urls.add(site['url'])
            
            # If still not enough, add more general sites
            if len(all_results) < 5:
                for site in quality_ai_sites:
                    if site['url'] not in seen_urls and len(all_results) < 8:
                        all_results.append(site)
                        seen_urls.add(site['url'])
            
            print(f"Added {len([r for r in all_results if r['url'] in [s['url'] for s in quality_ai_sites]])} curated AI sites")
        
        print(f"🎯 Total unique results found: {len(all_results)}")
        return all_results[:num_results]
    
    def extract_website_content(self, url: str) -> Dict:
        """Extract key information from a website"""
        try:
            headers = self.get_headers()
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'  # Force UTF-8 encoding
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
            # Clean up text and handle encoding issues
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Remove any problematic characters
            text_content = text_content.encode('ascii', 'ignore').decode('ascii')
            text_content = text_content[:1500]  # Limit length
            
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
        
        # Clean all text data before sending to AI
        def clean_text(text):
            if not text:
                return ""
            # Remove problematic unicode characters
            cleaned = text.encode('ascii', 'ignore').decode('ascii')
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            return cleaned[:500]  # Limit length
        
        clean_title = clean_text(website_data.get('title', ''))
        clean_description = clean_text(website_data.get('description', ''))
        clean_content = clean_text(website_data.get('content', ''))
        
        prompt = f"""
        Analyze this website and rate it on three dimensions (1-10 scale):

        Website: {clean_title}
        URL: {website_data['url']}
        Description: {clean_description}
        Content Preview: {clean_content}

        Rate this website on:
        1. CREATIVITY (1-10): How innovative, original, or artistically interesting is it?
        2. QUIRKINESS (1-10): How unique, unconventional, or delightfully weird is it?
        3. USEFULNESS (1-10): How practical and valuable is it for users?

        Also identify AI features present (e.g., "chatbot", "image generation", "text analysis").

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
                model="gpt-4o-mini",  # Use cheaper model for testing
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            # Clean the response too
            result_text = result_text.encode('ascii', 'ignore').decode('ascii')
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                print(f"JSON parse error, using defaults for {website_data['url']}")
                result = {
                    "creativity_score": 6.0,
                    "quirkiness_score": 5.0,
                    "usefulness_score": 7.0,
                    "ai_features": ["unknown"],
                    "reasoning": "AI analysis failed"
                }
            
            overall_score = (
                result['creativity_score'] + 
                result['quirkiness_score'] + 
                result['usefulness_score']
            ) / 3
            
            return WebsiteScore(
                url=website_data['url'],
                title=clean_title or "Unknown Title",
                description=clean_description or "No description",
                creativity_score=result['creativity_score'],
                quirkiness_score=result['quirkiness_score'],
                usefulness_score=result['usefulness_score'],
                overall_score=overall_score,
                ai_features=result.get('ai_features', []),
                discovered_date=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"AI analysis error for {website_data['url']}: {e}")
            # Return a working fallback score based on URL analysis
            if any(keyword in website_data['url'].lower() for keyword in ['openai', 'gpt', 'ai']):
                creativity, quirkiness, usefulness = 8.0, 6.0, 9.0
            elif any(keyword in website_data['url'].lower() for keyword in ['art', 'creative', 'design']):
                creativity, quirkiness, usefulness = 9.0, 8.0, 7.0
            else:
                creativity, quirkiness, usefulness = 6.0, 5.0, 7.0
            
            overall_score = (creativity + quirkiness + usefulness) / 3
            
            return WebsiteScore(
                url=website_data['url'],
                title=clean_title or "Unknown Title",
                description=clean_description or "No description",
                creativity_score=creativity,
                quirkiness_score=quirkiness,
                usefulness_score=usefulness,
                overall_score=overall_score,
                ai_features=["ai-tool"],
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