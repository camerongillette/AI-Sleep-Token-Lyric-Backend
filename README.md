# Sleep Token Lyric Generator

A FastAPI-based backend service that generates lyrics in the style of Sleep Token. The service uses OpenAI's GPT-3.5 to create emotionally evocative and poetic choruses.

## Features

- Generates lyrics in Sleep Token's distinctive style
- Supports multiple emotional themes and topics
- Rate-limited API endpoints for fair usage
- Secure with CORS and security headers

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   FRONTEND_URLS=http://localhost:5173
   ```

## API Endpoints

### Generate Lyrics
```
GET /lyricgenerator/sleeptoken?topicId={id}
```

**Parameters:**
- `topicId` (integer): The theme ID for the lyrics (0-7)
  - 0: ANY TOPIC
  - 1: LOVE
  - 2: DEATH
  - 3: BREAK UP
  - 4: LONELINESS
  - 5: BETRAYAL
  - 6: HEARTBREAK
  - 7: MANIPULATION

**Response:**
```json
{
    "band_name": "Sleep Token",
    "topic": "TOPIC_NAME",
    "lyrics": "Generated chorus lyrics..."
}
```
## Security

The API includes:
- CORS protection
- Rate limiting
- Security headers (HSTS, CSP, XSS protection)
- Input validation

## Error Handling


