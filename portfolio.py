import requests
from datetime import datetime
from html import escape
from pathlib import Path

USERNAME = "Arghnews"

# Read the GitHub token securely from secret.txt
TOKEN = Path("secret.txt").read_text().strip()

# Manual showcase section with tags
SHOWCASE_HTML = """
<h2>Projects</h2>
<ul>

  <li>
    <a href="https://github.com/Arghnews/cricket-scorer"><strong>Cricket scorer</strong><br></a>
    This project connects a mains-powered LED cricket scoreboard over WiFi to a laptop or Raspberry Pi control box.
    <div class="tags">
      <span class="tag">Python 3</span>
      <span class="tag">Raspberry Pi</span>
      <span class="tag">Bash</span>
      <span class="tag">systemd</span>
      <span class="tag">Reliable UDP</span>
      <span class="tag">PySimpleGUI</span>
      <span class="tag">smbus2/I2C</span>
      <span class="tag">PyInstaller</span>
      <span class="tag">xlwings</span>
    </div>
  </li>

  <li>
    <a href="https://github.com/Arghnews/wordsearch_solver"><strong>Wordsearch Solver</strong><br></a>
    C++17 library & ImGui app to solve wordsearches with trie backends and benchmarking.
    Used forked gperftools with ability to pause and resume profiling <a href="https://github.com/Arghnews/gperftools">here</a>.
    <div class="tags">
      <span class="tag">C++17</span>
      <span class="tag">ImGui</span>
      <span class="tag">Trie</span>
      <span class="tag">range-v3</span>
      <span class="tag">CMake</span>
      <span class="tag">conan</span>
      <span class="tag">Google benchmark</span>
      <span class="tag">catch2</span>
      <span class="tag">Boost</span>
    </div>
  </li>

  <li>
    <a href="https://github.com/Arghnews/pinger"><strong>Simple raspberry pi push pinger</strong><br></a>
    A simple script to ping another raspberry pi and send an email notification on connection loss.
    <div class="tags">
      <span class="tag">Python 3</span>
      <span class="tag">Raspberry Pi</span>
      <span class="tag">Email API: mailjet_rest</span>
    </div>
  </li>

  <li>
    <a href="https://github.com/Arghnews/bashrc"><strong>My bashrc setup</strong><br></a>
    Script to bootstrap my bash environment on fresh Linux installs. Vim setup is out of date. Assumes <code>rg</code>
    <div class="tags">
      <span class="tag">Bash</span>
      <span class="tag">Linux</span>
      <span class="tag">Dotfiles</span>
    </div>
  </li>

  <li>
    <a href="https://github.com/Arghnews/chickenpi"><strong>Raspberry pi chicken coop controller</strong><br></a>
    Raspberry Pi GPIO controller with camera, web UI and sensors.
    Code is a mess, but worked for years.
    <div class="tags">
      <span class="tag">Python 3</span>
      <span class="tag">PHP</span>
      <span class="tag">GPIO</span>
      <span class="tag">Raspberry Pi</span>
      <span class="tag">REST APIs</span>
    </div>
  </li>

</ul>
<hr>
"""

# Header with email
CUSTOM_HEADER_HTML = """
<h1>Justin Riddell – Portfolio</h1>
<p>C++ • Linux • Python</p>

<p>Contact: <a href="mailto:arghnews@hotmail.co.uk">arghnews@hotmail.co.uk</a></p>

<p><a href="#open-source-prs">See Open Source Contributions to fmtlib and llvm at the bottom of this page</a></p>

<p>This page is auto-generated via Python.</p>
<hr>
"""

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "Mozilla/5.0",
}


def fetch_prs(username):
    """Fetch both merged and closed PRs, sorted newest first."""
    url = "https://api.github.com/search/issues"
    params = {
        "q": f"author:{username} is:pr is:closed archived:false",
        "per_page": 100,
    }

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    items = r.json()["items"]

    # Sort newest first using merged_at or closed_at
    def sort_key(it):
        merged_at = it.get("pull_request", {}).get("merged_at")
        closed_at = it.get("closed_at")
        ts = merged_at or closed_at
        return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else datetime.min

    items.sort(key=sort_key, reverse=True)
    return items


def format_date(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%b %d %Y").replace(" 0", " ")


def pr_to_html(item):
    html_url = item["html_url"]
    parts = html_url.split("/")
    if len(parts) >= 6:
        owner = parts[3]
        repo = parts[4]
        repo_full = f"{owner}/{repo}"
    else:
        repo_full = html_url

    title = escape(item["title"])
    number = item["number"]
    author = item["user"]["login"]

    merged_at = item.get("pull_request", {}).get("merged_at")
    closed_at = item.get("closed_at")

    if merged_at:
        date = format_date(merged_at)
        status = f"#{number} by {author} was merged on {date}"
        bullet = "Merged"
    else:
        date = format_date(closed_at) if closed_at else "Unknown date"
        status = f"#{number} by {author} was closed on {date}"
        bullet = "Closed"

    return f"""
<li>
  <strong>{repo_full}:</strong>
  <a href="{html_url}">{title}</a><br>
  <small>{status}</small><br>
  <small>• {bullet}</small>
</li>
""".strip()


def build_html(pr_items):
    pr_list_html = "\n".join(pr_to_html(item) for item in pr_items)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{USERNAME} – Portfolio</title>
<style>
  body {{
    font-family: system-ui, sans-serif;
    max-width: 850px;
    margin: 40px auto;
    line-height: 1.6;
    padding: 0 20px;
  }}
  ul {{
    padding-left: 20px;
  }}
  .tags {{
    margin: 0.25rem 0 0.75rem 0;
  }}
  .tag {{
    display: inline-block;
    padding: 2px 6px;
    margin: 0 4px 4px 0;
    border-radius: 4px;
    background: #eee;
    font-size: 0.8rem;
  }}
</style>
</head>
<body>

{CUSTOM_HEADER_HTML}

{SHOWCASE_HTML}

<h2 id="open-source-prs">Open Source Contributions</h2>

<ul>
{pr_list_html}
</ul>

</body>
</html>
"""


def main():
    items = fetch_prs(USERNAME)
    html = build_html(items)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Wrote index.html — open it in your browser or run:")
    print("  python -m http.server")


if __name__ == "__main__":
    main()
