import argparse
import html.parser
import http.cookiejar
import os
import urllib.parse
import urllib.request

from tqdm import tqdm

FILE_ID = "1sQOUN4IvYdX26AaFS7tZ-A5R_A3ThtsL"
INITIAL_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DEST_PATH = os.path.join(DATA_DIR, "qc_pune.duckdb")
CHUNK_SIZE = 128 * 1024  # 128 KB


class _FormParser(html.parser.HTMLParser):
    """Extract action URL and hidden fields from the virus-scan confirmation form."""

    def __init__(self):
        super().__init__()
        self.action = None
        self.fields = {}
        self._in_form = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form" and attrs.get("id") == "download-form":
            self._in_form = True
            self.action = attrs.get("action", "")
        if self._in_form and tag == "input" and attrs.get("type") == "hidden":
            self.fields[attrs["name"]] = attrs.get("value", "")


def _build_confirm_url(page_html: str) -> str:
    parser = _FormParser()
    parser.feed(page_html)
    qs = urllib.parse.urlencode(parser.fields)
    return f"{parser.action}?{qs}"


def download(force=False):
    if os.path.exists(DEST_PATH) and not force:
        print(f"File already exists: {DEST_PATH}")
        print("Use --force to re-download.")
        return

    os.makedirs(DATA_DIR, exist_ok=True)

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    print(f"Downloading to {DEST_PATH} ...")
    response = opener.open(INITIAL_URL)

    # Large files trigger a virus-scan confirmation page.
    # Parse it to get the real download URL.
    if response.headers.get_content_type() == "text/html":
        confirm_url = _build_confirm_url(response.read().decode())
        response = opener.open(confirm_url)

    total_size = int(response.headers.get("Content-Length", 0))

    with (
        tqdm(total=total_size, unit="B", unit_scale=True, desc="qc_pune.duckdb") as bar,
        open(DEST_PATH, "wb") as f,
    ):
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            f.write(chunk)
            bar.update(len(chunk))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download workshop DuckDB file")
    parser.add_argument("--force", action="store_true", help="Re-download even if file exists")
    args = parser.parse_args()
    download(force=args.force)
