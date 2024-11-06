# AI-Powered Scraper with OpenAI and Google Custom Search

## Overview

This project is an AI-powered web scraping and query refinement tool that leverages OpenAI's GPT-4 model and Google Custom Search API. The core functionality involves breaking down a user's query into multiple sub-questions, gathering data from OpenAI or scraping web content from Google Search results, and providing a summarized response based on the gathered information.

### Key Features

1. **OpenAI GPT-4 Integration**: Queries OpenAI to generate human-like responses to complex questions.
2. **Google Custom Search**: Uses the Google Custom Search API to retrieve relevant web pages for specific queries and scrapes the content.
3. **Web Scraper**: Scrapes content from web pages and summarizes it using OpenAI to provide concise answers.
4. **Retry Logic**: Implements exponential backoff to handle rate-limiting (HTTP 429) from the Google Custom Search API.

### Core Concept

- The user submits a question, and based on the specified source (`OpenAI`, `Google`, or `Gemini`), the system processes the question accordingly.
- If **OpenAI** is selected, the question is sent directly to OpenAI's GPT-4 model, and the AI generates an answer.
- If **Google** is chosen, the system sends the question to Google Custom Search API to fetch web search results. It then scrapes the content of those web pages and summarizes it using OpenAI.
- The application also includes retry logic for Google API requests, handling the 429 error (Too Many Requests) by retrying with exponential backoff.

---

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)

## Requirements

- Python 3.8+
- FastAPI
- `requests` library
- `BeautifulSoup` for web scraping
- OpenAI API Key
- Google Custom Search API Key
- Uvicorn for running the FastAPI server

## Setup

1. Clone the repository:

```bash
git clone https://github.com/RuberDucky/AI-Powered-Scraper.git
cd AI-Powered-Scraper
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables by creating a `.env` file:

```bash
touch .env
```

4. Add the following environment variables in the `.env` file:

```bash
OPENAI_API_KEY=your-openai-api-key
GOOGLE_SEARCH_API_KEY=your-google-api-key
GOOGLE_CX_ID=your-google-cx-id
GEMINI_API_KEY=your-gemini-api-key  # Optional if Gemini is used
```

## Environment Variables

- `OPENAI_API_KEY`: Your API key for OpenAI GPT-4.
- `GOOGLE_SEARCH_API_KEY`: Your API key for the Google Custom Search API.
- `GOOGLE_CX_ID`: The custom search engine ID for Google.
- `GEMINI_API_KEY`: (Optional) Gemini API key if you're using a different data source.

## Usage

1. Run the FastAPI server:

```bash
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`.

### Example API Call

You can send a `POST` request to the `/ask` endpoint with a JSON body like this:

```json
{
  "question": "What are the latest technical specifications for the Tiangong robot?",
  "source": "Google"
}
```

- If `source` is set to `"OpenAI"`, the query is directly handled by OpenAI.
- If `source` is set to `"Google"`, it will use the Google Custom Search API, scrape the results, and provide a summary using OpenAI.

## API Endpoints

### POST `/ask`

This endpoint processes a user query and fetches answers from OpenAI, Google, or other sources (like Gemini). It accepts the following parameters:

- `question`: The question or query that needs to be answered.
- `source`: The source for answering the question (`OpenAI`, `Google`, `Gemini`).

#### Example Request:

```json
{
  "question": "What are the advancements in quantum computing?",
  "source": "Google"
}
```

#### Example Response:

```json
{
  "summary": "Quantum computing advancements include...",
  "source": "Google"
}
```

## Error Handling

- **429 Too Many Requests**: When Google Custom Search rate limits the application, the system will retry with exponential backoff.
- **500 Internal Server Error**: General server-side errors are logged and returned with appropriate messages.

---

## License

This project is licensed under the MIT License.

## Contact

For any queries or issues, please contact the project maintainer:

- **Email**: [zaindev@duck.com](zaindev@duck.com)
