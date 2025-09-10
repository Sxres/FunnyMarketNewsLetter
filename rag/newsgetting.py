from newspaper import Article
import nltk
nltk.download('punkt_tab')

urls = ["https://biztoc.com/x/6f2461e3d79ccc09", 
        "https://finance.yahoo.com/news/tesla-tsla-entry-india-sees-142931553.html", 
        "https://finance.yahoo.com/news/tesla-stock-nasdaq-tsla-faces-040724978.html", 
        "http://electrek.co/2025/09/08/tesla-tsla-us-market-share-ev-market-drop-new-lows/", 
        "https://finance.yahoo.com/news/why-soundhound-ai-soun-stock-182613993.html",
        "https://finance.yahoo.com/news/why-rocket-lab-rklb-stock-182639864.html",
        "https://biztoc.com/x/f641c289149dcfc7",
        "https://biztoc.com/x/a451abb732892338",
        "https://biztoc.com/x/5d2cd09fad7d0633",
        "https://www.etfdailynews.com/2025/09/07/northwest-quadrant-wealth-management-llc-reduces-stock-holdings-in-apple-inc-aapl/",
        "https://www.etfdailynews.com/2025/09/07/apple-inc-aapl-shares-sold-by-wittenberg-investment-management-inc/",
        "https://www.etfdailynews.com/2025/09/07/apple-inc-aapl-position-increased-by-mitsubishi-ufj-asset-management-co-ltd/"
        ]



with open('news_summaries.txt', 'w', encoding='utf-8') as file:
    for url in urls:  
        news = Article(url)
        news.download()
        news.parse()
        news.nlp()
        summary = news.summary
        
    
        file.write(f"{summary}\n")
         