import os, re, json
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
import joblib
import tensorflow as tf

# ── Chargement au démarrage ──────────────────────────────────
app = FastAPI(title="Fake News Detector")

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH      = os.path.join(BASE_DIR, "models", "best_model.keras")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")

model     = tf.keras.models.load_model(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

CONTRACTIONS = {
    "don't":"do not","doesn't":"does not","didn't":"did not",
    "isn't":"is not","aren't":"are not","wasn't":"was not",
    "weren't":"were not","won't":"will not","wouldn't":"would not",
    "can't":"cannot","couldn't":"could not","shouldn't":"should not",
    "it's":"it is","i'm":"i am","i've":"i have","they're":"they are",
    "we're":"we are","you're":"you are","he's":"he is","she's":"she is",
    "that's":"that is","there's":"there is","what's":"what is",
    "mustn't":"must not","needn't":"need not",
}
STOPWORDS = set([
    "i","me","my","we","our","you","your","he","him","his","she","her",
    "it","its","they","them","their","this","that","these","those",
    "am","is","are","was","were","be","been","being","have","has","had",
    "do","does","did","a","an","the","and","but","if","or","as","of",
    "at","by","for","with","about","into","through","to","from","in","on",
    "over","then","once","here","there","when","where","how","all","both",
    "each","more","most","some","only","same","so","than","very","can",
    "will","just","should","now","s","t","d","ll","m","o","re","ve","y",
])
NEGATIONS = {"not","no","never","neither","nor"}
STOPWORDS -= NEGATIONS

def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    for c, e in CONTRACTIONS.items():
        text = re.sub(r'\b' + re.escape(c) + r'\b', e, text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    tokens = [t for t in text.split() if t not in STOPWORDS or t in NEGATIONS]
    tokens = [t for t in tokens if len(t) >= 2]
    return ' '.join(tokens)

# ── Schémas ─────────────────────────────────────────────────
class PredictRequest(BaseModel):
    title: str

class PredictBatchRequest(BaseModel):
    titles: List[str]

# ── Endpoints ───────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "fake_news_detector"}

@app.post("/predict")
def predict(req: PredictRequest):
    if not req.title or not req.title.strip():
        raise HTTPException(status_code=422, detail="Le titre ne peut pas être vide.")
    if len(req.title) > 300:
        raise HTTPException(status_code=400,
            detail=f"Titre trop long ({len(req.title)} caractères). Maximum : 300.")
    cleaned = clean(req.title)
    vec = vectorizer.transform([cleaned]).toarray()
    prob = float(model.predict(vec, verbose=0)[0][0])
    label = "REAL" if prob >= 0.5 else "FAKE"
    confidence = round(prob if prob >= 0.5 else 1 - prob, 4)
    return {"title": req.title, "label": label, "confidence": confidence}

@app.post("/predict/batch")
def predict_batch(req: PredictBatchRequest):
    if not req.titles:
        raise HTTPException(status_code=400, detail="La liste de titres est vide.")
    if len(req.titles) > 50:
        raise HTTPException(status_code=400,
            detail=f"Trop de titres ({len(req.titles)}). Maximum : 50.")
    results = []
    for title in req.titles:
        if not title or not title.strip():
            results.append({"title": title, "label": None,
                            "confidence": None, "error": "Titre vide"})
            continue
        cleaned = clean(title)
        vec = vectorizer.transform([cleaned]).toarray()
        prob = float(model.predict(vec, verbose=0)[0][0])
        label = "REAL" if prob >= 0.5 else "FAKE"
        confidence = round(prob if prob >= 0.5 else 1 - prob, 4)
        results.append({"title": title, "label": label, "confidence": confidence})
    return {"predictions": results, "count": len(results)}
