"""
Collect public r/TrueFilm comments from the pullpush.io archive across several
time windows, so the sample spreads over many threads and films rather than one.
Saves raw text to raw_comments.csv. Annotation happens in a later step, by hand.
"""

import csv
import json
import time
import urllib.parse
import urllib.request

SUBREDDIT = "TrueFilm"
SIZE = 100

# Eight windows spanning roughly early 2023 to mid 2025, so we don't pull one
# topic. Each value is a UTC epoch; we ask for the SIZE newest comments before it.
WINDOWS = [
    1747000000,  # ~May 2025
    1738000000,  # ~Jan 2025
    1729000000,  # ~Oct 2024
    1720000000,  # ~Jul 2024
    1710000000,  # ~Mar 2024
    1700000000,  # ~Nov 2023
    1688000000,  # ~Jun 2023
    1675000000,  # ~Feb 2023
]

JUNK_BODIES = {"[deleted]", "[removed]", "", None}
BOT_AUTHORS = {"AutoModerator", "[deleted]"}


def fetch(before):
    params = urllib.parse.urlencode(
        {"subreddit": SUBREDDIT, "size": SIZE, "sort": "desc", "before": before}
    )
    url = f"https://api.pullpush.io/reddit/search/comment/?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "takemeter-collector/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8")).get("data", [])


def main():
    seen = set()
    rows = []
    for before in WINDOWS:
        try:
            data = fetch(before)
        except Exception as e:
            print(f"window {before}: error {e}")
            continue
        kept = 0
        for c in data:
            cid = c.get("id")
            body = c.get("body")
            author = c.get("author")
            if cid in seen:
                continue
            if body in JUNK_BODIES or author in BOT_AUTHORS:
                continue
            body_stripped = body.strip()
            if len(body_stripped) < 3:
                continue
            seen.add(cid)
            rows.append(
                {
                    "id": cid,
                    "created_utc": c.get("created_utc"),
                    "score": c.get("score"),
                    "link_id": c.get("link_id"),
                    "permalink": c.get("permalink"),
                    "body": body_stripped,
                }
            )
            kept += 1
        print(f"window {before}: fetched {len(data)}, kept {kept}, total {len(rows)}")
        time.sleep(1.5)

    with open("raw_comments.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "created_utc", "score", "link_id", "permalink", "body"]
        )
        writer.writeheader()
        writer.writerows(rows)

    threads = {r["link_id"] for r in rows}
    print(f"\nDONE: {len(rows)} unique comments across {len(threads)} threads -> raw_comments.csv")


if __name__ == "__main__":
    main()
