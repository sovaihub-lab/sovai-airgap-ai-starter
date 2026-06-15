import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


DOCUMENTS_DIR = Path(os.getenv("DOCUMENTS_DIR", "/app/data/documents"))


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    path: str
    text: str


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


class PrivateRAG:
    """
    Pure-Python BM25-style retrieval.

    This avoids scikit-learn/numpy/scipy so the laptop MVP is easier to
    prepare and run offline on Windows, Linux, or macOS.
    """

    def __init__(self, docs_dir: Path = DOCUMENTS_DIR):
        self.docs_dir = docs_dir
        self.chunks: List[Chunk] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_term_counts: List[Counter] = []
        self.document_frequency: Dict[str, int] = {}
        self.avg_doc_len: float = 0.0
        self.reload()

    def reload(self) -> Dict[str, Any]:
        self.chunks = self._load_chunks()
        self._build_index()
        return {
            "documents": len(set(c.document_id for c in self.chunks)),
            "chunks": len(self.chunks),
            "retrieval": "pure-python-bm25",
        }

    def _build_index(self) -> None:
        self.doc_tokens = [tokenize(c.text) for c in self.chunks]
        self.doc_term_counts = [Counter(tokens) for tokens in self.doc_tokens]

        df = defaultdict(int)
        for tokens in self.doc_tokens:
            for token in set(tokens):
                df[token] += 1

        self.document_frequency = dict(df)
        if self.doc_tokens:
            self.avg_doc_len = sum(len(tokens) for tokens in self.doc_tokens) / len(self.doc_tokens)
        else:
            self.avg_doc_len = 0.0

    def _load_chunks(self) -> List[Chunk]:
        chunks: List[Chunk] = []
        if not self.docs_dir.exists():
            return chunks

        for path in sorted(self.docs_dir.glob("**/*")):
            if path.suffix.lower() not in [".md", ".txt"]:
                continue

            raw = path.read_text(encoding="utf-8", errors="ignore")
            title = self._extract_title(raw, path)
            doc_id = path.stem

            parts = self._split_text(raw)
            for idx, part in enumerate(parts):
                chunk_text = part.strip()
                if len(chunk_text) < 40:
                    continue
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_id}-chunk-{idx+1:03d}",
                        document_id=doc_id,
                        title=title,
                        path=str(path),
                        text=chunk_text,
                    )
                )
        return chunks

    @staticmethod
    def _extract_title(raw: str, path: Path) -> str:
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line.replace("# ", "", 1).strip()
        return path.stem.replace("-", " ").title()

    @staticmethod
    def _split_text(raw: str) -> List[str]:
        raw = re.sub(r"\r\n", "\n", raw)
        blocks = re.split(r"\n\s*\n", raw)
        merged = []
        buffer = []

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            buffer.append(block)
            if sum(len(x) for x in buffer) > 700:
                merged.append("\n\n".join(buffer))
                buffer = []

        if buffer:
            merged.append("\n\n".join(buffer))

        return merged

    def _bm25_score(self, query_tokens: List[str], doc_index: int) -> float:
        if not self.chunks or not query_tokens:
            return 0.0

        k1 = 1.5
        b = 0.75

        N = len(self.chunks)
        doc_len = len(self.doc_tokens[doc_index]) or 1
        term_counts = self.doc_term_counts[doc_index]

        score = 0.0
        for token in query_tokens:
            tf = term_counts.get(token, 0)
            if tf == 0:
                continue

            df = self.document_frequency.get(token, 0)
            idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
            denominator = tf + k1 * (1 - b + b * doc_len / (self.avg_doc_len or 1))
            score += idf * ((tf * (k1 + 1)) / denominator)

        return score

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = tokenize(query)

        scored = []
        for idx, chunk in enumerate(self.chunks):
            score = self._bm25_score(query_tokens, idx)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for rank, (score, chunk) in enumerate(scored[:top_k], start=1):
            results.append(
                {
                    "rank": rank,
                    "score": round(float(score), 4),
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "title": chunk.title,
                    "text": chunk.text,
                    "citation": f"{chunk.title} / {chunk.chunk_id}",
                }
            )
        return results

    def answer(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        results = self.search(question, top_k=top_k)

        if not results:
            return {
                "answer": (
                    "The approved internal documents do not contain enough information "
                    "to answer this question."
                ),
                "confidence": "low",
                "citations": [],
                "retrieved_chunks": [],
            }

        top_score = results[0]["score"]
        confidence = "high" if top_score >= 4.0 else "medium" if top_score >= 1.5 else "low"

        evidence_lines = []
        citations = []
        for item in results:
            snippet = item["text"].replace("\n", " ")
            if len(snippet) > 450:
                snippet = snippet[:450].rsplit(" ", 1)[0] + "..."
            evidence_lines.append(f"- {snippet} [{item['citation']}]")
            citations.append(item["citation"])

        answer = (
            "Based only on the approved internal document evidence, the relevant information is:\n\n"
            + "\n".join(evidence_lines)
        )

        if confidence == "low":
            answer = (
                "The retrieval confidence is low. Do not treat this as a final authoritative answer.\n\n"
                + answer
            )

        return {
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
            "retrieved_chunks": results,
        }
