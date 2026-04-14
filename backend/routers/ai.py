from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

router = APIRouter(prefix="/api/ai", tags=["ai"])

OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

CDC_PROMPT_TEMPLATE = """You are a senior Technical Project Manager and Software Architect.
Write a detailed, professional Cahier de Charge (project specifications document) for the following project.

Project Name: {name}
Description: {description}

The document must include these 10 sections:
1. Objectif — what the project achieves and why it matters
2. Perimetre fonctionnel — all features and user stories (detailed)
3. Stack technique — technologies, frameworks, databases to use
4. Architecture — high-level system design (components, APIs, data flow)
5. Modele de donnees — key entities and relationships
6. API et Endpoints — main REST endpoints needed
7. Interface utilisateur — pages and UI components needed
8. Securite — authentication, authorization, data protection requirements
9. Performance — expected load, caching, optimization requirements
10. Livrables et Planning — sprints breakdown, deliverables per sprint

Write in a clear, structured format. Be specific and technical.
Every requirement must be actionable. Start writing the document now:"""


class CdcRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class CdcResponse(BaseModel):
    cahier_de_charge: str


@router.post("/generate-cdc", response_model=CdcResponse)
def generate_cdc(data: CdcRequest):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Project name is required")

    prompt = CDC_PROMPT_TEMPLATE.format(
        name=data.name.strip(),
        description=data.description or "No description provided."
    )

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=180
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama at {OLLAMA_URL}. Make sure Ollama is running: run 'ollama serve' in a terminal."
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Ollama took too long to respond. The model may still be loading — try again in a moment."
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{OLLAMA_MODEL}' not found in Ollama. Run: ollama pull {OLLAMA_MODEL}"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama error {response.status_code}: {response.text[:300]}"
        )

    cdc_text = response.json().get("response", "").strip()
    if not cdc_text:
        raise HTTPException(status_code=500, detail="Ollama returned an empty response. Try again.")

    return CdcResponse(cahier_de_charge=cdc_text)
