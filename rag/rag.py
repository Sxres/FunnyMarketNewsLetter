from newspaper import Article
import nltk
nltk.download('punkt_tab')
url = "https://www.etfdailynews.com/2025/09/06/ritter-daniher-financial-advisory-llc-de-has-432000-holdings-in-nvidia-corporation-nvda/"
article = Article(url)
article.download()
article.parse()
article.nlp()

print("Summary\n", article.summary)


