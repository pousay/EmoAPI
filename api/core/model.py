import joblib
from pathlib import Path

models_path = Path(__file__).parent.parent.parent / "model"

vectorizer = joblib.load(models_path / "vectorizer.joblib")
classifier = joblib.load(models_path / "classifier.joblib")


class Predict:

    @staticmethod
    def predict(text: str) -> str:
        X = vectorizer.transform([text])
        return classifier.predict(X)[0]
