import os 
import json 
from datetime import datetime, timedelta, timezone
import requests
from google.cloud import storage
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(docs_url="/Docs", title="Get News", description="News API")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")



def load_tickers_from_bucket():
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("tickers.json")
    tickers_data = blob.download_as_text()
    return json.loads(tickers_data)

@app.post("/get_news/")
async def get_news():
    if not NEWSAPI_KEY:
        raise HTTPException(status_code=500, detail="NEWSAPI_KEY environment variable not set")
    
    tickers = load_tickers_from_bucket()
    results = {}

    # get news from yesterday to today, changed news api now we get latest news without paying 400 bucks
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    for ticker in tickers:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&RANGE={yesterday}&RANGE={today}&apikey={NEWSAPI_KEY}"
        response = requests.get(url)
        news_data = response.json() 
        
        filename = f"news/{ticker}_news_{datetime.now().strftime('%Y%m%d%H%M%S')}.json" 
        client = storage.Client() 
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{filename}")
        blob.upload_from_string(json.dumps(news_data), content_type="application/json")

        results[ticker] = {"message": f"News data for {ticker} saved to {filename}"}
    
    return JSONResponse(content=results)


