#!/usr/bin/env python3
"""
Supercharged Creative AI Web Discovery Agent
Searches multiple sources + Perplexity AI for creative websites
"""

import os
import json
import requests
import time
from datetime import datetime
from github import Github
import base64
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import random

def get_headers():
    """Get rotating headers to avoid detection"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def search_perplexity(query):
    """Search using Perplexity API if available"""
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    if not perplexity_key:
        print("⚠️ No Perplexity API key - skipping Perplexity search")
        return []
    
    try:
        print(f"🧠 Searching Perplexity: {query}")
        
        headers = {
            'Authorization': f'Bearer {perplexity_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "user", 
                    "content": f"Find 5 creative, experimental, or quirky AI websites for: {query}. Return only the URLs, one per line, no explanations."
                }
            ]
        }
        
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            json=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            urls = re.findall(r'https?://[^\s\n]+', content)
            print(f"🎯 Perplexity found {len(urls)} URLs")
            return urls[:5]  # Limit to 5
        else:
            print(f"⚠️ Perplexity API error: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Perplexity search error: {e}")
    
    return []

def search_duckduckgo(query, max_results=5):
    """Search DuckDuckGo for creative AI sites"""
    try:
        print(f"🦆 Searching DuckDuckGo: {query}")
        search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=get_headers(), timeout=15)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='result')[:max_results]:
            title_elem = result.find('a', class_='result__a')
            if title_elem:
                url = title_elem.get('href')
                title = title_elem.get_text().strip()
                
                if url and url.startswith('http'):
                    results.append({
                        'url': url,
                        'title': title,
                        'source': 'DuckDuckGo'
                    })
        
        print(f"  Found {len(results)} results from DuckDuckGo")
        return results
        
    except Exception as e:
        print(f"⚠️ DuckDuckGo search failed: {e}")
        return []

def search_reddit_ai(query):
    """Search Reddit for AI tool discussions"""
    try:
        print(f"🤖 Searching Reddit: {query}")
        reddit_query = f"site:reddit.com {query} AI tool 2024 2025"
        search_url = f"https://duckduckgo.com/html/?q={reddit_query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result')[:3]:
            title_elem = result.find('a', class_='result__a')
            if title_elem and 'reddit.com' in title_elem.get('href', ''):
                url = title_elem.get('href')
                title = f"[Reddit] {title_elem.get_text().strip()}"
                results.append({
                    'url': url,
                    'title': title,
                    'source': 'Reddit'
                })
        
        print(f"  Found {len(results)} Reddit discussions")
        return results
        
    except Exception as e:
        print(f"⚠️ Reddit search failed: {e}")
        return []

def search_producthunt(query):
    """Search ProductHunt for AI products"""
    try:
        print(f"🚀 Searching ProductHunt: {query}")
        ph_query = f"site:producthunt.com {query} AI"
        search_url = f"https://duckduckgo.com/html/?q={ph_query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result')[:4]:
            title_elem = result.find('a', class_='result__a')
            if title_elem and 'producthunt.com' in title_elem.get('href', ''):
                url = title_elem.get('href')
                title = f"[ProductHunt] {title_elem.get_text().strip()}"
                results.append({
                    'url': url,
                    'title': title,
                    'source': 'ProductHunt'
                })
        
        print(f"  Found {len(results)} ProductHunt products")
        return results
        
    except Exception as e:
        print(f"⚠️ ProductHunt search failed: {e}")
        return []

def search_github_ai(query):
    """Search GitHub for AI projects"""
    try:
        print(f"🐙 Searching GitHub: {query}")
        github_query = f"site:github.com {query} AI creative tool"
        search_url = f"https://duckduckgo.com/html/?q={github_query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result')[:3]:
            title_elem = result.find('a', class_='result__a')
            if title_elem and 'github.com' in title_elem.get('href', ''):
                url = title_elem.get('href')
                title = f"[GitHub] {title_elem.get_text().strip()}"
                results.append({
                    'url': url,
                    'title': title,
                    'source': 'GitHub'
                })
        
        print(f"  Found {len(results)} GitHub projects")
        return results
        
    except Exception as e:
        print(f"⚠️ GitHub search failed: {e}")
        return []

def search_hackernews(query):
    """Search Hacker News for AI discussions"""
    try:
        print(f"📰 Searching Hacker News: {query}")
        hn_query = f"site:news.ycombinator.com {query} AI"
        search_url = f"https://duckduckgo.com/html/?q={hn_query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result')[:2]:
            title_elem = result.find('a', class_='result__a')
            if title_elem and 'ycombinator.com' in title_elem.get('href', ''):
                url = title_elem.get('href')
                title = f"[HackerNews] {title_elem.get_text().strip()}"
                results.append({
                    'url': url,
                    'title': title,
                    'source': 'HackerNews'
                })
        
        print(f"  Found {len(results)} HackerNews discussions")
        return results
        
    except Exception as e:
        print(f"⚠️ HackerNews search failed: {e}")
        return []

def search_ai_specific_sites(query):
    """Search AI-specific sites"""
    try:
        print(f"🤖 Searching AI-specific sites: {query}")
        ai_sites_query = f"(site:huggingface.co OR site:paperswithcode.com OR site:towardsdatascience.com) {query}"
        search_url = f"https://duckduckgo.com/html/?q={ai_sites_query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result')[:3]:
            title_elem = result.find('a', class_='result__a')
            if title_elem:
                url = title_elem.get('href')
                title = title_elem.get_text().strip()
                
                site_name = "AI Site"
                if 'huggingface' in url:
                    site_name = "HuggingFace"
                elif 'paperswithcode' in url:
                    site_name = "Papers with Code"
                elif 'towardsdatascience' in url:
                    site_name = "Towards Data Science"
                
                results.append({
                    'url': url,
                    'title': f"[{site_name}] {title}",
                    'source': site_name
                })
        
        print(f"  Found {len(results)} AI-specific results")
        return results
        
    except Exception as e:
        print(f"⚠️ AI sites search failed: {e}")
        return []

def analyze_website_content(url):
    """Analyze website content and create structured data"""
    try:
        response = requests.get(url, headers=get_headers(), timeout=8)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Unknown Site"
        title_text = re.sub(r'\s+', ' ', title_text)[:100]
        
        # Extract description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        if not description:
            first_p = soup.find('p')
            description = first_p.get_text().strip()[:200] if first_p else ""
        
        description = re.sub(r'\s+', ' ', description).strip()[:200]
        
        # Intelligent categorization
        content_lower = f"{title_text} {description}".lower()
        category = "creative"
        emoji = "🎨"
        tags = ["AI"]
        
        # Advanced categorization logic
        if any(word in content_lower for word in ['music', 'audio', 'voice', 'sound', 'sing', 'speech']):
            category = "audio"
            emoji = random.choice(["🎵", "🎤", "🎧", "🔊"])
            tags.extend(["Music", "Audio"])
        elif any(word in content_lower for word in ['art', 'draw', 'paint', 'image', 'visual', 'design', 'create']):
            category = "creative"
            emoji = random.choice(["🎨", "✨", "🖌️", "🎭", "🌈"])
            tags.extend(["Art", "Creative"])
        elif any(word in content_lower for word in ['game', 'play', 'interactive', 'fun', 'quiz']):
            category = "games"
            emoji = random.choice(["🎮", "🎯", "🎲", "🎪"])
            tags.extend(["Game", "Interactive"])
        elif any(word in content_lower for word in ['tool', 'assistant', 'helper', 'utility', 'productivity']):
            category = "ai-tools"
            emoji = random.choice(["🤖", "⚡", "🔧", "🛠️"])
            tags.append("Tools")
        elif any(word in content_lower for word in ['weird', 'strange', 'experimental', 'research', 'demo']):
            category = "experimental"
            emoji = random.choice(["🧪", "⚗️", "🔬", "🌀"])
            tags.append("Experimental")
        elif any(word in content_lower for word in ['funny', 'humor', 'joke', 'meme', 'absurd']):
            category = "fun"
            emoji = random.choice(["😄", "🤪", "😂", "🎉"])
            tags.append("Humor")
        
        # Add specific feature tags
        if any(word in content_lower for word in ['generate', 'generator', 'creation']):
            tags.append("Generation")
        if any(word in content_lower for word in ['neural', 'network', 'deep learning']):
            tags.append("Neural Networks")
        if any(word in content_lower for word in ['text', 'writing', 'copy']):
            tags.append("Text")
        if any(word in content_lower for word in ['video', 'animation', 'motion']):
            tags.append("Video")
        
        # Remove duplicates and limit tags
        tags = list(set(tags))[:4]
        
        return {
            "title": title_text,
            "description": description or "An interesting AI-powered creative tool",
            "link": url,
            "category": category,
            "emoji": emoji,
            "tags": tags
        }
        
    except Exception as e:
        print(f"⚠️ Could not analyze {url}: {e}")
        return None

def discover_creative_sites():
    """Main discovery function using all sources"""
    print("🌐 Starting multi-source creative AI discovery...")
    
    # Creative search queries
    creative_queries = [
        "creative AI art generator 2024",
        "experimental AI music tools",
        "weird AI websites interactive",
        "quirky AI experiments online",
        "AI drawing playground",
        "neural network creative tools",
        "AI text generation fun",
        "interactive AI experiences",
        "AI voice synthesis creative",
        "generative art AI tools"
    ]
    
    all_discovered_sites = []
    seen_urls = set()
    
    for query in creative_queries[:6]:  # Limit queries to avoid timeout
        print(f"\n🔍 Processing query: '{query}'")
        
        query_results = []
        
        # Search all sources for this query
        query_results.extend(search_duckduckgo(query, 3))
        time.sleep(1)
        
        query_results.extend(search_reddit_ai(query))
        time.sleep(1)
        
        query_results.extend(search_producthunt(query))
        time.sleep(1)
        
        query_results.extend(search_github_ai(query))
        time.sleep(1)
        
        query_results.extend(search_hackernews(query))
        time.sleep(1)
        
        query_results.extend(search_ai_specific_sites(query))
        time.sleep(1)
        
        # Use Perplexity for this query
        perplexity_urls = search_perplexity(query)
        for url in perplexity_urls:
            query_results.append({
                'url': url,
                'title': f"[Perplexity] Found via AI search",
                'source': 'Perplexity'
            })
        
        # Analyze promising results
        for result in query_results:
            url = result['url']
            if url in seen_urls or not url.startswith('http'):
                continue
            
            seen_urls.add(url)
            
            # Skip certain domains
            skip_domains = ['reddit.com', 'github.com/topics', 'news.ycombinator.com']
            if any(domain in url for domain in skip_domains):
                continue
            
            print(f"  📝 Analyzing: {result['title'][:50]}...")
            
            site_data = analyze_website_content(url)
            if site_data:
                all_discovered_sites.append(site_data)
                print(f"    ✨ Added: {site_data['title']} ({site_data['category']})")
        
        time.sleep(2)  # Rate limiting between queries
    
    print(f"\n🎯 Total sites discovered: {len(all_discovered_sites)}")
    return all_discovered_sites

def main():
    print("🚀 Supercharged Creative AI Discovery Agent Starting...")
    print("🌐 Multi-source search: DuckDuckGo + Reddit + ProductHunt + GitHub + HackerNews + AI Sites + Perplexity")
    
    # Get environment variables
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    
    if not all([GITHUB_TOKEN, GITHUB_REPO]):
        print("❌ Missing required environment variables")
        return
    
    # Initialize GitHub
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPO)
    
    # Discover new creative AI sites
    discovered_sites = discover_creative_sites()
    
    # Load existing data
    existing_sites = []
    try:
        file = repo.get_contents("creative_discoveries.json")
        content = base64.b64decode(file.content).decode('utf-8')
        existing_sites = json.loads(content)
        print(f"📚 Loaded {len(existing_sites)} existing sites")
    except:
        print("📝 Creating new creative discoveries file")
    
    # Filter for truly new sites
    existing_urls = {site.get('link', '') for site in existing_sites}
    new_sites = [site for site in discovered_sites if site['link'] not in existing_urls]
    
    if new_sites:
        print(f"\n🎉 DISCOVERED {len(new_sites)} NEW CREATIVE AI SITES!")
        
        # Show what was found
        for site in new_sites:
            print(f"  {site['emoji']} {site['title']} - {site['category']}")
        
        # Add to existing collection
        all_sites = existing_sites + new_sites
        
        # Save to GitHub
        content = json.dumps(all_sites, indent=2, ensure_ascii=False)
        
        try:
            file = repo.get_contents("creative_discoveries.json")
            repo.update_file(
                path="creative_discoveries.json",
                message=f"🚀 Multi-source discovery: {len(new_sites)} new creative AI sites - {datetime.now().strftime('%Y-%m-%d')}",
                content=content,
                sha=file.sha
            )
        except:
            repo.create_file(
                path="creative_discoveries.json",
                message=f"🚀 Create multi-source creative AI discoveries - {datetime.now().strftime('%Y-%m-%d')}",
                content=content
            )
        
        print(f"💾 Saved {len(new_sites)} new sites to GitHub!")
        print(f"🎊 Total creative sites: {len(all_sites)}")
        
    else:
        print("🔍 No new creative AI sites found - all discovered sites already exist in collection!")
    
    print("\n✅ Supercharged multi-source discovery complete!")

if __name__ == "__main__":
    main()