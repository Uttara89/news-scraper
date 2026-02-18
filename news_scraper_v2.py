"""
AI-Powered News Scraper v2.0
Now using RSS feeds for more reliable data collection
"""

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import xml.etree.ElementTree as ET

# Your keywords for filtering
KEYWORDS = [
    "AI", "Artificial Intelligence", "Machine Learning", "ML",
    "India", "Indian", "BJP", "Congress", "Election", "Politics",
    "CFA", "Chartered Financial Analyst", "Finance", "Financial",
    "Automation", "RPA", "Automate",
    "Financial Modeling", "Valuation", "DCF", "Investment"
]

# Convert keywords to lowercase for case-insensitive matching
KEYWORDS_LOWER = [k.lower() for k in KEYWORDS]


def check_keywords(text):
    """Check if text contains any of our keywords"""
    if not text:
        return False
    text_lower = text.lower()
    for keyword in KEYWORDS_LOWER:
        if keyword in text_lower:
            return True
    return False


def get_matched_keywords(text):
    """Get list of matched keywords in text"""
    if not text:
        return 'General Match'
    matched = []
    text_lower = text.lower()
    
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    
    return ', '.join(matched[:3]) if matched else 'General Match'  # Limit to 3 keywords


def scrape_rss_feed(feed_url, source_name):
    """Generic RSS feed scraper"""
    print(f"Scraping {source_name} RSS feed...")
    articles = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse RSS/Atom feed
        root = ET.fromstring(response.content)
        
        # Check if it's RSS or Atom
        if root.tag == '{http://www.w3.org/2005/Atom}feed':
            # Atom feed
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            for entry in entries[:20]:
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                
                if title_elem is not None:
                    title = title_elem.text
                    link = link_elem.get('href') if link_elem is not None else ""
                    
                    if check_keywords(title):
                        articles.append({
                            'source': source_name,
                            'title': title,
                            'link': link,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'matched_keywords': get_matched_keywords(title)
                        })
        else:
            # RSS feed
            items = root.findall('.//item')
            for item in items[:20]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                description_elem = item.find('description')
                
                if title_elem is not None:
                    title = title_elem.text
                    link = link_elem.text if link_elem is not None else ""
                    description = description_elem.text if description_elem is not None else ""
                    
                    # Check title and description
                    combined_text = f"{title} {description}"
                    if check_keywords(combined_text):
                        articles.append({
                            'source': source_name,
                            'title': title,
                            'link': link,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'matched_keywords': get_matched_keywords(combined_text)
                        })
        
        print(f"✅ Found {len(articles)} relevant articles from {source_name}")
        
    except requests.RequestException as e:
        print(f"❌ Network error scraping {source_name}: {e}")
    except ET.ParseError as e:
        print(f"❌ Parse error for {source_name}: {e}")
    except Exception as e:
        print(f"❌ Unexpected error scraping {source_name}: {e}")
    
    return articles


def scrape_techcrunch_rss():
    """Scrape TechCrunch RSS feed"""
    return scrape_rss_feed(
        'https://techcrunch.com/feed/',
        'TechCrunch'
    )


def scrape_google_news_rss(topic):
    """Scrape Google News RSS for specific topic"""
    # Google News RSS URLs
    topic_urls = {
        'technology': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
        'business': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB',
        'india': 'https://news.google.com/rss/search?q=india&hl=en-IN&gl=IN&ceid=IN:en',
        'finance': 'https://news.google.com/rss/search?q=finance&hl=en-IN&gl=IN&ceid=IN:en',
    }
    
    url = topic_urls.get(topic, f'https://news.google.com/rss/search?q={topic}&hl=en-IN&gl=IN&ceid=IN:en')
    return scrape_rss_feed(url, f'Google News ({topic})')


def scrape_bbc_rss():
    """Scrape BBC News RSS"""
    return scrape_rss_feed(
        'http://feeds.bbci.co.uk/news/rss.xml',
        'BBC News'
    )


def scrape_reuters_rss():
    """Scrape Reuters RSS"""
    return scrape_rss_feed(
        'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'Reuters'
    )


def scrape_economic_times_rss():
    """Scrape Economic Times RSS"""
    return scrape_rss_feed(
        'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'Economic Times'
    )


def scrape_hindu_rss():
    """Scrape The Hindu RSS"""
    return scrape_rss_feed(
        'https://www.thehindu.com/news/national/feeder/default.rss',
        'The Hindu'
    )


def scrape_newslaundry_direct():
    """Direct scrape NewsLaundry (no RSS available)"""
    print("Scraping NewsLaundry...")
    articles = []
    
    try:
        url = "https://www.newslaundry.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors
        article_elements = (
            soup.find_all('h2', limit=20) + 
            soup.find_all('h3', limit=20) +
            soup.find_all('a', class_=lambda x: x and 'article' in x.lower(), limit=20)
        )
        
        for element in article_elements:
            try:
                # Try to extract title and link
                if element.name in ['h2', 'h3']:
                    link_tag = element.find('a')
                    if link_tag:
                        title = link_tag.get_text(strip=True) or element.get_text(strip=True)
                        link = link_tag.get('href', '')
                    else:
                        title = element.get_text(strip=True)
                        link = ''
                else:
                    title = element.get_text(strip=True)
                    link = element.get('href', '')
                
                if not title or len(title) < 10:
                    continue
                
                if link and not link.startswith('http'):
                    link = 'https://www.newslaundry.com' + link
                
                if check_keywords(title):
                    articles.append({
                        'source': 'NewsLaundry',
                        'title': title,
                        'link': link,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'matched_keywords': get_matched_keywords(title)
                    })
            except Exception as e:
                continue
        
        # Remove duplicates
        seen = set()
        unique_articles = []
        for article in articles:
            if article['title'] not in seen:
                seen.add(article['title'])
                unique_articles.append(article)
        
        print(f"✅ Found {len(unique_articles)} relevant articles from NewsLaundry")
        return unique_articles
                
    except Exception as e:
        print(f"❌ Error scraping NewsLaundry: {e}")
        return []


def save_to_csv(articles, filename=None):
    """Save articles to CSV file"""
    if not filename:
        filename = f"news_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if not articles:
        print("⚠️  No articles to save!")
        return None
    
    # Define CSV columns
    fieldnames = ['source', 'title', 'link', 'date', 'matched_keywords']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"\n✅ Saved {len(articles)} articles to {filename}")
    return filename


def main():
    """Main function to run the scraper"""
    print("=" * 60)
    print("🤖 AI News Scraper v2.0 Starting...")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Keywords: {', '.join(KEYWORDS[:8])}...")
    print("=" * 60)
    print("\n📡 Using RSS feeds for reliable data collection\n")
    
    all_articles = []
    
    # Scrape TechCrunch RSS
    all_articles.extend(scrape_techcrunch_rss())
    time.sleep(1)
    
    # Scrape Google News (multiple topics)
    all_articles.extend(scrape_google_news_rss('india'))
    time.sleep(1)
    
    all_articles.extend(scrape_google_news_rss('finance'))
    time.sleep(1)
    
    all_articles.extend(scrape_google_news_rss('technology'))
    time.sleep(1)
    
    # Scrape Indian news sources
    all_articles.extend(scrape_economic_times_rss())
    time.sleep(1)
    
    all_articles.extend(scrape_hindu_rss())
    time.sleep(1)
    
    # Scrape international sources
    all_articles.extend(scrape_bbc_rss())
    time.sleep(1)
    
    all_articles.extend(scrape_reuters_rss())
    time.sleep(1)
    
    # Scrape NewsLaundry (direct scraping)
    all_articles.extend(scrape_newslaundry_direct())
    
    # Remove duplicates based on title
    seen_titles = set()
    unique_articles = []
    
    for article in all_articles:
        title_lower = article['title'].lower().strip()
        if title_lower not in seen_titles and len(title_lower) > 10:
            seen_titles.add(title_lower)
            unique_articles.append(article)
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: Found {len(unique_articles)} unique articles")
    print("=" * 60)
    
    # Show breakdown by source
    sources = {}
    for article in unique_articles:
        source = article['source']
        sources[source] = sources.get(source, 0) + 1
    
    print("\n📈 Articles by source:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"   {source}: {count}")
    
    # Save to CSV
    if unique_articles:
        filename = save_to_csv(unique_articles)
        print(f"\n💾 File saved: {filename}")
        print(f"📂 Location: {os.path.abspath(filename)}")
    else:
        print("\n⚠️  No articles matched your keywords today.")
        print("💡 Try broadening your keywords or check back tomorrow!")
    
    print("\n✨ Scraping complete!")
    return unique_articles


if __name__ == "__main__":
    import os
    main()
