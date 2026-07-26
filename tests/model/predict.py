import joblib

vectorizer = joblib.load("../../model/vectorizer.joblib")
classifier = joblib.load("../../model/classifier.joblib")


def predict(text: str) -> str:
    X = vectorizer.transform([text])
    return classifier.predict(X)[0]


if __name__ == "__main__":
    while True:
        text = input("Enter text (or 'q' to quit): ")
        if text.lower() == "q":
            break
        label = predict(text)
        print(f"-> {label}\n")
