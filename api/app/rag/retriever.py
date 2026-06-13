import json
import math
import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = APP_DIR / "rag_index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_chunks = None
_vectors = None
_vocab = None
_idf = None
_method = None
_model = None


def _lazy_load():
    global _chunks, _vectors, _vocab, _idf, _method, _model
    if _chunks is not None:
        return
    meta_path = INDEX_DIR / "index_meta.json"
    if not meta_path.exists():
        _chunks = []
        _vectors = []
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    _method = meta.get("method", "tfidf")
    _chunks = json.loads((INDEX_DIR / "content_chunks.json").read_text(encoding="utf-8"))
    _vectors = json.loads((INDEX_DIR / "content_vectors.json").read_text(encoding="utf-8"))

    if _method == "tfidf":
        _vocab = json.loads((INDEX_DIR / "vocab.json").read_text(encoding="utf-8"))
        _idf = json.loads((INDEX_DIR / "idf.json").read_text(encoding="utf-8"))
    else:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME)
        except Exception:
            _method = "tfidf"
            _vocab = json.loads((INDEX_DIR / "vocab.json").read_text(encoding="utf-8"))
            _idf = json.loads((INDEX_DIR / "idf.json").read_text(encoding="utf-8"))


def tokenize(text):
    return re.findall(r'[a-zA-Z0-9]+', text.lower())


def _embed_query(query):
    if _method == "sentence-transformers" and _model is not None:
        import numpy as np
        vec = _model.encode([query], normalize_embeddings=True)[0]
        return vec.tolist()
    tokens = tokenize(query)
    vec = [0.0] * len(_vocab)
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    max_tf = max(tf.values()) if tf else 1
    for token, count in tf.items():
        if token in _vocab:
            idx = _vocab[token]
            idf_val = _idf.get(token, 1.0)
            vec[idx] = (count / max_tf) * idf_val
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine_similarity(a, b):
    dot = sum(ai * bi for ai, bi in zip(a, b))
    return dot


def _extract_metadata(message):
    lower = message.lower()
    meta = {"module_ids": [], "phases": [], "systems": []}

    for m in ["t1", "t2", "t3", "t4"]:
        if m in lower:
            meta["module_ids"].append(m.upper())

    if "salesforce" in lower:
        meta["systems"].append("salesforce")
        meta["phases"].append("salesforce_setup")
    if "slack" in lower:
        meta["systems"].append("slack")
        meta["phases"].append("slack_setup")

    profile_keywords = ["profile", "personal info", "update", "change my"]
    if any(k in lower for k in profile_keywords):
        meta["phases"].append("profile_update")

    access_keywords = ["access", "system", "permission", "request", "entitlement"]
    if any(k in lower for k in access_keywords):
        meta["phases"].append("access_request")

    approval_keywords = ["approval", "manager", "pending", "approve", "waiting"]
    if any(k in lower for k in approval_keywords):
        meta["phases"].append("manager_approval")

    ticket_keywords = ["ticket", "it", "submitted", "itsm"]
    if any(k in lower for k in ticket_keywords):
        meta["phases"].append("ticket_status")

    if "training" in lower:
        meta["phases"].append("training")

    return meta


def _matches_metadata(chunk, meta):
    if not any(meta.values()):
        return True
    if meta["module_ids"] and chunk.get("module_ids"):
        if any(m in chunk["module_ids"] for m in meta["module_ids"]):
            return True
    if meta["phases"] and chunk.get("phases"):
        if any(p in chunk["phases"] for p in meta["phases"]):
            return True
    if meta["systems"] and chunk.get("systems"):
        if any(s in chunk["systems"] for s in meta["systems"]):
            return True
    return False


def retrieve(query, top_k=3, minimum_score=0.10):
    _lazy_load()
    if not _chunks:
        return {"matches": []}

    meta = _extract_metadata(query)
    query_vec = _embed_query(query)

    candidates = [
        (i, chunk)
        for i, chunk in enumerate(_chunks)
        if chunk.get("runtime_approved") is True
    ]

    preferred = [
        (i, chunk) for i, chunk in candidates
        if _matches_metadata(chunk, meta)
    ]

    scored = []
    search_space = preferred if preferred else candidates
    for i, chunk in search_space:
        score = _cosine_similarity(query_vec, _vectors[i])
        if score >= minimum_score:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    scored = scored[:top_k]

    return {
        "matches": [
            {
                "chunk_id": chunk["chunk_id"],
                "content_id": chunk["content_id"],
                "title": chunk["title"],
                "score": round(score, 4),
                "text": chunk["text"],
                "source_ids": chunk.get("source_ids", []),
                "runtime_approved": chunk.get("runtime_approved", False),
            }
            for score, chunk in scored
        ],
        "retrieval_method": _method or "unknown",
    }
