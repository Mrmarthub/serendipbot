#!/usr/bin/env python3
"""
Pure Web Discovery Agent
Discovers creative AI sites fresh from the web using alternative methods
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
from urllib.parse import urljoin, urlparse, quote
import random
import feedparser

def get_rotating_headers():
    """Get different headers to avoid detection"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

def search_bing_creative_ai():
    """Use Bing search API or scraping for AI discoveries"""
    print("🔍 Searching Bing for creative AI sites...")
    discovered_sites = []
    
    search_queries = [
        "new AI art generator 2024 site:*.ai",
        "creative AI tool launched 2024",
        "experimental AI website interactive",
        "AI music generator new platform",
        "text to image AI tool 2024",
        "AI voice synthesis new site",
        "neural network art creative tool",
        "generative AI platform new",
        "AI writing assistant creative 2024",
        "interactive AI experiment website"
    ]
    
    for query in search_queries[:4]:  # Limit queries
        try:
            print(f"  🎯 Query: {query}")
            
            # Try Bing search
            bing_url = f"https://www.bing.com/search?q={quote(query)}&count=10"
            headers = get_rotating_headers()
            
            response = requests.get(bing_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for search result links
                results = soup.find_all('h2') + soup.find_all('a', href=True)
                
                for result in results[:5]:  # Limit results per query
                    if result.name == 'h2':
                        link = result.find('a', href=True)
                        if link:
                            url = link.get('href')
                            title = link.get_text().strip()
                        else:
                            continue
                    else:
                        url = result.get('href')
                        title = result.get_text().strip()
                    
                    if url and url.startswith('http') and len(url) > 20:
                        # Filter for AI-related domains
                        if any(keyword in url.lower() for keyword in ['.ai', 'ai-', 'artificial', 'neural', 'ml-', 'deep', 'generate', 'create']):
                            site_info = analyze_discovered_site(url, title)
                            if site_info:
                                discovered_sites.append(site_info)
                                print(f"    ✨ Found: {site_info['title']}")
                
            time.sleep(random.uniform(3, 6))  # Random delay to avoid blocks
            
        except Exception as e:
            print(f"    ⚠️ Bing search error: {e}")
            time.sleep(5)
    
    print(f"  📊 Bing discovered: {len(discovered_sites)} sites")
    return discovered_sites

def search_alternative_engines():
    """Try alternative search engines that are less likely to block"""
    print("🌐 Searching alternative engines...")
    discovered_sites = []
    
    # Try Startpage (privacy-focused Google proxy)
    try:
        print("  🔍 Trying Startpage...")
        query = "creative AI tool 2024"
        startpage_url = f"https://startpage.com/sp/search?query={quote(query)}"
        
        response = requests.get(startpage_url, headers=get_rotating_headers(), timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for result links
            links = soup.find_all('a', href=True)
            for link in links[:10]:
                url = link.get('href')
                if url and url.startswith('http') and 'ai' in url.lower():
                    title = link.get_text().strip()
                    site_info = analyze_discovered_site(url, title)
                    if site_info:
                        discovered_sites.append(site_info)
                        print(f"    ✨ Startpage found: {site_info['title']}")
        
        time.sleep(random.uniform(4, 7))
        
    except Exception as e:
        print(f"    ⚠️ Startpage error: {e}")
    
    # Try Searx instances (open source search)
    try:
        print("  🔍 Trying Searx...")
        searx_instances = [
            "https://search.bus-hit.me",
            "https://searx.be",
            "https://searx.tiekoetter.com"
        ]
        
        searx_url = random.choice(searx_instances)
        query_url = f"{searx_url}/search?q=AI+creative+tool+2024&categories=general"
        
        response = requests.get(query_url, headers=get_rotating_headers(), timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = soup.find_all('h3') + soup.find_all('a', href=True)
            for result in results[:8]:
                if result.name == 'h3':
                    link = result.find('a', href=True)
                    if link:
                        url = link.get('href')
                        title = link.get_text().strip()
                    else:
                        continue
                else:
                    url = result.get('href')
                    title = result.get_text().strip()
                
                if url and url.startswith('http') and any(ai_word in url.lower() for ai_word in ['ai', 'artificial', 'neural', 'ml']):
                    site_info = analyze_discovered_site(url, title)
                    if site_info:
                        discovered_sites.append(site_info)
                        print(f"    ✨ Searx found: {site_info['title']}")
        
        time.sleep(random.uniform(3, 5))
        
    except Exception as e:
        print(f"    ⚠️ Searx error: {e}")
    
    print(f"  📊 Alternative engines discovered: {len(discovered_sites)} sites")
    return discovered_sites

def discover_from_rss_feeds():
    """Discover AI sites from RSS feeds and news sources"""
    print("📡 Discovering from RSS feeds...")
    discovered_sites = []
    
    # AI/Tech RSS feeds that might mention new tools
    rss_feeds = [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/ai/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://feeds.feedburner.com/oreilly/radar",
        "https://www.wired.com/feed/tag/ai/latest/rss"
    ]
    
    for feed_url in rss_feeds[:3]:  # Limit feeds
        try:
            print(f"  📰 Checking feed: {feed_url.split('/')[2]}")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:  # Check recent entries
                title = entry.get('title', '')
                link = entry.get('link', '')
                description = entry.get('summary', '')
                
                # Look for AI tool mentions in content
                content = f"{title} {description}".lower()
                if any(keyword in content for keyword in ['ai tool', 'ai platform', 'new ai', 'ai app', 'ai website', 'ai service']):
                    
                    # Try to extract mentioned URLs from the content
                    urls = re.findall(r'https?://[^\s<>"]+', description)
                    for url in urls:
                        if any(ai_indicator in url.lower() for ai_indicator in ['.ai', 'ai-', 'artificial', 'neural']):
                            site_info = analyze_discovered_site(url, f"[RSS] {title}")
                            if site_info:
                                discovered_sites.append(site_info)
                                print(f"    ✨ RSS found: {site_info['title']}")
            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"    ⚠️ RSS feed error: {e}")
    
    print(f"  📊 RSS discovered: {len(discovered_sites)} sites")
    return discovered_sites

def discover_from_github_trending():
    """Find AI projects from GitHub trending that might have web interfaces"""
    print("🐙 Checking GitHub trending AI projects...")
    discovered_sites = []
    
    try:
        # Get trending AI repositories
        github_url = "https://github.com/trending?l=python&since=weekly"
        response = requests.get(github_url, headers=get_rotating_headers(), timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for repo links
            repo_links = soup.find_all('a', href=True)
            
            for link in repo_links[:10]:
                href = link.get('href')
                if href and href.startswith('/') and len(href.split('/')) >= 3:
                    repo_url = f"https://github.com{href}"
                    title = link.get_text().strip()
                    
                    # Check if it's an AI-related repo
                    if any(ai_word in title.lower() for ai_word in ['ai', 'artificial', 'neural', 'ml', 'deep', 'generate']):
                        
                        # Try to find if this repo has a web demo
                        try:
                            repo_response = requests.get(repo_url, headers=get_rotating_headers(), timeout=10)
                            if repo_response.status_code == 200:
                                repo_soup = BeautifulSoup(repo_response.content, 'html.parser')
                                
                                # Look for demo links in README or description
                                demo_links = repo_soup.find_all('a', href=True)
                                for demo_link in demo_links:
                                    demo_href = demo_link.get('href')
                                    demo_text = demo_link.get_text().strip().lower()
                                    
                                    if demo_href and demo_href.startswith('http') and any(demo_word in demo_text for demo_word in ['demo', 'try', 'app', 'website', 'live']):
                                        site_info = analyze_discovered_site(demo_href, f"[GitHub] {title}")
                                        if site_info:
                                            discovered_sites.append(site_info)
                                            print(f"    ✨ GitHub demo found: {site_info['title']}")
                                            break
                        except:
                            pass
                        
                        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        print(f"    ⚠️ GitHub trending error: {e}")
    
    print(f"  📊 GitHub discovered: {len(discovered_sites)} sites")
    return discovered_sites

def analyze_discovered_site(url, fallback_title=""):
    """Analyze a discovered site to create structured data"""
    try:
        print(f"    🔍 Analyzing: {url}")
        
        response = requests.get(url, headers=get_rotating_headers(), timeout=8)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text().strip() if title_elem else fallback_title
        title = re.sub(r'\s+', ' ', title)[:100]
        
        if not title or title.lower() in ['', 'untitled', 'loading...']:
            title = fallback_title or urlparse(url).netloc
        
        # Extract description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        if not description:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc:
                description = meta_desc.get('content', '')
        
        if not description:
            # Try first paragraph
            first_p = soup.find('p')
            if first_p:
                description = first_p.get_text().strip()[:200]
        
        description = re.sub(r'\s+', ' ', description.strip())[:200] if description else "AI-powered creative tool discovered from web search"
        
        # Smart categorization based on content
        content_text = f"{title} {description} {url}".lower()
        
        category = "creative"  # Default
        emoji = "🎨"
        tags = ["AI", "Discovered"]
        
        # Categorize based on keywords
        if any(word in content_text for word in ['art', 'image', 'photo', 'visual', 'design', 'draw', 'paint', 'creative']):
            category = "creative"
            emoji = random.choice(["🎨", "✨", "🖌️", "🎭"])
            tags.extend(["Art", "Creative"])
            
        elif any(word in content_text for word in ['music', 'audio', 'voice', 'sound', 'sing', 'compose']):
            category = "audio"
            emoji = random.choice(["🎵", "🎤", "🎧", "🔊"])
            tags.extend(["Music", "Audio"])
            
        elif any(word in content_text for word in ['game', 'play', 'interactive', 'fun', 'quiz', 'adventure']):
            category = "games"
            emoji = random.choice(["🎮", "🎯", "🎲", "🎪"])
            tags.extend(["Game", "Interactive"])
            
        elif any(word in content_text for word in ['write', 'text', 'copy', 'content', 'article', 'blog']):
            category = "ai-tools"
            emoji = random.choice(["✍️", "📝", "💬", "📄"])
            tags.extend(["Writing", "Text"])
            
        elif any(word in content_text for word in ['video', 'animation', 'movie', 'film', 'motion']):
            category = "creative"
            emoji = random.choice(["🎬", "🎥", "📹", "🎞️"])
            tags.extend(["Video", "Animation"])
            
        elif any(word in content_text for word in ['chat', 'conversation', 'assistant', 'bot', 'talk']):
            category = "ai-tools"
            emoji = random.choice(["🤖", "💬", "🗣️", "💭"])
            tags.append("Assistant")
            
        elif any(word in content_text for word in ['experiment', 'research', 'demo', 'test', 'lab']):
            category = "experimental"
            emoji = random.choice(["🧪", "⚗️", "🔬", "🧬"])
            tags.append("Experimental")
            
        elif any(word in content_text for word in ['weird', 'funny', 'humor', 'strange', 'quirky']):
            category = "fun"
            emoji = random.choice(["😄", "🤪", "😂", "🎉"])
            tags.append("Humor")
        
        # Add more specific tags
        if 'generate' in content_text or 'generator' in content_text:
            tags.append("Generation")
        if 'neural' in content_text or 'deep learning' in content_text:
            tags.append("Neural Networks")
        if 'open source' in content_text or 'github' in url:
            tags.append("Open Source")
        
        # Remove duplicates and limit tags
        tags = list(set(tags))[:4]
        
        return {
            "title": title,
            "description": description,
            "link": url,
            "category": category,
            "emoji": emoji,
            "tags": tags
        }
        
    except Exception as e:
        print(f"    ⚠️ Analysis error for {url}: {e}")
        return None

def main():
    print("🚀 Pure Web Discovery Agent Starting...")
    print("🌐 Discovering creative AI sites fresh from the web")
    print("🔍 Sources: Bing + Alternative Engines + RSS Feeds + GitHub Trending")
    
    # Get environment variables
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    
    if not all([GITHUB_TOKEN, GITHUB_REPO]):
        print("❌ Missing required environment variables")
        return
    
    # Initialize GitHub
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPO)
    
    print("\n🔍 Starting web discovery...")
    all_discovered = []
    
    # Try different discovery methods
    all_discovered.extend(search_bing_creative_ai())
    time.sleep(random.uniform(5, 8))
    
    all_discovered.extend(search_alternative_engines())
    time.sleep(random.uniform(5, 8))
    
    all_discovered.extend(discover_from_rss_feeds())
    time.sleep(random.uniform(3, 6))
    
    all_discovered.extend(discover_from_github_trending())
    
    # Remove duplicates
    seen_urls = set()
    unique_discovered = []
    for site in all_discovered:
        if site['link'] not in seen_urls:
            unique_discovered.append(site)
            seen_urls.add(site['link'])
    
    print(f"\n🎯 Total unique sites discovered from web: {len(unique_discovered)}")
    
    if not unique_discovered:
        print("🔍 No new sites discovered from web search - search engines may be blocking requests")
        print("💡 Try running again later or consider using API-based search services")
        return
    
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
    new_sites = [site for site in unique_discovered if site['link'] not in existing_urls]
    
    if new_sites:
        print(f"\n🎉 DISCOVERED {len(new_sites)} NEW CREATIVE AI SITES FROM THE WEB!")
        
        # Show breakdown by category
        categories = {}
        for site in new_sites:
            cat = site['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("📊 New sites by category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} sites")
        
        # Add to existing collection
        all_sites = existing_sites + new_sites
        
        # Save to GitHub
        content = json.dumps(all_sites, indent=2, ensure_ascii=False)
        
        try:
            file = repo.get_contents("creative_discoveries.json")
            repo.update_file(
                path="creative_discoveries.json",
                message=f"🌐 Pure web discovery: {len(new_sites)} fresh AI sites from the web - {datetime.now().strftime('%Y-%m-%d')}",
                content=content,
                sha=file.sha
            )
        except:
            repo.create_file(
                path="creative_discoveries.json",
                message=f"🌐 Create web-discovered creative AI sites - {datetime.now().strftime('%Y-%m-%d')}",
                content=content
            )
        
        print(f"\n💾 Saved {len(new_sites)} new web-discovered sites to GitHub!")
        print(f"🎊 Total creative sites: {len(all_sites)}")
        
        # Show examples
        print(f"\n✨ Examples of web discoveries:")
        for site in new_sites[:5]:
            print(f"  {site['emoji']} {site['title']} - {site['category']}")
        
    else:
        print("🔍 All discovered sites already exist in collection - web search found known sites")
    
    print("\n✅ Pure web discovery complete!")

if __name__ == "__main__":
    main()