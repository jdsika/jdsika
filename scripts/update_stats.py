#!/usr/bin/env python3
"""Patch live GitHub stats into profile-dark.svg / profile-light.svg.

Uses only the Python standard library. Requires GITHUB_TOKEN (the default
Actions token is sufficient; it sees public data only, which is intentional:
every number on the profile stays publicly verifiable).
"""

import json
import os
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

LOGIN = os.environ.get("GH_LOGIN", "jdsika")
TOKEN = os.environ["GITHUB_TOKEN"]
JOINED = date(2015, 4, 14)
ROOT = Path(__file__).resolve().parent.parent


def graphql(query: str) -> dict:
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise SystemExit(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


current_year = datetime.now(timezone.utc).year

user = graphql(
    f"""
query {{
  user(login: "{LOGIN}") {{
    followers {{ totalCount }}
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{
      totalCount
      nodes {{ stargazerCount }}
    }}
    repositoriesContributedTo(
      contributionTypes: [COMMIT, PULL_REQUEST]
      includeUserRepositories: false
    ) {{ totalCount }}
  }}
}}"""
)["user"]

# contributionsCollection is limited to one year per range and a few aliases
# per query before hitting resource limits, so fetch the years in chunks.
commits = prs = issues = reviews = 0
years = list(range(JOINED.year, current_year + 1))
CHUNK = 3
for start in range(0, len(years), CHUNK):
    yearly = "\n".join(
        f'y{year}: contributionsCollection('
        f'from: "{year}-01-01T00:00:00Z", to: "{year}-12-31T23:59:59Z") '
        "{ totalCommitContributions totalPullRequestContributions "
        "totalIssueContributions totalPullRequestReviewContributions }"
        for year in years[start : start + CHUNK]
    )
    chunk = graphql(f'query {{ user(login: "{LOGIN}") {{ {yearly} }} }}')["user"]
    for value in chunk.values():
        commits += value["totalCommitContributions"]
        prs += value["totalPullRequestContributions"]
        issues += value["totalIssueContributions"]
        reviews += value["totalPullRequestReviewContributions"]

today = datetime.now(timezone.utc).date()
months = (today.year - JOINED.year) * 12 + (today.month - JOINED.month)
if today.day < JOINED.day:
    months -= 1
uptime = f"{months // 12} years, {months % 12} months (joined {JOINED.isoformat()})"

values = {
    "uptime": uptime,
    "repos": str(user["repositories"]["totalCount"]),
    "contrib": str(user["repositoriesContributedTo"]["totalCount"]),
    "commits": f"{commits:,}",
    "prs": f"{prs:,}",
    "reviews": f"{reviews:,}",
    "issues": f"{issues:,}",
    "stars": f"{sum(n['stargazerCount'] for n in user['repositories']['nodes']):,}",
    "followers": str(user["followers"]["totalCount"]),
    "updated": today.isoformat(),
}

for name in ("profile-dark.svg", "profile-light.svg"):
    path = ROOT / name
    svg = path.read_text()
    for key, value in values.items():
        svg = re.sub(
            rf'(<tspan[^>]*id="{key}"[^>]*>)[^<]*(</tspan>)',
            rf"\g<1>{value}\g<2>",
            svg,
        )
    path.write_text(svg)

print(json.dumps(values, indent=2))
