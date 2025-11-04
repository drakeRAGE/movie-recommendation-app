# main.py
import os
import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
from openai import OpenAI

# Load env vars
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY in environment or .env file")

# Create OpenAI client (new style)
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Database setup (SQLite) ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recommendations.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text, nullable=False)
    recommended_movies = Column(Text, nullable=False)  # store JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- FastAPI app ---
app = FastAPI(title="Movie Recommender (backend, new OpenAI API)")

# --- Pydantic schemas ---
class RecommendRequest(BaseModel):
    user_input: str

class MovieSuggestion(BaseModel):
    title: str
    year: Optional[str] = None
    reason: Optional[str] = None

class RecommendResponse(BaseModel):
    recommendations: List[MovieSuggestion]

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper: call OpenAI (Responses API) ---
def ask_openai_for_movies(user_input: str) -> List[dict]:
    """
    Use the modern Responses API to ask the model to output a JSON array
    with 3-5 movie suggestion objects.
    """
    system_prompt = (
        "You are a helpful movie recommendation assistant. "
        "When given a user's preference, return a JSON array with 3 to 5 movie objects. "
        "Each object must contain at least 'title' (string). Optionally include 'year' and a one-sentence 'reason'. "
        "IMPORTANT: respond ONLY with valid JSON (an array). Do not add extra commentary or markdown."
    )
    user_prompt = f"User preference: {user_input}\nReturn 3-5 movie suggestions as a JSON array."

    try:
        resp = client.responses.create(
            model="gpt-3.5-turbo",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_output_tokens=500,   # <-- correct parameter for Responses API
            temperature=0.8,
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI API request failed: {e}")

    text = (resp.output_text or "").strip()
    if not text:
        # fallback: try to inspect resp.output
        try:
            pieces = []
            for item in getattr(resp, "output", []) or []:
                content = item.get("content") if isinstance(item, dict) else None
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and "text" in c:
                            pieces.append(c["text"])
                elif isinstance(item, str):
                    pieces.append(item)
            text = "\n".join(pieces).strip()
        except Exception:
            text = ""

    if not text:
        raise RuntimeError("OpenAI response was empty")

    # Try to parse JSON directly; if model added surrounding text, extract JSON substring
    try:
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise ValueError("Parsed JSON is not a list")
        return parsed
    except Exception:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            try:
                parsed = json.loads(json_str)
                if not isinstance(parsed, list):
                    raise ValueError("Parsed JSON substring is not a list")
                return parsed
            except Exception as e:
                raise RuntimeError(f"Failed to parse JSON from model response: {e}\nRaw response: {text}")
        else:
            raise RuntimeError(f"Model response did not contain a JSON array. Raw response: {text}")

# --- Endpoint: POST /recommend ---
@app.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest, db: Session = Depends(get_db)):
    if not payload.user_input or not payload.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input must be a non-empty string")

    # Call OpenAI
    try:
        movie_list = ask_openai_for_movies(payload.user_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Normalize items to expected shape (title, year, reason)
    normalized = []
    for item in movie_list:
        if isinstance(item, dict) and "title" in item:
            normalized.append({
                "title": str(item.get("title", "")).strip(),
                "year": str(item.get("year")) if item.get("year") is not None else None,
                "reason": str(item.get("reason")) if item.get("reason") is not None else None,
            })
        else:
            # If model returned strings instead of objects
            if isinstance(item, str):
                normalized.append({"title": item.strip(), "year": None, "reason": None})

    # Save to DB
    rec = Recommendation(
        user_input=payload.user_input.strip(),
        recommended_movies=json.dumps(normalized, ensure_ascii=False),
        created_at=datetime.utcnow()
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {"recommendations": normalized}

# --- Utility endpoint: get saved history ---
@app.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.query(Recommendation).order_by(Recommendation.created_at.desc()).limit(limit).all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "user_input": r.user_input,
            "recommended_movies": json.loads(r.recommended_movies),
            "created_at": r.created_at.isoformat(),
        })
    return {"results": out}
