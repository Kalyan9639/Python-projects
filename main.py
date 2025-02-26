import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from googletrans import Translator, LANGUAGES
from fastapi.templating import Jinja2Templates
from gtts import gTTS
from fastapi.responses import FileResponse
import uuid

app = FastAPI()

# Absolute Path Fix for Static Files
current_dir = os.path.dirname(__file__)
static_folder = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_folder), name="static")

# Initialize Jinja2 templates
templates_folder = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_folder)

# Home route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "languages": LANGUAGES})

# Translation route
@app.post("/translate", response_class=HTMLResponse)
async def translate(request: Request, text: str = Form(...), lang: str = Form(...)):
    translator = Translator()
    result = translator.translate(text, dest=lang)
    return templates.TemplateResponse("index.html", {"request": request, "translated_text": result.text, "languages": LANGUAGES, "input_text": text, "selected_lang": lang})

@app.get("/tts")
async def tts(text: str, lang: str):
    # Ensure the directory exists before saving the audio file
    audio_folder = "static/audio"
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)

    tts = gTTS(text=text, lang=lang)
    audio_file = f"static/audio/{uuid.uuid4().hex}.mp3"
    tts.save(audio_file)
    return FileResponse(audio_file, media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
