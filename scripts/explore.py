"""Erkundung der Seite abfall-lro.de (laeuft in GitHub Actions).

Schreibt alle Ergebnisse nach debug/ damit man die echten Parameter sieht.
Nur Python-Standardbibliothek.
"""
import datetime
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BASE = "https://www.abfall-lro.de"
OUT = Path("debug")
OUT.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ORT = "Tessin"

report = []


def log(msg):
    print(msg)
    report.append(msg)


def get(url, method="GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read() if method == "GET" else b""
            return r.status, r.headers.get("Content-Type", ""), body, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read(), url
    except Exception as e:  # noqa: BLE001
        return None, "", str(e).encode(), url


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms, self.links = [], []
        self._form = self._select = self._a = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._form = {"attrs": a, "fields": []}
            self.forms.append(self._form)
        elif tag in ("input", "textarea") and self._form is not None:
            self._form["fields"].append({"tag": tag, **a})
        elif tag == "select":
            self._select = {"tag": "select", **a, "options": []}
            if self._form is not None:
                self._form["fields"].append(self._select)
        elif tag == "option" and self._select is not None:
            self._select["options"].append({"value": a.get("value"), "text": ""})
        elif tag == "a":
            self._a = {"href": a.get("href", ""), "text": ""}
            self.links.append(self._a)

    def handle_endtag(self, tag):
        if tag == "form":
            self._form = None
        elif tag == "select":
            self._select = None
        elif tag == "a":
            self._a = None

    def handle_data(self, data):
        if self._select is not None and self._select["options"]:
            self._select["options"][-1]["text"] += data.strip()
        if self._a is not None:
            self._a["text"] += data


def main():
    year = datetime.date.today().year
    log(f"Datum: {datetime.datetime.now().isoformat()}")

    pages = {"main": f"{BASE}/de/abfuhrtermine/"}
    for y in (year - 1, year, year + 1):
        pages[f"index-{y}"] = f"{BASE}/de/abfuhrtermine/index-{y}.php"

    letters = set()
    for name, url in pages.items():
        st, ct, body, final = get(url)
        log(f"\n=== {name}: {url} -> {st} {ct} (final {final}), {len(body)} bytes")
        if st != 200:
            continue
        text = body.decode("utf-8", "replace")
        (OUT / f"{name}.html").write_text(text, encoding="utf-8")
        p = FormParser()
        p.feed(text)
        for i, f in enumerate(p.forms):
            log(f"  FORM {i}: {f['attrs']}")
            for fld in f["fields"]:
                if fld["tag"] == "select":
                    opts = fld["options"]
                    hits = [o for o in opts if ORT.lower() in (o["text"] + str(o["value"])).lower()]
                    log(f"    select name={fld.get('name')} id={fld.get('id')} ({len(opts)} Optionen) erste: {opts[:6]} Tessin: {hits}")
                else:
                    log(f"    {fld}")
        for ln in p.links:
            t = " ".join(ln["text"].split())
            if ORT.lower() in t.lower() or "ical" in ln["href"].lower() or ".ics" in ln["href"].lower():
                log(f"  LINK '{t}' -> {ln['href']}")
                m = re.search(r"/([^/]+)\.pdf$", ln["href"])
                if m and ORT.lower() in t.lower():
                    letters.add(m.group(1))
        for m in re.finditer(r"[^\"'\s]*(ical|\.ics|kalender)[^\"'\s]*", text, re.I):
            if "/" in m.group(0):
                log(f"  ERWAEHNUNG: {html.unescape(m.group(0))[:200]}")
        for m in re.finditer(r"<script[^>]+src=[\"']([^\"']+)", text):
            log(f"  SCRIPT: {m.group(1)}")
        for m in re.finditer(r"(?i)(stand|aktualisiert|geändert)[^<]{0,60}\d{1,2}\.\d{1,2}\.\d{4}", text):
            log(f"  STAND: {m.group(0)}")

    log(f"\nGefundene Codes fuer {ORT}: {sorted(letters)}")

    # PDF-Ordner pruefen
    for y in (year, year + 1):
        for code in sorted(letters) or ["x"]:
            url = f"{BASE}/default-wAssets/docs/abfuhrtermine/{y}/pdf/{code}.pdf"
            st, ct, body, _ = get(url)
            log(f"PDF {y} {code}: {st} {ct} {len(body)} bytes")

    ical = f"{BASE}/default-wGlobal/wGlobal/abfuhrtermine/ical.php"
    for code in sorted(letters):
        for y in (year, year + 1):
            for variant, extra in (("4w", {"black": "4w"}), ("4w+erinnerung", {"black": "4w", "reminder": "18"})):
                params = {"letters": code, "year": y, "green": "", "yellow": "y", "blue": "y", **extra}
                url = ical + "?" + urllib.parse.urlencode(params)
                st, ct, body, _ = get(url)
                text = body.decode("utf-8", "replace")
                n = text.count("BEGIN:VEVENT")
                log(f"ICAL {variant} {y} {code}: {st} {ct} {len(body)} bytes, {n} Events -> {url}")
                (OUT / f"ical_{code}_{y}_{variant}.txt").write_text(text, encoding="utf-8")

    (OUT / "report.txt").write_text("\n".join(report), encoding="utf-8")
    (OUT / "codes.json").write_text(json.dumps(sorted(letters)), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
