import os
import requests
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

app = FastAPI()

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Question(BaseModel):
    question: str
    source: str

# Function to query OpenAI API
async def ask_openai(question: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": question}],
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        logging.info("OpenAI API successfully returned a response.")
        return {
            "answer": response.json()["choices"][0]["message"]["content"].strip(),
            "source": "OpenAI",
        }
    else:
        logging.error(f"OpenAI API error: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail="OpenAI API error.")

# Function to scrape web page content
def scrape_content(url: str):
    try:
        logging.info(f"Scraping content from {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.content, 'lxml')
        paragraphs = soup.find_all('p')
        content = ' '.join(p.get_text() for p in paragraphs)
        logging.info(f"Scraped content length: {len(content)} characters")
        return content
    except Exception as e:
        logging.error(f"Error scraping {url}: {str(e)}")
        return ""

# Function to summarize text using OpenAI
async def summarize_text(text: str, query:str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": f"{query} from this paragraph:\n{text}"}],
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        logging.info("Successfully summarized the text using OpenAI.")
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        logging.error(f"OpenAI API error while summarizing: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail="OpenAI API error while summarizing.")

# Function to query Google Custom Search
async def search_google(query: str):
    logging.info(f"Searching Google for: {query}")
    response = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params={"key": GOOGLE_API_KEY, "cx": GOOGLE_CX_ID, "q": query},
    )
    
    if response.status_code == 200:
        results = response.json().get("items", [])
        
        if not results:
            logging.warning("No results found on Google.")
            return {"snippets": "No results found.", "source": "Google"}

        scraped_contents = []
        result_count = 0

        for result in results[:10]:  # Limit to the first 10 results
            first_result_url = result['link']
            # Check if the result is a PDF
            if not first_result_url.casefold().endswith('.pdf'):
                # Scrape content if it's not a PDF
                scraped_content = scrape_content(first_result_url)
                if scraped_content:
                    scraped_contents.append(scraped_content)
                    result_count += 1

            if result_count >= 10:
                break

        if not scraped_contents:
            return {"snippets": "All results were PDF files, no content could be scraped.", "source": "Google"}

        # Concatenate all scraped contents for summarization
        combined_text = " ".join(scraped_contents[:10])  # Limit text for better performance

        # Summarize the combined text
        summary = await summarize_text(combined_text,query )
        return {
            "summary": summary,
            "source": "Google",
        }
    else:
        logging.error(f"Google Search API error: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail="Google Search API error.")

# Main route to handle the question
@app.post("/ask")
async def ask_question(question: Question):
    if question.source == "OpenAI":
        return await ask_openai(question.question)
    elif question.source == "Google":
        return await search_google(question.question)
    elif question.source == "Gemini":
        logging.info("Querying Gemini API.")
        return await ask_gemini(question.question)  # Assuming you have implemented this function
    else:
        logging.error("Invalid source specified.")
        raise HTTPException(status_code=400, detail="Invalid source specified. Use 'OpenAI', 'Google', or 'Gemini'.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
