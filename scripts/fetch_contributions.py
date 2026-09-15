#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint (the same fragment the profile page itself uses) and
write data/contributions.json with raw days plus derived stats
(total contributions, current streak, longest streak, best day, active days).

No token, no auth, no GraphQL -- just the public HTML GitHub already serves.
Run daily by .github/workflows/update-profile-art.yml.
"""
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "kamesprabum")
URL = f"https://github.com/users/{USERNAME}/contributions"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")
OUT_PATH = os.path.join(DATA_DIR, "contributions.json")


def fetch_days():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print(f"Warning: no calendar cells found for user '{USERNAME}'. Markup may have changed.", file=sys.stderr)
        return []

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        
        # Determine count: either from tooltip or data-level or text
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        
        count = 0
        if text:
            if re.search(r"no contributions", text, re.I):
                count = 0
            else:
                m = re.search(r"(\d+)\s+contribution", text, re.I)
                if m:
                    count = int(m.group(1))
                else:
                    m2 = re.match(r"(\d+)", text)
                    if m2:
                        count = int(m2.group(1))
        else:
            # Fallback to data-level heuristic if tooltip is absent
            level = int(td.get("data-level", 0))
            count = level  # basic estimation if count not in text

        days.append({"date": date, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    if not days:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": {"date": None, "count": 0},
            "active_days": 0,
            "days": [],
        }

    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    
    # Best day
    best_day = max(days, key=lambda d: d["count"]) if days else {"date": None, "count": 0}

    # Streaks calculation
    longest_streak = 0
    current_run = 0
    for d in days:
        if d["count"] > 0:
            current_run += 1
            if current_run > longest_streak:
                longest_streak = current_run
        else:
            current_run = 0

    # Current streak (looking back from today / last day)
    current_streak = 0
    today = datetime.date.today()
    # Check reversed days
    for d in reversed(days):
        d_date = datetime.date.fromisoformat(d["date"])
        # Allow today or yesterday as start of current streak
        if d["count"] > 0:
            current_streak += 1
        elif (today - d_date).days > 1:
            # If a zero is encountered older than yesterday, streak ends
            break

    return {
        "username": USERNAME,
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "active_days": active_days,
        "best_day": best_day,
        "days": days,
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Fetching GitHub contributions for {USERNAME}...")
    days = fetch_days()
    stats = compute_stats(days)
    
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    
    print(f"Wrote {len(stats['days'])} days and stats to {OUT_PATH}")
    print(f"Total contributions: {stats['total']} | Current streak: {stats['current_streak']} | Longest: {stats['longest_streak']}")


if __name__ == "__main__":
    main()
