import os 
import json 
from datetime import datetime, timedelta
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

    # calculate date 24 hours ago
    yesterday = datetime.now() - timedelta(days=2)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    for ticker in tickers:
        url = f"https://newsapi.org/v2/everything?q={ticker}&from={yesterday_str}&to={datetime.now().strftime('%Y-%m-%d')}&Language=en&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
        response = requests.get(url)
        news_data = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching news data")
        if news_data.get("status") != "ok":
            raise HTTPException(status_code=500, detail="Error in news data response")

        filename = f"news/{ticker}_news_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{filename}")
        blob.upload_from_string(json.dumps(news_data), content_type="application/json")

        results[ticker] = {"message": f"News data for {ticker} saved to {filename}"}
    
    return JSONResponse(content=results)


