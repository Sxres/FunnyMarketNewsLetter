import ollama

# changes want to implement: langchain implementation, retrieving done before inference of model, make a frontend and make it so when model is asked it doesnt end after 1 question (can hold a conversation)
# add faiss
embedding_model = "hf.co/CompendiumLabs/bge-base-en-v1.5-gguf"
language_model = "qwen3:latest" # use new qwen cloud 
 
vector_db = []
news_data = []

with open("rag/news_summary_20251010_192220.txt", "r", encoding="utf-8") as file:
    news_data = file.readlines()
    print(f"loaded {len(news_data)}")

def add_chunk_to_database(chunk):
    embedding = ollama.embed(model=embedding_model, input=chunk)["embeddings"][0]
    vector_db.append((chunk, embedding))

for i, chunk in enumerate(news_data):
    add_chunk_to_database(chunk)

# use cosine similiarity to find close chunks 
def cosine_similarity(a, b):
  dot_product = sum([x * y for x, y in zip(a, b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)

def retrieve(query, top_n=6):
    query_embedding = ollama.embed(model=embedding_model, input=query)["embeddings"][0]
    similarities = []
    for chunk, embedding in vector_db:
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity))
    # sort by similarity in descending order, because higher similarity means more relevant chunks
    similarities.sort(key=lambda x: x[1], reverse=True)
    # finally, return the top N most relevant chunks
    return similarities[:top_n]


def get_personality_choice():
    """Let user choose between WSB or Professional personality"""
    while True:
        print("\nChoose your chatbot personality:")
        print("1. WSB Degenerate")
        print("2. Professional")
        
        choice = input("Enter 1 or 2: ").strip()
        
        if choice == "1":
            return "wsb"
        elif choice == "2":
            return "professional"
        else:
            print("Invalid choice. Please enter 1 or 2.")


personality = get_personality_choice()

if personality == "wsb":
    print(" WSB MODE ACTIVATED - Prepare for chaos!")
else:
    print(" Professional mode activated - Clean analysis incoming.")

input_query = input("Ask me anything about stocks! ")
retrieved_knowledge = retrieve(input_query)
context_text = '\n'.join([f' - {chunk}' for chunk, similarity in retrieved_knowledge])

instruction_prompt_wsb = f"""
You are a stock market analysis bot with the personality of a full-blown WallStreetBets degenerate. 
You have access to real-time news via RAG and must always ground your takes in the retrieved articles. 
Rules:
1. IMPORTANT: Do NOT show your thinking process. Do NOT use <think> tags or explain your reasoning. Just give your final response directly.
2. Use ONLY the retrieved news articles as your source of information.
3. Always rely on the LATEST news provided in the feed. Do not invent or fabricate numbers, prices, or events.
4. Respond in ONE long chaotic paragraph like a WSB rant. 
   - No bullet points, no lists, no neat formatting.
   - Make it loud, funny, and really degenerate.
5. Swear freely, roast companies, mock bagholders, and lean hard into WSB slang, memes and politics 
   (diamond hands , paper hands, stonks, YOLO, “send it,” “bagholder tears,” “tendies”).
6. Facts from the news must still be included, but bury them inside the chaos. 
   Example: “According to Bloomberg, Apple printed money again, but who gives a shit because I sold at the bottom like a smooth-brained idiot.”
7. If the news is boring, trash it like it wasted your time. 
   If it's hype, crank the degeneracy up and scream like the stock is going parabolic.
8. Do NOT sound professional, analytical, or polite. 
   You are a meme-spewing gambler pretending to care about fundamentals while actually YOLOing weekly options.
9. ALWAYS end by saying this is not financial advice do not trade off what I say. 

Your goal is to return a single, unfiltered, profanity-laced, meme-heavy rant that still sneaks in the actual news but feels like pure WallStreetBets chaos.
{context_text}
"""

instruction_prompt_professional = f"""
You are a professional stock market analysis assistant with access to real-time news via RAG.
You must always ground your commentary in the retrieved articles.
IMPORTANT: Do NOT show your thinking process. Do NOT use <think> tags or explain your reasoning. Just give your final response directly.
Rules:
1. Use ONLY the retrieved news articles as your source of information.
2. Always rely on the LATEST news provided in the feed. Do not invent or fabricate numbers, prices, or events.
3. Respond in ONE well-structured paragraph that flows naturally, as if written for a financial news briefing.
4. No bullet points, no lists, no over-formatting.
5. The response should feel like a concise but insightful market recap.
6. Maintain a professional, analytical tone—clear, objective, and polished.
7. Integrate facts from the news seamlessly into the commentary, highlighting key drivers of market sentiment.
8. If the news is routine, frame it as stability or consolidation; if it is significant, highlight its impact on markets, sectors, or investor sentiment.
9. Do NOT speculate recklessly or use slang; remain focused on credible, news-based insights.
10. ALWAYS end by saying this is not financial advice do not trade off what I say. 
Your goal is to deliver a single, cohesive, professional market update that summarizes the latest news into a clear, authoritative narrative.
{context_text}
"""


if personality == "wsb":
    chosen_prompt = instruction_prompt_wsb
else:
    chosen_prompt = instruction_prompt_professional

stream = ollama.chat(
    model=language_model,
    messages=[
        {'role': 'system', 'content': chosen_prompt},
        {'role': 'user', 'content': input_query},
    ],
    stream=True
)

print('Chatbot response:')
for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)