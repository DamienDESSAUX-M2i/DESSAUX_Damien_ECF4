import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import joblib
import nltk
import spacy
import tensorflow

from api.core.settings import get_settings
from api.models.prediction import PredictionLabel


def ensure_stopwords_downloaded():
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")


ensure_stopwords_downloaded()

NLP = spacy.load("en_core_web_sm")

STOP_WORDS = set(nltk.corpus.stopwords.words("english")) - {
    "not",
    "no",
    "never",
    "neither",
}

CONTRACTIONS = {
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "can't": "can not",
    "couldn't": "could not",
    "won't": "will not",
    "wouldn't": "would not",
    "shouldn't": "should not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "haven't": "have not",
    "hasn't": "has not",
    "hadn't": "had not",
    "i'm": "i am",
    "you're": "you are",
    "he's": "he is",
    "she's": "she is",
    "it's": "it is",
    "we're": "we are",
    "they're": "they are",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "i'll": "i will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "we'll": "we will",
    "they'll": "they will",
    "there's": "there is",
    "that's": "that is",
}

DOMAIN_PATTERN = re.compile(
    r"\b(?:[a-z0-9-]+\.)+(?:org|net|info|co|io|gov|edu|uk|us|biz|online|site)\b"
)

TLD_PATTERN = re.compile(r"\.(com|org|net|info|co|io|gov|edu|uk|us|biz|online|site)\b")

CONTRACTION_PATTERN = re.compile(
    r"\b(" + "|".join(map(re.escape, CONTRACTIONS.keys())) + r")\b"
)


class MLModel:
    """Wrapper autour du modèle scikit-learn."""

    def __init__(self, vectorizer_path: Path, model_path: Path):
        self.model = None
        self.vectorizer = None
        self.classes = [PredictionLabel.FAKE, PredictionLabel.REAL]
        settings = get_settings()
        self.threshold = settings.threshold
        self.report: Optional[dict] = None
        self._load_vectorizer(vectorizer_path)
        self._load_model(model_path)

    def _load_vectorizer(self, vectorizer_path: Path) -> None:
        """Charge le vectorizer depuis un fichier joblib."""
        if not vectorizer_path.exists():
            raise FileNotFoundError(
                f"Fichier vectorizer introuvable : {vectorizer_path}"
            )

        self.vectorizer = joblib.load(vectorizer_path)

    def _load_model(self, model_path: Path) -> None:
        """Charge le modèle depuis un fichier joblib."""
        if not model_path.exists():
            raise FileNotFoundError(f"Fichier modèle introuvable : {model_path}")

        self.model = tensorflow.keras.models.load_model(model_path)

    def predict(
        self, titles: list[str], threshold: float | None = None
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Retourne (classe_prédite, confiance, dict_probabilités).

        Raises:
            RuntimeError: si le vectorizer ou le modèle n'est pas chargé.
        """
        if self.vectorizer is None:
            raise RuntimeError("Le vectorizer n'est pas chargé.")
        if self.model is None:
            raise RuntimeError("Le modèle n'est pas chargé.")

        titles_cleaned = [self._clean_title(title) for title in titles]

        titles_vectorized = self.vectorizer.transform(titles_cleaned)

        labels_probabilities = self.model.predict(titles_vectorized).flatten()

        threshold = threshold or self.threshold

        labels_predicted_int = (labels_probabilities > threshold).astype(int)

        prediction_class = [
            self.classes[label_predicted_int]
            for label_predicted_int in labels_predicted_int
        ]
        confidence = labels_probabilities

        return prediction_class, confidence

    def get_accuracy(self) -> Optional[float]:
        """Retourne l'accuracy issue du rapport d'entraînement."""
        if self.report:
            return self.report.get("accuracy")
        return None

    def _expand_contractions(self, text: str) -> str:
        return CONTRACTION_PATTERN.sub(lambda x: CONTRACTIONS[x.group()], text)

    def _clean_title(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"http\S+|www\S+", "", text)
        text = DOMAIN_PATTERN.sub("", text)
        text = TLD_PATTERN.sub("", text)
        text = re.sub(r"@\w+", "", text)
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\b\d+\b", "", text)
        text = self._expand_contractions(text)
        tokens = text.split()
        tokens = [w for w in tokens if w not in STOP_WORDS]
        doc = NLP(" ".join(tokens))
        lemmas = [token.lemma_ for token in doc]
        lemmas = [w for w in lemmas if len(w) >= 2]
        return " ".join(lemmas)
