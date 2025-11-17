import chromadb 
import os 
import json
import requests 
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import asyncio
from newspaper import Article
import nltk

# Download required NLTK data
nltk.download('punkt_tab', quiet=True)

load_dotenv()

# create class to do newsprocessing
class newsprocessing:
    def __init__(self):
        self.news_api_key = os.getenv("NEWSAPI_KEY")
        self.vector_db = chromadb.Client()
        self.collection = self.vector_db.get_or_create_collection("market_news")
        self.all_summaries = []  # Track all summaries

    def load_tickers(self):
        return ["AAPL", "TSLA", "GOOG", "MSFT", "LUNR", "NVDA", "CMG", "BBAI", "INTC", "AMD",]
    
    def fetch_news(self, ticker, start_date, end_date):
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&RANGE={start_date}&RANGE={end_date}&apikey={self.news_api_key}"
        response = requests.get(url)
        return response.json()

    async def fetch_and_process_news(self):
        tickers = self.load_tickers()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
        
        print(f" Starting news processing for {len(tickers)} tickers: {', '.join(tickers)}")
        print(f" Date range: {yesterday} to {today}")
        print("-" * 60)
        
        task = [self.process_tickers(ticker, yesterday, today) for ticker in tickers]
        await asyncio.gather(*task)

    async def process_tickers(self, ticker, start_date, end_date):
        print(f" Fetching news for {ticker}...")
        news_data = self.fetch_news(ticker, start_date, end_date)
        
        if not news_data.get("feed"):
            print(f" No news found for {ticker}")
            return
            
        articles = news_data["feed"]
        print(f" Found {len(articles)} articles for {ticker}")
        
        for i, article in enumerate(articles, 1):
            title = article.get("title", "")[:80] + "..." if len(article.get("title", "")) > 80 else article.get("title", "")
            print(f"   [{ticker}] Processing article {i}/{len(articles)}: {title}")
            
            cleaned_article = self.cleaning(article)
            await self.store_in_db(cleaned_article, ticker)
            
            # Add summary to our collection for the text file
            if cleaned_article['content']:
                summary_entry = f"[{ticker}] {cleaned_article['title']}: {cleaned_article['content']}"
                self.all_summaries.append(summary_entry)
            
            print(f" Stored article {i}/{len(articles)} for {ticker}")
        
        print(f"🎉 Completed processing {len(articles)} articles for {ticker}")
        print("-" * 40)

    def extract_article_content(self, url):
        """Extract article content using newspaper3k"""
        try:
            print(f" Processing with newspaper3k: {url[:60]}...")
            
            news = Article(url)
            news.download()
            news.parse()
            news.nlp()
            
            content = news.summary if news.summary else news.text[:1000]
            print(f" Extracted {len(content)} characters")
            
            return {
                'content': content,
                'full_text': news.text[:2000] if news.text else "",
                'authors': news.authors,
                'publish_date': news.publish_date
            }
            
        except Exception as e:
            print(f" newspaper3k extraction failed: {e}")
            return None
            
    def cleaning(self, article):
        # Get the full article content using newspaper3k
        article_url = article.get("url", "")
        extracted_data = self.extract_article_content(article_url) if article_url else None
        
        # Use extracted content or fallback to original summary
        content = extracted_data['content'] if extracted_data else article.get("summary", "")
        full_text = extracted_data['full_text'] if extracted_data else ""
        
        return {
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "content": content,
            "full_content": full_text,
            "sentiment": article.get("overall_sentiment_score", 0),
            "published": article.get("time_published", ""),
            "source": article.get("source", ""),
            "url": article_url,
            "authors": extracted_data['authors'] if extracted_data else [],
            "extracted_date": str(extracted_data['publish_date']) if extracted_data and extracted_data['publish_date'] else ""
        }
    
    async def store_in_db(self, article, ticker):
        embedding_text = f"{article['title']} {article['content']}"
        self.collection.add(
            documents=[embedding_text],
            metadatas=[
                {
                    "ticker": ticker,
                    "sentiment": article["sentiment"],
                    "published": article["published"],
                    "source": article["source"],
                    "url": article.get("url", ""),
                    "authors": str(article.get("authors", []))
                }
            ],
            ids=[f"{ticker}_{article['published']}_{hash(article['title'])}"]
        )
    
    def save_summaries_to_file(self):
        """Save all summaries to a text file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"news_summary_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"News Summaries - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for summary in self.all_summaries:
                    f.write(summary + "\n\n")
                    
            print(f" Saved {len(self.all_summaries)} summaries to {filename}")
            return filename
            
        except Exception as e:
            print(f" Error saving summaries: {e}")
            return None
    
async def main():
    start_time = datetime.now()
    print(f" Starting at {start_time.strftime('%H:%M:%S')}")
    
    process = newsprocessing()
    await process.fetch_and_process_news()
    
    # Save summaries to text file
    summary_file = process.save_summaries_to_file()
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f" News processing complete!")
    print(f" Total time: {duration}")
    if summary_file:
        print(f" Summary file: {summary_file}")
    
if __name__ == "__main__":
    asyncio.run(main())