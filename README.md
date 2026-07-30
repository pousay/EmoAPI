# EmoAPI

A Persian (Farsi) text emotion classification API. Given a piece of Persian text, it predicts one of seven emotional states: **ANGRY, FEAR, HAPPY, HATE, OTHER, SAD, SURPRISE**.

Built end-to-end: data cleaning → classical ML model training → FastAPI service with optional JWT auth and rate limiting.

---

## Table of Contents

- [Dataset](#dataset)
- [Modeling Approach](#modeling-approach)
- [Results](#results)
- [Confusion Matrix & Error Analysis](#confusion-matrix--error-analysis)
- [Known Limitations](#known-limitations)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Setup & Running Locally](#setup--running-locally)
- [Environment Variables](#environment-variables)
- [Security Notes](#security-notes)

---

## Dataset

`datasets/train.csv` contains ~6,157 labeled Persian text samples (informal, social-media-style text — product reviews, tweets, comments). Each row has raw text and one of seven emotion labels.

**Label distribution** (imbalanced):

| Label | Count |
|---|---|
| OTHER | 1686 |
| ANGRY | 926 |
| SAD | 903 |
| FEAR | 759 |
| SURPRISE | 741 |
| HAPPY | 626 |
| HATE | 516 |

> Note: `datasets/test.csv` is byte-identical to `train.csv` (verified by hash) and was **not** used as a held-out set, since doing so would leak training data into evaluation. Instead, a stratified 80/10/10 train/val/test split was carved directly out of `train.csv`, ensuring rare classes (e.g. HATE) are represented in every split.

## Modeling Approach

This project deliberately uses **classical ML (TF-IDF + Linear SVM)** rather than a fine-tuned transformer (e.g. ParsBERT). Given the dataset size (~6k rows) and short, informal text, the accuracy gap versus a transformer is modest, while classical ML keeps the model small, fast, dependency-light (no `torch`/GPU needed), and easy to deploy.

Several configurations were tried and compared using macro-F1 (chosen over accuracy because of class imbalance — macro-F1 weighs all 7 classes equally, so it can't be inflated by the dominant OTHER class):

| Model | Features | Val Macro F1 |
|---|---|---|
| Baseline | Word TF-IDF (1-2 grams) + Logistic Regression | 0.61 |
| Char n-grams | Char TF-IDF (2-4 grams, `char_wb`) + LinearSVC | **0.63–0.64** |
| Combined | Word + Char TF-IDF (stacked) + LinearSVC | 0.62 |
| Tuned (`GridSearchCV`, `C`) | Char TF-IDF only + LinearSVC(C=0.5) | 0.62 (cross-val) |

**Character n-grams outperformed word n-grams**, and combining both features performed *worse* than char n-grams alone — extra word-level sparse features added noise rather than signal on this dataset size. This was a deliberate, tested finding, not an assumption.

**Final model**: `TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4), max_features=30000)` + `LinearSVC(C=0.5, class_weight='balanced')`, retrained on train+val combined, evaluated once on the untouched test split.

## Results

Final held-out test set performance:

```
              precision    recall  f1-score   support

       ANGRY       0.69      0.70      0.69        92
        FEAR       0.78      0.91      0.84        76
       HAPPY       0.51      0.56      0.53        63
        HATE       0.80      0.87      0.83        52
       OTHER       0.61      0.56      0.59       169
         SAD       0.49      0.48      0.48        90
    SURPRISE       0.61      0.55      0.58        74

    accuracy                           0.64       616
   macro avg       0.64      0.66      0.65       616
weighted avg       0.63      0.64      0.63       616
```

**Macro F1: 0.65** on data the model never saw during training or tuning.

HATE and FEAR are the strongest classes (F1 0.83–0.84) despite HATE having the fewest training examples — both have distinctive vocabulary that surface-level n-gram features pick up easily. HAPPY, SAD, and OTHER are the hardest (F1 0.48–0.59).

## Confusion Matrix & Error Analysis

![Confusion Matrix](./../assets/confusion_matrix.png)

*(Add `confusion_matrix.png`, generated in `main.ipynb`, to the repo root — see `Confusion Matrix` cell.)*

Two consistent error patterns emerged from the confusion matrix (based on the validation set):

**HAPPY → OTHER / SAD.** Of 62 HAPPY validation samples, 29 were correct, but 16 were predicted as OTHER and 9 as SAD. Manual inspection showed several HAPPY-labeled texts are actually sarcastic or mixed-sentiment (e.g. a review praising a phone's durability after describing it being smashed against a wall). The literal words read as negative even though the label is positive — a known hard problem in sentiment analysis that surface-level n-gram features can't resolve, since it requires understanding tone/context rather than just vocabulary.

**OTHER spreads broadly, not into one dominant class.** Of 169 OTHER validation samples, 86 were correct, with the remaining 83 spread fairly evenly across all six other classes (24 SAD, 19 ANGRY, 15 HAPPY, 11 SURPRISE, 9 FEAR, 5 HATE). This is expected: OTHER is defined as "none of the above," so by construction it contains fragments of every other class's vocabulary — there's no single, consistent linguistic signature for a classifier to learn.

**Conclusion**: the ~0.63–0.65 macro F1 ceiling for this feature representation is primarily a **data/label-design limitation**, not a hyperparameter or feature-engineering gap. `GridSearchCV` tuning on `C` confirmed this — tuning barely moved the needle (0.624 vs 0.63 already achieved), indicating the model had already converged near what these features can support.

## Known Limitations

- Struggles with sarcasm and mixed-sentiment text (surface words contradict intended emotion)
- OTHER is a low-precision catch-all class by design
- Trained on informal/social-media-style Persian text; may not generalize well to formal writing
- No transformer/contextual embeddings — purely n-gram/lexical features

## Project Structure

```
EmoAPI/
├── datasets/
│   ├── train.csv          # labeled training data
│   └── test.csv           # NOTE: identical to train.csv, not used for evaluation
├── model/
│   ├── vectorizer.joblib  # fitted TfidfVectorizer
│   └── classifier.joblib  # fitted LinearSVC
├── main.ipynb              # full training notebook: cleaning → baseline → tuning → final model
├── confusion_matrix.png    # generated during training
├── api/
│   ├── main.py             # FastAPI app entrypoint
│   ├── schema.py           # Pydantic request/response models
│   ├── _types.py           # emotion label enum
│   ├── core/
│   │   ├── config.py       # env-based settings (pydantic-settings)
│   │   ├── model.py        # loads joblib model, exposes Predict.predict()
│   │   ├── ratelimiter.py  # slowapi rate limiting setup
│   │   ├── dependencies.py # optional JWT auth dependency
│   │   ├── crud.py         # user DB operations
│   │   ├── hash.py         # JWT token creation
│   │   └── database.py     # SQLAlchemy session
│   ├── database/
│   │   ├── database.py     # SQLAlchemy engine/session setup
│   │   └── models.py       # User table definition
│   └── routes/
│       ├── query.py        # POST text -> predicted emotion
│       ├── states.py       # GET list of possible emotion labels
│       └── auth.py         # register/login/refresh/me
├── .env.example             # template — copy to .env and fill in your own SECRET_KEY
└── requirements.txt
```

## API Reference

Base URL: `http://<HOST>:<PORT>` (default `http://127.0.0.1:8080`)

### `GET /text`

Classify the emotion of a piece of Persian text.

**Query params**: `text` (string, required)

```bash
curl "http://127.0.0.1:8080/text?text=خیلی%20خوشحالم"
```

```json
{
  "text": "خیلی خوشحالم",
  "state": "HAPPY"
}
```

Rate-limited (see `RATE_LIMITER_PER_MINUTE`). Returns `422` if `text` is empty, `429` if rate limit exceeded. Requires a bearer token if `ENABLE_AUTH=true`.

### `GET /all_states`

Returns the full set of possible emotion labels.

```bash
curl "http://127.0.0.1:8080/all_states"
```

```json
["ANGRY", "FEAR", "HAPPY", "HATE", "OTHER", "SAD", "SURPRISE"]
```

Requires a bearer token if `ENABLE_AUTH=true`.

### Auth endpoints (active only if `ENABLE_AUTH=true`)

| Endpoint | Method | Description |
|---|---|---|
| `/auth/register` | POST | Create a new user (`username`, `password`) |
| `/auth/login` | POST | Log in, receive `access_token` + `refresh_token` |
| `/auth/me` | GET | Get current user (requires bearer token) |
| `/auth/refresh` | POST | Exchange a refresh token for a new token pair |

When `ENABLE_AUTH=false`, all endpoints (including `/text` and `/all_states`) are open, no token required.

## Setup & Running Locally

```bash
# 1. clone the repo
git clone https://github.com/pousay/EmoAPI.git
cd EmoAPI

# 2. create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. install dependencies
pip install -r requirements.txt

# 4. set up your environment file
cp .env.example .env
# then edit .env and set your own SECRET_KEY (see Security Notes below)

# 5. (optional) retrain the model
# open and run main.ipynb top to bottom — this regenerates model/vectorizer.joblib
# and model/classifier.joblib from datasets/train.csv

# 6. run the API
uvicorn api.main:app --reload --host 127.0.0.1 --port 8080
```

Interactive API docs available at `http://127.0.0.1:8080/docs` once running (FastAPI's built-in Swagger UI).

## Environment Variables

| Variable | Description |
|---|---|
| `HOST` | Host to bind the server to (e.g. `127.0.0.1`) |
| `PORT` | Port to bind the server to (e.g. `8080`) |
| `DB_PATH` | SQLAlchemy DB URL (e.g. `sqlite:///./users.db`) |
| `SECRET_KEY` | Secret used to sign JWTs — **generate your own, never reuse the example value** |
| `ALGORITHM` | JWT signing algorithm (e.g. `HS256`) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime in days |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes |
| `RATE_LIMITER_ENABLED` | `true`/`false` — toggle rate limiting |
| `RATE_LIMITER_PER_MINUTE` | Requests allowed per minute per client IP |
| `ENABLE_AUTH` | `true`/`false` — require bearer auth on `/text` and `/all_states` |
| `DEBUG` | `true`/`false` — enables uvicorn `reload`; keep `false` in production |

## Security Notes

- `ENABLE_AUTH=false` is convenient for local development but means `/text` and `/all_states` are fully open with no authentication — confirm this is intentional before deploying publicly.
- CORS is currently configured with `allow_origins=["*"]` and no credentials — fine for a public, tokenless API, but revisit if cookie-based auth is ever introduced.

---

## License
- [MIT LICENSE](./LICENSE)