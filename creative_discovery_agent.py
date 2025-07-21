#!/usr/bin/env python3
"""
Pure Web Discovery Agent - No External Dependencies
Discovers creative AI sites fresh from the web using only built-in modules
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
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    }

def search_bing_for_ai_sites():
    """Search Bing for new AI creative tools"""
    print("🔍 Searching Bing for fresh AI sites...")
    discovered_sites = []
    
    search_queries = [
        "new AI art generator 2024",
        "creative AI tool launched recently", 
        "AI music generator new platform",
        "text to image AI 2024",
        "AI voice generator new",
        "interactive AI experiment",
        "generative AI platform new",
        "AI writing tool creative 2024"
    ]
    
    for query in search_queries[:3]:  # Limit to avoid timeout
        try:
            print(f"  🎯 Searching: {query}")
            
            # Bing search URL
            bing_url = f"https://www.bing.com/search?q={quote(query)}&count=10&mkt=en-US"
            headers = get_rotating_headers()
            
            response = requests.get(bing_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract search result URLs
                result_count = 0
                
                # Look for different types of result links
                for link in soup.find_all('a', href=True)[:20]:
                    href = link.get('href')
                    text = link.get_text().strip()
                    
                    # Filter for AI-related URLs
                    if (href and href.startswith('http') and 
                        len(href) > 25 and
                        any(ai_indicator in href.lower() for ai_indicator in ['.ai', 'ai-', 'artificial', 'neural', 'generate', 'create']) and
                        not any(skip in href.lower() for skip in ['bing.com', 'microsoft.com', 'wikipedia', 'reddit.com/r/all'])):
                        
                        # Analyze this potential AI site
                        site_info = analyze_discovered_site(href, text)
                        if site_info and result_count < 3:  # Limit per query
                            discovered_sites.append(site_info)
                            result_count += 1
                            print(f"    ✨ Found: {site_info['title']}")
                
                time.sleep(random.uniform(4, 7))  # Random delay
                
            else:
                print(f"    ⚠️ Bing returned status {response.status_code}")
                
        except Exception as e:
            print(f"    ⚠️ Bing search error: {e}")
            time.sleep(5)
    
    print(f"  📊 Bing discovered: {len(discovered_sites)} sites")
    return discovered_sites

def search_alternative_sources():
    """Try alternative search methods"""
    print("🌐 Trying alternative discovery methods...")
    discovered_sites = []
    
    # Method 1: Try Searx instance
    try:
        print("  🔍 Trying Searx search engine...")
        searx_url = "https://searx.be/search"
        params = {
            'q': 'AI creative tool 2024',
            'categories': 'general',
            'language': 'en'
        }
        
        response = requests.get(searx_url, params=params, headers=get_rotating_headers(), timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for result links
            for link in soup.find_all('a', href=True)[:10]:
                href = link.get('href')
                if (href and href.startswith('http') and 
                    any(ai_word in href.lower() for ai_word in ['ai', 'artificial', 'neural', 'ml']) and
                    len(href) > 20):
                    
                    text = link.get_text().strip()
                    site_info = analyze_discovered_site(href, text)
                    if site_info:
                        discovered_sites.append(site_info)
                        print(f"    ✨ Searx found: {site_info['title']}")
        
        time.sleep(random.uniform(3, 6))
        
    except Exception as e:
        print(f"    ⚠️ Searx error: {e}")
    
    # Method 2: Check known AI directory sites for new listings
    try:
        print("  📊 Checking AI tool directories...")
        directory_sites = [
            "https://theresanaiforthat.com",
            "https://futurepedia.io", 
            "https://toolify.ai"
        ]
        
        for dir_site in directory_sites[:2]:  # Limit to avoid timeout
            try:
                response = requests.get(dir_site, headers=get_rotating_headers(), timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for external links to AI tools
                    for link in soup.find_all('a', href=True)[:15]:
                        href = link.get('href')
                        if (href and href.startswith('http') and 
                            dir_site not in href and  # External link
                            any(ai_indicator in href.lower() for ai_indicator in ['.ai', 'ai-', 'app', 'tool']) and
                            len(href) > 20):
                            
                            text = link.get_text().strip()
                            site_info = analyze_discovered_site(href, text)
                            if site_info:
                                discovered_sites.append(site_info)
                                print(f"    ✨ Directory found: {site_info['title']}")
                                break  # One per directory
                
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"    ⚠️ Directory {dir_site} error: {e}")
                
    except Exception as e:
        print(f"    ⚠️ Directory search error: {e}")
    
    # Method 3: Check GitHub for trending AI projects with demos
    try:
        print("  🐙 Checking GitHub trending...")
        github_url = "https://github.com/trending?l=python&since=weekly"
        
        response = requests.get(github_url, headers=get_rotating_headers(), timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for AI-related trending repos
            repo_links = soup.find_all('a', href=True)
            
            for link in repo_links[:8]:
                href = link.get('href')
                text = link.get_text().strip()
                
                if (href and href.startswith('/') and 
                    len(href.split('/')) >= 3 and
                    any(ai_word in text.lower() for ai_word in ['ai', 'artificial', 'neural', 'ml', 'generate', 'creative'])):
                    
                    repo_url = f"https://github.com{href}"
                    
                    # Quick check if repo has a demo/website link
                    try:
                        repo_response = requests.get(repo_url, headers=get_rotating_headers(), timeout=8)
                        if repo_response.status_code == 200:
                            repo_soup = BeautifulSoup(repo_response.content, 'html.parser')
                            
                            # Look for demo links
                            for demo_link in repo_soup.find_all('a', href=True)[:10]:
                                demo_href = demo_link.get('href')
                                demo_text = demo_link.get_text().strip().lower()
                                
                                if (demo_href and demo_href.startswith('http') and 
                                    'github.com' not in demo_href and
                                    any(demo_word in demo_text for demo_word in ['demo', 'try', 'app', 'website', 'live', 'playground'])):
                                    
                                    site_info = analyze_discovered_site(demo_href, f"[GitHub] {text}")
                                    if site_info:
                                        discovered_sites.append(site_info)
                                        print(f"    ✨ GitHub demo: {site_info['title']}")
                                        break
                        
                        time.sleep(random.uniform(2, 4))
                        
                    except:
                        continue
        
    except Exception as e:
        print(f"    ⚠️ GitHub trending error: {e}")
    
    print(f"  📊 Alternative sources discovered: {len(discovered_sites)} sites")
    return discovered_sites

def analyze_discovered_site(url, fallback_title=""):
    """Analyze a discovered site to create structured data"""
    try:
        print(f"    🔍 Analyzing: {url[:50]}...")
        
        # Add delay to be respectful
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=get_rotating_headers(), timeout=10)
        if response.status_code != 200:
            print(f"    ⚠️ Site returned {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text().strip() if title_elem else fallback_title
        title = re.sub(r'\s+', ' ', title)[:100]
        
        # Clean up common unhelpful titles
        if not title or title.lower() in ['', 'untitled', 'loading...', 'just a moment', 'please wait']:
            domain = urlparse(url).netloc.replace('www.', '')
            title = fallback_title or domain.replace('.com', '').replace('.ai', '').title()
        
        # Extract description
        description = ""
        
        # Try multiple meta description tags
        for meta_name in ['description', 'og:description', 'twitter:description']:
            meta_desc = soup.find('meta', attrs={'name': meta_name}) or soup.find('meta', attrs={'property': meta_name})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc.get('content', '')
                break
        
        # Fallback to first paragraph
        if not description:
            for p in soup.find_all('p')[:3]:
                p_text = p.get_text().strip()
                if len(p_text) > 30 and not any(skip in p_text.lower() for skip in ['cookie', 'privacy', 'terms']):
                    description = p_text[:200]
                    break
        
        # Clean description
        description = re.sub(r'\s+', ' ', description.strip())[:200] if description else "AI-powered creative tool discovered from web search"
        
        # Smart categorization
        content_text = f"{title} {description} {url}".lower()
        
        category = "creative"  # Default
        emoji = "🎨"
        tags = ["AI", "Web Discovered"]
        
        # Enhanced categorization
        if any(word in content_text for word in ['art', 'image', 'photo', 'visual', 'design', 'draw', 'paint', 'creative', 'generate']):
            category = "creative"
            emoji = random.choice(["🎨", "✨", "🖌️", "🎭", "🌈"])
            tags.extend(["Art", "Creative"])
            
        elif any(word in content_text for word in ['music', 'audio', 'voice', 'sound', 'sing', 'compose', 'beat']):
            category = "audio"
            emoji = random.choice(["🎵", "🎤", "🎧", "🔊", "🎶"])
            tags.extend(["Music", "Audio"])
            
        elif any(word in content_text for word in ['game', 'play', 'interactive', 'fun', 'quiz', 'adventure', 'rpg']):
            category = "games"
            emoji = random.choice(["🎮", "🎯", "🎲", "🎪", "🕹️"])
            tags.extend(["Game", "Interactive"])
            
        elif any(word in content_text for word in ['write', 'text', 'copy', 'content', 'article', 'blog', 'essay']):
            category = "ai-tools"
            emoji = random.choice(["✍️", "📝", "💬", "📄", "📖"])
            tags.extend(["Writing", "Text"])
            
        elif any(word in content_text for word in ['video', 'animation', 'movie', 'film', 'motion', 'clip']):
            category = "creative"
            emoji = random.choice(["🎬", "🎥", "📹", "🎞️", "✨"])
            tags.extend(["Video", "Animation"])
            
        elif any(word in content_text for word in ['chat', 'conversation', 'assistant', 'bot', 'talk', 'help']):
            category = "ai-tools"
            emoji = random.choice(["🤖", "💬", "🗣️", "💭", "⚡"])
            tags.extend(["Assistant", "Chat"])
            
        elif any(word in content_text for word in ['experiment', 'research', 'demo', 'test', 'lab', 'beta']):
            category = "experimental"
            emoji = random.choice(["🧪", "⚗️", "🔬", "🧬", "🌀"])
            tags.append("Experimental")
            
        elif any(word in content_text for word in ['weird', 'funny', 'humor', 'strange', 'quirky', 'bizarre']):
            category = "fun"
            emoji = random.choice(["😄", "🤪", "😂", "🎉", "🎭"])
            tags.append("Humor")
        
        # Add specific feature tags
        if any(word in content_text for word in ['generate', 'generator', 'creation', 'create']):
            tags.append("Generation")
        if any(word in content_text for word in ['free', 'open source', 'no cost']):
            tags.append("Free")
        if any(word in content_text for word in ['api', 'developer', 'code']):
            tags.append("API")
        
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
    print("🌐 No hardcoded sites - discovering fresh AI tools from live web search")
    print("🔍 Sources: Bing Search + Alternative Engines + AI Directories + GitHub Trending")
    
    # Get environment variables
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    
    if not all([GITHUB_TOKEN, GITHUB_REPO]):
        print("❌ Missing required environment variables")
        return
    
    # Initialize GitHub
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPO)
    
    print("\n🔍 Starting fresh web discovery...")
    all_discovered = []
    
    # Try Bing search
    try:
        bing_results = search_bing_for_ai_sites()
        all_discovered.extend(bing_results)
        time.sleep(random.uniform(5, 8))
    except Exception as e:
        print(f"⚠️ Bing search failed: {e}")
    
    # Try alternative sources
    try:
        alt_results = search_alternative_sources()
        all_discovered.extend(alt_results)
    except Exception as e:
        print(f"⚠️ Alternative search failed: {e}")
    
    # Remove duplicates
    seen_urls = set()
    unique_discovered = []
    for site in all_discovered:
        if site['link'] not in seen_urls:
            unique_discovered.append(site)
            seen_urls.add(site['link'])
    
    print(f"\n🎯 Total unique sites discovered from web: {len(unique_discovered)}")
    
    if not unique_discovered:
        print("🔍 No new sites discovered - search engines may be blocking or no new AI tools found")
        print("💡 This is normal - try running again later for fresh discoveries")
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
        print(f"\n🎉 DISCOVERED {len(new_sites)} FRESH AI SITES FROM THE WEB!")
        
        # Show breakdown
        categories = {}
        for site in new_sites:
            cat = site['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("📊 Fresh discoveries by category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} sites")
        
        # Add to collection
        all_sites = existing_sites + new_sites
        
        # Save to GitHub
        content = json.dumps(all_sites, indent=2, ensure_ascii=False)
        
        try:
            file = repo.get_contents("creative_discoveries.json")
            repo.update_file(
                path="creative_discoveries.json",
                message=f"🌐 Fresh web discovery: {len(new_sites)} new AI sites from live search - {datetime.now().strftime('%Y-%m-%d')}",
                content=content,
                sha=file.sha
            )
        except:
            repo.create_file(
                path="creative_discoveries.json",
                message=f"🌐 Create fresh web-discovered AI sites - {datetime.now().strftime('%Y-%m-%d')}",
                content=content
            )
        
        print(f"\n💾 Saved {len(new_sites)} fresh web discoveries to GitHub!")
        print(f"🎊 Total creative sites: {len(all_sites)}")
        
        # Show examples
        print(f"\n✨ Fresh discoveries from the web:")
        for site in new_sites:
            print(f"  {site['emoji']} {site['title']} - {site['category']}")
        
    else:
        print("🔍 All web-discovered sites already exist in collection")
        print("🔄 Web search found known sites - try again later for fresh discoveries")
    
    print("\n✅ Fresh web discovery complete!")

if __name__ == "__main__":
    main()