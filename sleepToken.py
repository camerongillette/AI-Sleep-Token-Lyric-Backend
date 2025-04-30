import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from openai import OpenAI
from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address
from SecurityHeaderMiddleware import SecurityHeadersMiddleware;

load_dotenv()

topics = {
    0: "ANY TOPIC",
    1: "LOVE",
    2: "DEATH",
    3: "BREAK UP",
    4: "LONELINESS"
}

choruses = [
    """So stick to me
    Stick to me like caramel
    Walk beside me till you feel nothin' as well
    I'm fallin' free of the final parallel
    The sweetest dreams are bitter
    But there's no one left to tell""",
    """Come on, come on
    Out from underneath who you were
    Come on, come on now
    You know that it's time to emerge""",
    """Raise me up again
    Take me past the edge
    I want to see the other side
    Won't you show me what it's like?
    Won't you show me what it's like?""",
    """When the river runs dry and the curtain is called
    How will I know if I can't see the bottom?
    Come up for air and choke on it all
    No one else knows that I've got a problem
    What if I can't get up and stand tall?
    What if the diamond days are all gone
    And who will I be when the empire falls?
    Wake up alone and I'll be forgotten""",
    """My, my, those eyes like fire
    I'm a winged insect, you're a funeral pyre
    Come now, bite through these wires
    I'm a waking hell and the gods grow tired
    Reset my patient violence along both lines of a pathway higher
    Grow back your sharpest teeth, you know my desire""",
    """I was more than just a body in your passenger seat
    And you were more than just somebody I was destined to meet
    I see you go half-blind when you're looking at me
    But I am
    Between the secondhand smoke and the glass on the street
    You gave me nothing whatsoever but a reason to leave
    You say you want me, but you know I'm not what you need
    But I am""",
    """And just like the rain
    You cast the dust into nothing
    And wash out the salt from my hands
    So touch me again
    I feel my shadow dissolving
    Will you cleanse me with pleasure?""",
    """She's not acid nor alkaline
    Caught between black and white
    Not quite either day or night
    She's perfectly misaligned
    I'm caught up in her design
    And how it connects to mine
    I see in a different light
    The objects of my desire""",
    """You've got me in a chokehold
    You've got me in a chokehold
    You've got me in a chokehold
    You've got me in a chokehold""",
    """And I believe
    That somewhere in the past
    Something was between
    You and I, my dear
    And it remains
    With me to this day
    No matter what I do
    This wound will never heal"""
]

# Prepare the examples for the prompt (multiline choruses remain intact)
examples = "\n\n".join([f"Chorus {i+1}: {chorus}" for i, chorus in enumerate(choruses)])

#- --- CORS VARIABLES ----
frontend_url = os.getenv('FRONTEND_URL', 'MISSING FRONTEND_URL ENV VAR')
print(f"Frontend URL: {frontend_url}")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

# ---- RATE LIMITING ----
limiter = Limiter(key_func=get_remote_address)

@app.exception_handler(RateLimitExceeded)
def rate_limit_error(request, exc):
    return JSONResponse(status_code=500, content={"error": "Slow down a bit, servers are expensive :)"})

# ----- OpenAI STUFF
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the function to generate lyrics
def generate_lyrics(band_name: str, topic: str) -> str:
    # Construct the prompt, ensuring the model knows to generate a full multi-line chorus
    prompt = (
        f"Generate a lyrically poetic and emotionally evocative chorus inspired by the style of Sleep Token. "
        f"The chorus should express themes of sacred longing, romantic worship, or the anguish of unreciprocated devotion. "
        f"Use rich sensory imagery, mystical or ritualistic metaphors (e.g., altars, offerings, divine punishment, sacred pain), "
        f"and a tone that feels intimate, reverent, and haunted. The vocal delivery should be imagined as dynamic—whispered tenderness escalating "
        f"into soulful wails or cathartic screams. Combine ethereal beauty with raw, aching vulnerability. "
        f"Format the chorus in 4–8 lines, suitable for a genre-blending track of ambient metal and alternative R&B. Avoid standard pop phrasing; lean "
        f"into spiritual or mythic undertones. Sometimes use Alternate Rhyme or ABAB structure. "
        "Here are some examples of choruses from the band's top 8 songs:\n"
        f"{examples}\n"
        f"Topic: {topic}\n"
        "Chorus (4-8 lines):\n"
    )

    # Call OpenAI API to generate lyrics
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # You can use GPT-3.5/4 models if available
        prompt=prompt,
        max_tokens=200,  # Increased max tokens to ensure enough space for 4-8 lines
        temperature=0.8,  # Controls creativity
        top_p=1,  # Top-p sampling for diversity
        n=1  # Generate one response
    )

    # Extract and return the generated text from the response
    chorus = response.choices[0].text.strip()  # Access the correct attribute
    return chorus

# ----- API ENDPOINTS -----

@app.get("/sleeptoken")
@limiter.limit("5/minute")
def generate_lyrics_endpoint(request: Request, topicId: int):
    try:
        band_name = "Sleep Token"
        topic = topics.get(topicId);
        if topic is None:
            return JSONResponse(status_code=400, content={"error": "Invalid topic ID."})
        
        generated_chorus = generate_lyrics(band_name, topic)
        return JSONResponse(content={"band_name": band_name, "topic": topic, "lyrics": generated_chorus})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to generate lyrics", "message": str(e)})
