#!/usr/bin/env python3
"""
Simplified Creative AI Web Discovery Agent
Focuses on creative, quirky, and experimental AI websites
Outputs in structured JSON format
"""

import os
import json
from datetime import datetime
from github import Github
import base64

def main():
    print("🚀 Creative AI Discovery Agent Starting...")
    
    # Get environment variables
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    
    if not all([GITHUB_TOKEN, GITHUB_REPO]):
        print("❌ Missing required environment variables")
        return
    
    # Initialize GitHub
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPO)
    
    print("🎨 Starting Creative AI Website Discovery...")
    
    # Creative AI sites collection
    creative_sites = [
        {
            "title": "This Person Does Not Exist",
            "description": "AI-generated faces of people who don't actually exist using StyleGAN neural networks",
            "link": "https://thispersondoesnotexist.com",
            "category": "ai-tools",
            "emoji": "👤",
            "tags": ["AI", "Faces", "Neural Networks"]
        },
        {
            "title": "Artbreeder",
            "description": "Collaborative AI art tool that lets you create and explore images using GANs",
            "link": "https://artbreeder.com",
            "category": "creative",
            "emoji": "🎨",
            "tags": ["AI", "Art", "Collaborative"]
        },
        {
            "title": "AI Weirdness",
            "description": "Blog showcasing hilarious and bizarre results when AI tries to understand human things",
            "link": "https://aiweirdness.com",
            "category": "fun",
            "emoji": "🤪",
            "tags": ["AI", "Humor", "Blog"]
        },
        {
            "title": "Deep Dream Generator",
            "description": "Generate surreal, dream-like images using advanced neural networks",
            "link": "https://deepdreamgenerator.com",
            "category": "creative",
            "emoji": "🌌",
            "tags": ["AI", "Art", "Dreams"]
        },
        {
            "title": "Quick, Draw!",
            "description": "Google's AI experiment that challenges you to draw while a neural network guesses",
            "link": "https://quickdraw.withgoogle.com",
            "category": "games",
            "emoji": "✏️",
            "tags": ["AI", "Drawing", "Game"]
        },
        {
            "title": "Blob Opera",
            "description": "Create opera harmonies by dragging adorable blob voices",
            "link": "https://blobopera.io",
            "category": "creative",
            "emoji": "🎶",
            "tags": ["Music", "Interactive", "Fun"]
        },
        {
            "title": "InspiroBot",
            "description": "AI-generated motivational quotes with a twist - usually absurd or darkly funny",
            "link": "https://inspirobot.me",
            "category": "fun",
            "emoji": "💡",
            "tags": ["AI", "Quotes", "Humor"]
        },
        {
            "title": "Character.AI",
            "description": "Chat with AI characters and personalities - create conversations with anyone",
            "link": "https://character.ai",
            "category": "ai-tools",
            "emoji": "🗣️",
            "tags": ["AI", "Chatbot", "Roleplay"]
        },
        {
            "title": "This Word Does Not Exist",
            "description": "AI generates fake words that sound real, complete with definitions",
            "link": "https://thisworddoesnotexist.com",
            "category": "fun",
            "emoji": "📝",
            "tags": ["AI", "Language", "Words"]
        },
        {
            "title": "AutoDraw",
            "description": "Doodle freely and watch AI suggest polished clipart versions of your sketches",
            "link": "https://autodraw.com",
            "category": "ai-tools",
            "emoji": "✏️",
            "tags": ["AI", "Drawing", "Tools"]
        },
        {
            "title": "Remove.bg",
            "description": "AI-powered background removal tool that creates perfect cutouts in seconds",
            "link": "https://remove.bg",
            "category": "ai-tools",
            "emoji": "🖼️",
            "tags": ["AI", "Images", "Tools"]
        },
        {
            "title": "Craiyon",
            "description": "Type a prompt and get quirky AI art in seconds - formerly DALL-E Mini",
            "link": "https://craiyon.com",
            "category": "creative",
            "emoji": "🖌️",
            "tags": ["AI", "Art", "Text to Image"]
        }
    ]
    
    print(f"✨ Found {len(creative_sites)} creative AI sites!")
    
    # Load existing data
    existing_sites = []
    try:
        file = repo.get_contents("creative_discoveries.json")
        content = base64.b64decode(file.content).decode('utf-8')
        existing_sites = json.loads(content)
        print(f"📚 Loaded {len(existing_sites)} existing sites")
    except:
        print("📝 Creating new creative discoveries file")
    
    # Check for new sites
    existing_urls = {site.get('link', '') for site in existing_sites}
    new_sites = [site for site in creative_sites if site['link'] not in existing_urls]
    
    if new_sites:
        # Add new sites
        all_sites = existing_sites + new_sites
        
        # Save to GitHub
        content = json.dumps(all_sites, indent=2, ensure_ascii=False)
        
        try:
            file = repo.get_contents("creative_discoveries.json")
            repo.update_file(
                path="creative_discoveries.json",
                message=f"Add {len(new_sites)} creative AI sites - {datetime.now().strftime('%Y-%m-%d')}",
                content=content,
                sha=file.sha
            )
        except:
            repo.create_file(
                path="creative_discoveries.json",
                message=f"Create creative AI discoveries - {datetime.now().strftime('%Y-%m-%d')}",
                content=content
            )
        
        print(f"💾 Saved {len(new_sites)} new creative sites to GitHub!")
        print(f"🎉 Total creative sites: {len(all_sites)}")
    else:
        print("📋 All sites already exist - no new discoveries today!")
    
    print("✅ Creative discovery complete!")

if __name__ == "__main__":
    main()