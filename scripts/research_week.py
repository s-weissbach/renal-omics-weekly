#!/usr/bin/env python3
"""Find and rank recent renal/omics papers using the free Europe PMC API."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
ROOT = Path(__file__).resolve().parents[1]

QUERIES = (
    '(kidney OR renal OR nephrology OR nephropathy OR cardiorenal) AND FIRST_PDATE:[{start} TO {end}]',
    '("spatial transcriptomics" OR "single-cell" OR "single cell" OR "spatial omics" OR multi-omics OR multiomics OR "foundation model") AND FIRST_PDATE:[{start} TO {end}]',
)

TOPIC_WEIGHTS = {
    "kidney": 7.0,
    "renal": 7.0,
    "nephro": 6.0,
    "cardiorenal": 7.0,
    "spatial transcript": 5.0,
    "spatial omics": 5.0,
    "single-cell": 4.0,
    "single cell": 4.0,
    "multi-omics": 4.0,
    "multiomics": 4.0,
    "foundation model": 4.0,
    "machine learning": 3.0,
    "deep learning": 3.0,
    "computational": 2.0,
}

NOVELTY_TERMS = (
    "method", "framework", "model", "atlas", "alignment", "integration",
    "lineage", "trajectory", "multimodal", "multi-modal", "algorithm",
)
TRANSLATION_TERMS = (
    "patient", "human", "clinical", "therapeutic", "drug", "cohort",
    "biomarker", "injury", "fibrosis", "disease",
)
PENALTY_TERMS = ("review", "meta-analysis", "case report", "bibliometric")


def fetch(query: str, page_size: int = 100) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "query": query,
            "format": "json",
            "resultType": "core",
            "pageSize": page_size,
        }
    )
    req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": "RenalOmicsWeekly/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response:
        payload = json.load(response)
    return payload.get("resultList", {}).get("result", [])


def clean(value: str | None) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def paper_id(paper: dict) -> str:
    if paper.get("doi"):
        return "doi:" + paper["doi"].lower()
    if paper.get("pmid"):
        return "pmid:" + paper["pmid"]
    return "title:" + re.sub(r"\W+", " ", clean(paper.get("title")).lower()).strip()


def score(paper: dict) -> tuple[float, list[str]]:
    title = clean(paper.get("title")).lower()
    abstract = clean(paper.get("abstractText")).lower()
    combined = title + " " + abstract
    value = 0.0
    reasons: list[str] = []
    for term, weight in TOPIC_WEIGHTS.items():
        if term in combined:
            value += weight * (1.5 if term in title else 1.0)
    novelty_hits = [term for term in NOVELTY_TERMS if term in combined]
    translation_hits = [term for term in TRANSLATION_TERMS if term in combined]
    value += min(len(novelty_hits), 4) * 1.4
    value += min(len(translation_hits), 4) * 0.8
    if paper.get("source") == "PPR":
        value += 1.0
        reasons.append("new preprint")
    if paper.get("isOpenAccess") == "Y":
        value += 1.0
        reasons.append("open access")
    if novelty_hits:
        reasons.append("method novelty: " + ", ".join(novelty_hits[:3]))
    if translation_hits:
        reasons.append("translation: " + ", ".join(translation_hits[:3]))
    for term in PENALTY_TERMS:
        if term in title or term in clean(" ".join(paper.get("pubTypeList", {}).get("pubType", []))).lower():
            value -= 7.0
            reasons.append("lower priority: " + term)
    if not abstract:
        value -= 3.0
        reasons.append("no abstract")
    return round(value, 2), reasons


def normalize(paper: dict) -> dict:
    value, reasons = score(paper)
    doi = paper.get("doi")
    pmid = paper.get("pmid")
    if doi:
        stable_url = "https://doi.org/" + doi
    elif pmid:
        stable_url = "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/"
    else:
        stable_url = paper.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url", "")
    return {
        "id": paper_id(paper),
        "score": value,
        "title": clean(paper.get("title")),
        "authors": clean(paper.get("authorString")),
        "date": paper.get("firstPublicationDate") or paper.get("electronicPublicationDate"),
        "journal": clean(paper.get("journalTitle")),
        "doi": doi,
        "pmid": pmid,
        "source": paper.get("source"),
        "open_access": paper.get("isOpenAccess") == "Y",
        "stable_url": stable_url,
        "abstract": clean(paper.get("abstractText")),
        "ranking_reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--end", default=dt.date.today().isoformat(), help="inclusive end date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    end = dt.date.fromisoformat(args.end)
    start = end - dt.timedelta(days=args.days)
    seen_path = ROOT / "state" / "seen.json"
    seen = json.loads(seen_path.read_text()) if seen_path.exists() else {}
    excluded = set(seen.get("published_papers", []))

    unique: dict[str, dict] = {}
    for template in QUERIES:
        query = template.format(start=start.isoformat(), end=end.isoformat())
        for raw in fetch(query):
            normalized = normalize(raw)
            if normalized["id"] not in excluded:
                previous = unique.get(normalized["id"])
                if not previous or normalized["score"] > previous["score"]:
                    unique[normalized["id"]] = normalized

    ranked = sorted(unique.values(), key=lambda item: (-item["score"], item.get("date") or ""))
    payload = {
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "candidates": ranked[: args.limit],
    }
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
