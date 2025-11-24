# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json

app = FastAPI(title="FastAPI + Ollama (llama3.2:3b-instruct-q4_K_M)")

# CORS pour ton frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ton frontend
    allow_methods=["*"],
    allow_headers=["*"],
) 

# ✅ Configuration Ollama
OLLAMA_API_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:3b-instruct-q4_K_M"

# Modèle de réponse JSON
class ResponseModel(BaseModel):
    prompt: str
    response: str

@app.get("/ask", response_model=ResponseModel)
def ask_ollama(prompt: str = Query(..., description="Question à poser au modèle Llama3.2")):
    """
    Envoie le prompt à Ollama et retourne la réponse complète.
    """
    try:
        data = {
            "model": MODEL_NAME,
            "prompt": prompt
        }

        # Appel à l'API Ollama /api/generate
        with requests.post(f"{OLLAMA_API_URL}/api/generate", json=data, stream=True) as resp:
            resp.raise_for_status()
            completion_text = ""

            # Ollama renvoie du streaming JSON ligne par ligne
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    parsed = json.loads(line.decode("utf-8"))
                    completion_text += parsed.get("response", "")
                except json.JSONDecodeError:
                    continue

        return ResponseModel(prompt=prompt, response=completion_text.strip() or "Aucune réponse reçue.")

    except requests.RequestException as e:
        return ResponseModel(prompt=prompt, response=f"Erreur lors de l'appel à Ollama : {e}")
