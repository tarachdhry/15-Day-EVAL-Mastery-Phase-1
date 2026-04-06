# File: stripe_scraper.py
"""
Stripe Documentation Scraper
Extracts content from Stripe's public docs for RAG system
"""

import requests
from bs4 import BeautifulSoup
import json
import time

class StripeScraper:
    """Scrape Stripe documentation"""
    
    def __init__(self):
        self.base_url = "https://stripe.com/docs"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Educational RAG Project)'
        }
        self.documents = []
    
    def scrape_page(self, url: str, category: str) -> dict:
        """
        Scrape a single Stripe doc page
        
        WHAT THIS DOES:
        1. Sends HTTP GET request to URL
        2. Parses HTML with BeautifulSoup
        3. Extracts main content text
        4. Returns structured document
        
        Args:
            url: Full URL to scrape
            category: Topic category (e.g., "payments", "refunds")
        
        Returns:
            Dict with doc_id, category, content, url
        """
        print(f"📄 Scraping: {url}")
        
        try:
            # Get the page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise error if request failed
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1')
            title = title_tag.get_text().strip() if title_tag else "Untitled"
            
            # Extract main content
            # Stripe uses <article> or <main> tags for content
            content_tag = soup.find('article') or soup.find('main')
            
            if content_tag:
                # Remove navigation, code examples (keep text only for now)
                for tag in content_tag.find_all(['nav', 'aside']):
                    tag.decompose()
                
                content = content_tag.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)
            
            # Clean up content (remove excess whitespace)
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            # Create document
            doc = {
                'doc_id': url.split('/')[-1],  # Use last part of URL as ID
                'category': category,
                'title': title,
                'content': content[:5000],  # Limit to first 5000 chars
                'url': url
            }
            
            return doc
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def scrape_stripe_docs(self):
        """
        Scrape key Stripe documentation pages
        
        STRATEGY:
        - Manually curated list of important pages
        - Covers main customer support topics
        - ~15-20 pages (good for learning, not overwhelming)
        """
        
        # Pages to scrape (carefully selected)
        pages = [
            # Payment Intents (core payment flow)
            ("https://stripe.com/docs/payments/payment-intents", "payments"),
            ("https://stripe.com/docs/payments/accept-a-payment", "payments"),
            
            # Refunds
            ("https://stripe.com/docs/refunds", "refunds"),
            
            # Webhooks
            ("https://stripe.com/docs/webhooks", "webhooks"),
            ("https://stripe.com/docs/webhooks/best-practices", "webhooks"),
            
            # Subscriptions
            ("https://stripe.com/docs/billing/subscriptions/overview", "subscriptions"),
            ("https://stripe.com/docs/billing/subscriptions/creating", "subscriptions"),
            
            # Disputes/Chargebacks
            ("https://stripe.com/docs/disputes", "disputes"),
            
            # Testing
            ("https://stripe.com/docs/testing", "testing"),
            
            # API Keys
            ("https://stripe.com/docs/keys", "authentication"),
            
            # Errors
            ("https://stripe.com/docs/error-handling", "errors"),
            
            # Checkout
            ("https://stripe.com/docs/payments/checkout", "checkout"),
        ]
        
        print(f"🚀 Starting Stripe documentation scrape...")
        print(f"📋 {len(pages)} pages to scrape\n")
        
        for url, category in pages:
            doc = self.scrape_page(url, category)
            
            if doc:
                self.documents.append(doc)
                print(f"✅ Scraped: {doc['title']}\n")
            
            # Be polite - don't hammer their server
            time.sleep(2)  # 2 second delay between requests
        
        print(f"\n✅ Scraping complete! Collected {len(self.documents)} documents")
        
        return self.documents
    
    def save_to_file(self, filename: str = "stripe_knowledge_base.json"):
        """Save scraped documents to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to {filename}")
    
    def print_summary(self):
        """Print summary of scraped content"""
        print("\n" + "="*60)
        print("📊 SCRAPING SUMMARY")
        print("="*60)
        
        print(f"\nTotal documents: {len(self.documents)}")
        
        # Count by category
        categories = {}
        for doc in self.documents:
            cat = doc['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nBy category:")
        for cat, count in sorted(categories.items()):
            print(f"  - {cat}: {count} docs")
        
        print(f"\n📄 Sample document:")
        if self.documents:
            sample = self.documents[0]
            print(f"  Title: {sample['title']}")
            print(f"  Category: {sample['category']}")
            print(f"  Content preview: {sample['content'][:200]}...")
            print(f"  URL: {sample['url']}")


def main():
    """Run the scraper"""
    scraper = StripeScraper()
    
    # Scrape
    docs = scraper.scrape_stripe_docs()
    
    # Save
    scraper.save_to_file()
    
    # Summary
    scraper.print_summary()


if __name__ == "__main__":
    main()
