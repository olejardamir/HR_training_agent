import json
import math
import re
from pathlib import Path
from collections import Counter

APP_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = APP_DIR / "fixtures"
INDEX_DIR = APP_DIR / "rag_index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_USE_TFIDF = False
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    _MODEL = SentenceTransformer(MODEL_NAME)
except Exception:
    _USE_TFIDF = True
    _MODEL = None


def load_runtime_content():
    items = []
    for content_type, filename in [
        ("training", "training_content.json"),
        ("onboarding", "onboarding_content.json"),
    ]:
        path = FIXTURE_DIR / filename
        if not path.exists():
            continue
        for item in json.loads(path.read_text(encoding="utf-8")):
            if item.get("runtime_approved") is True:
                items.append((content_type, item))
    return items


def chunk_text(text, max_words=700, overlap_words=50):
    words = text.split()
    if len(words) <= max_words:
        return [text.strip()] if text.strip() else []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap_words)
    return chunks


def split_by_headings(text):
    sections = re.split(r'(?=^#{1,3}\s)', text, flags=re.MULTILINE)
    return [s.strip() for s in sections if s.strip()]


def build_chunks():
    chunks = []
    for content_type, item in load_runtime_content():
        body = item.get("body", "")
        heading_sections = split_by_headings(body)
        for section in heading_sections:
            for i, text in enumerate(chunk_text(section), start=1):
                chunk = {
                    "chunk_id": f"{item['content_id']}__chunk_{i:03d}",
                    "content_id": item["content_id"],
                    "content_type": content_type,
                    "title": item.get("title", ""),
                    "text": text,
                    "module_ids": item.get("module_ids", []),
                    "phases": item.get("phases", []),
                    "systems": item.get("systems", []),
                    "roles": item.get("roles", ["all"]),
                    "levels": item.get("levels", ["all"]),
                    "source_ids": item.get("source_ids", []),
                    "runtime_approved": item.get("runtime_approved", False),
                }
                chunks.append(chunk)
    return chunks


def tokenize(text):
    return re.findall(r'[a-zA-Z0-9]+', text.lower())


class SimpleTfidfVectorizer:
    def __init__(self):
        self.vocab = {}
        self.idf = {}
        self.doc_count = 0

    def fit(self, texts):
        doc_freq = Counter()
        all_tokens = set()
        for text in texts:
            tokens = set(tokenize(text))
            for t in tokens:
                doc_freq[t] += 1
            all_tokens.update(tokens)
        self.doc_count = len(texts)
        self.vocab = {t: i for i, t in enumerate(sorted(all_tokens))}
        n = self.doc_count
        self.idf = {
            t: math.log((n + 1) / (doc_freq[t] + 1)) + 1
            for t in self.vocab
        }

    def transform(self, texts):
        vectors = []
        for text in texts:
            vec = [0.0] * len(self.vocab)
            tf = Counter(tokenize(text))
            max_tf = max(tf.values()) if tf else 1
            for token, count in tf.items():
                if token in self.vocab:
                    vec[self.vocab[token]] = (count / max_tf) * self.idf[token]
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]
            vectors.append(vec)
        return vectors


def build_index():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    chunks = build_chunks()
    texts = [f"{c['title']}\n{c['text']}" for c in chunks]

    if _USE_TFIDF:
        vectorizer = SimpleTfidfVectorizer()
        vectorizer.fit(texts)
        vectors = vectorizer.transform(texts)
        (INDEX_DIR / "vocab.json").write_text(
            json.dumps(vectorizer.vocab, indent=2), encoding="utf-8"
        )
        (INDEX_DIR / "idf.json").write_text(
            json.dumps(vectorizer.idf, indent=2), encoding="utf-8"
        )
        method = "tfidf"
        vector_dim = len(vectorizer.vocab)
    else:
        import numpy as np
        vectors = _MODEL.encode(texts, normalize_embeddings=True)
        vectors = vectors.tolist()
        method = "sentence-transformers"
        vector_dim = 384

    (INDEX_DIR / "content_chunks.json").write_text(
        json.dumps(chunks, indent=2), encoding="utf-8"
    )
    (INDEX_DIR / "content_vectors.json").write_text(
        json.dumps(vectors), encoding="utf-8"
    )
    (INDEX_DIR / "index_meta.json").write_text(
        json.dumps({
            "method": method,
            "chunk_count": len(chunks),
            "vector_dim": vector_dim,
        }, indent=2), encoding="utf-8"
    )

    print(f"Index built: {len(chunks)} chunks, method={method}, dim={vector_dim}")


if __name__ == "__main__":
    build_index()
