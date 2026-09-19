from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Callable

from src import Document, EmbeddingStore, FixedSizeChunker, RecursiveChunker, SentenceChunker

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_DATA_DIR = Path("data/library-uit")
DEFAULT_OUTPUT = Path("ket_qua_benchmark.txt")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    _, frontmatter, body = text.split("---", 2)
    metadata = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, body.strip()


def normalize_text(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    ).lower()


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", normalize_text(text), flags=re.UNICODE)


class LexicalEmbedder:
    """Small bag-of-words embedder for the benchmark script.

    It avoids external model downloads but still gives retrieval behavior that is
    more meaningful than the MD5-based MockEmbedder used by the unit tests.
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self._backend_name = "hashed lexical benchmark embedder"

    def __call__(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for token in tokenize(text):
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            vector[int(digest, 16) % self.dim] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class HeadingChunker:
    """Chunk Markdown by heading/section boundaries."""

    def chunk(self, text: str) -> list[str]:
        lines = text.splitlines()
        chunks: list[str] = []
        current: list[str] = []

        for line in lines:
            if line.startswith("#") and current:
                chunk = "\n".join(current).strip()
                if chunk:
                    chunks.append(chunk)
                current = [line]
            else:
                current.append(line)

        chunk = "\n".join(current).strip()
        if chunk:
            chunks.append(chunk)
        return chunks


def make_chunker(strategy: str):
    if strategy == "fixed":
        return FixedSizeChunker(chunk_size=350, overlap=50)
    if strategy == "recursive":
        return RecursiveChunker(chunk_size=450)
    if strategy == "sentence":
        return SentenceChunker(max_sentences_per_chunk=4)
    if strategy == "heading":
        return HeadingChunker()
    raise ValueError(f"Unknown strategy: {strategy}")


def load_chunk_documents(data_dir: Path, strategy: str) -> list[Document]:
    chunker = make_chunker(strategy)
    documents: list[Document] = []

    for path in sorted(data_dir.glob("*.md")):
        metadata, body = parse_frontmatter(path)
        doc_id = metadata.get("doc_id", path.stem)
        chunks = chunker.chunk(body)
        for index, chunk in enumerate(chunks, start=1):
            chunk_metadata = dict(metadata)
            chunk_metadata["doc_id"] = doc_id
            chunk_metadata["source_file"] = str(path)
            chunk_metadata["chunk_index"] = index
            documents.append(
                Document(
                    id=f"{doc_id}::chunk-{index:02d}",
                    content=chunk,
                    metadata=chunk_metadata,
                )
            )
    return documents


def load_queries(data_dir: Path) -> list[dict[str, str]]:
    path = data_dir / "benchmark_queries.csv"
    with path.open(encoding="utf-8", newline="") as query_file:
        return list(csv.DictReader(query_file))


def parse_filter(raw_filter: str) -> dict[str, str] | None:
    raw_filter = (raw_filter or "").strip()
    if not raw_filter:
        return None
    return json.loads(raw_filter)


def run_benchmark(data_dir: Path, strategy: str) -> str:
    docs = load_chunk_documents(data_dir, strategy)
    queries = load_queries(data_dir)

    store = EmbeddingStore(collection_name=f"bench_{strategy}", embedding_fn=LexicalEmbedder())
    store.add_documents(docs)

    lines = [
        f"Benchmark corpus: {data_dir}",
        f"Strategy: {strategy}",
        f"Chunks loaded: {store.get_collection_size()}",
        f"Queries: {len(queries)}",
        "",
    ]

    for number, row in enumerate(queries, start=1):
        metadata_filter = parse_filter(row.get("metadata_filter", ""))
        results = store.search_with_filter(row["query"], top_k=3, metadata_filter=metadata_filter)
        expected_doc_id = row.get("expected_doc_id", "")

        lines.extend(
            [
                f"Query {number}: {row['query']}",
                f"Gold: {row['gold_answer']}",
                f"Filter: {metadata_filter}",
                f"Expected doc: {expected_doc_id}",
                "Top-3:",
            ]
        )

        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]
            doc_id = metadata.get("doc_id", "")
            chunk_index = metadata.get("chunk_index", "")
            relevant = "YES" if doc_id == expected_doc_id else "NO"
            preview = " ".join(result["content"].split())[:180]
            lines.append(
                f"  {rank}. score={result['score']:.3f} "
                f"doc_id={doc_id} chunk={chunk_index} relevant={relevant}"
            )
            lines.append(f"     {preview}")
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the L3A retrieval benchmark.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument(
        "--strategy",
        choices=["heading", "fixed", "recursive", "sentence"],
        default="heading",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = run_benchmark(args.data_dir, args.strategy)
    print(output)
    args.output.write_text(output + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
