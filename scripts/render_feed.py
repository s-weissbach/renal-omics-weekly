#!/usr/bin/env python3
"""Render a Spotify-compatible RSS feed and a small public archive page."""

from __future__ import annotations

import datetime as dt
import email.utils
import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ITUNES = "http://www.itunes.com/dtds/podcast-1.0.dtd"
CONTENT = "http://purl.org/rss/1.0/modules/content/"
ATOM = "http://www.w3.org/2005/Atom"
ET.register_namespace("itunes", ITUNES)
ET.register_namespace("content", CONTENT)
ET.register_namespace("atom", ATOM)


def text(parent: ET.Element, tag: str, value: str | int | None, attrib: dict | None = None) -> ET.Element | None:
    if value in (None, ""):
        return None
    node = ET.SubElement(parent, tag, attrib or {})
    node.text = str(value)
    return node


def rfc2822(value: str) -> str:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return email.utils.format_datetime(parsed)


def load_episodes() -> list[dict]:
    episodes = []
    for path in sorted((ROOT / "episodes").glob("*/episode.json"), reverse=True):
        episode = json.loads(path.read_text())
        if episode.get("audio_url"):
            episodes.append(episode)
    return sorted(episodes, key=lambda item: item["published_at"], reverse=True)


def build_feed(config: dict, episodes: list[dict]) -> None:
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    text(channel, "title", config["title"])
    text(channel, "link", config["base_url"] + "/")
    text(channel, "description", config["description"])
    text(channel, "language", config.get("language", "en"))
    text(channel, f"{{{ITUNES}}}author", config["author"])
    text(channel, f"{{{ITUNES}}}summary", config["description"])
    text(channel, f"{{{ITUNES}}}subtitle", config.get("subtitle"))
    text(channel, f"{{{ITUNES}}}explicit", "true" if config.get("explicit") else "false")
    ET.SubElement(channel, f"{{{ITUNES}}}image", {"href": config["cover_url"]})
    category = ET.SubElement(channel, f"{{{ITUNES}}}category", {"text": config["category"]})
    if config.get("subcategory"):
        ET.SubElement(category, f"{{{ITUNES}}}category", {"text": config["subcategory"]})
    owner = ET.SubElement(channel, f"{{{ITUNES}}}owner")
    text(owner, f"{{{ITUNES}}}name", config.get("owner_name"))
    text(owner, f"{{{ITUNES}}}email", config.get("owner_email"))
    ET.SubElement(channel, f"{{{ATOM}}}link", {"href": config["feed_url"], "rel": "self", "type": "application/rss+xml"})
    text(channel, "lastBuildDate", email.utils.format_datetime(dt.datetime.now(dt.timezone.utc)))

    for episode in episodes:
        item = ET.SubElement(channel, "item")
        text(item, "title", episode["title"])
        text(item, "guid", episode["guid"], {"isPermaLink": "false"})
        text(item, "pubDate", rfc2822(episode["published_at"]))
        text(item, "description", episode["summary"])
        text(item, f"{{{CONTENT}}}encoded", episode.get("show_notes_html", episode["summary"]))
        text(item, f"{{{ITUNES}}}summary", episode["summary"])
        text(item, f"{{{ITUNES}}}duration", episode.get("duration"))
        text(item, f"{{{ITUNES}}}explicit", "true" if episode.get("explicit") else "false")
        text(item, f"{{{ITUNES}}}episodeType", "full")
        ET.SubElement(
            item,
            "enclosure",
            {
                "url": episode["audio_url"],
                "length": str(episode["length_bytes"]),
                "type": episode["mime_type"],
            },
        )

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    DOCS.mkdir(parents=True, exist_ok=True)
    tree.write(DOCS / "feed.xml", encoding="utf-8", xml_declaration=True)


def build_index(config: dict, episodes: list[dict]) -> None:
    cards = []
    for episode in episodes:
        papers = "".join(
            f'<li><a href="{html.escape(p["url"], quote=True)}">{html.escape(p["title"])}</a></li>'
            for p in episode.get("papers", [])
        )
        cards.append(
            f'''<article><p class="date">{html.escape(episode["published_at"][:10])}</p>
<h2>{html.escape(episode["title"])}</h2><p>{html.escape(episode["summary"])}</p>
<audio controls preload="none" src="{html.escape(episode["audio_url"], quote=True)}"></audio>
<h3>Sources</h3><ul>{papers}</ul></article>'''
        )
    body = "\n".join(cards) or "<p>The first episode is being prepared.</p>"
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(config["title"])}</title><link rel="alternate" type="application/rss+xml" href="feed.xml" title="{html.escape(config["title"])}">
<style>body{{margin:0;background:#071c35;color:#effaff;font:17px/1.55 system-ui,sans-serif}}main{{max-width:760px;margin:auto;padding:40px 22px 80px}}header{{display:grid;grid-template-columns:150px 1fr;gap:24px;align-items:center}}img{{width:150px;border-radius:22px}}h1{{font-size:clamp(2rem,7vw,4rem);line-height:1;margin:.2em 0}}a{{color:#56e2dd}}article{{background:#0d2b4b;border:1px solid #18506d;border-radius:18px;padding:24px;margin-top:30px}}audio{{width:100%}}.date{{color:#92cdd1;text-transform:uppercase;letter-spacing:.08em;font-size:.8rem}}@media(max-width:550px){{header{{grid-template-columns:1fr}}}}</style></head>
<body><main><header><img src="cover.png" alt=""><div><h1>{html.escape(config["title"])}</h1><p>{html.escape(config["subtitle"])}</p><a href="feed.xml">RSS feed</a></div></header>{body}</main></body></html>'''
    (DOCS / "index.html").write_text(page)


def main() -> None:
    config = json.loads((ROOT / "podcast.json").read_text())
    episodes = load_episodes()
    build_feed(config, episodes)
    build_index(config, episodes)
    ET.parse(DOCS / "feed.xml")
    print(f"Rendered {len(episodes)} episode(s) to {DOCS / 'feed.xml'}")


if __name__ == "__main__":
    main()

