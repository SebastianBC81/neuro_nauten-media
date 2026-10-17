"""Kostenloser TikTok-Autoposter für @neuro_nauten (läuft als GitHub Action).

Postet fällige Videos (type REEL) aus autopost/queue.json zusätzlich auf TikTok,
über die offizielle Content Posting API (Direct Post, Datei-Upload).
Ergebnisse stehen in autopost/tiktok-posted.json. Ein Eintrag mit "tiktok": false
wird übersprungen.

Zugang: Secrets TT_CLIENT_KEY und TT_CLIENT_SECRET (aus dem TikTok-Entwicklerportal).
Der Zugangsschlüssel des Kontos liegt nur verschlüsselt in autopost/tiktok-token.enc
(AES-256, Schlüssel = TT_CLIENT_SECRET); er wird nie ausgegeben.

Aufrufe:
  python3 autopost/tiktok.py            fällige Videos posten
  TT_CODE=... python3 autopost/tiktok.py connect   Konto verbinden (Code von der Rückmeldeseite)
Solange TikTok die App nicht geprüft hat, erlaubt TikTok nur private Beiträge (SELF_ONLY).
"""
import datetime as dt, json, os, subprocess, sys, time, urllib.parse, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post import ROOT, Q, load, save, now, limit_tags  # noqa: E402

TP = os.path.join(ROOT, "autopost", "tiktok-posted.json")
TOK = os.path.join(ROOT, "autopost", "tiktok-token.enc")
STATUS = os.path.join(ROOT, "autopost", "tiktok-selbsttest.txt")
API = "https://open.tiktokapis.com/v2"
REDIRECT = "https://sebastianbc81.github.io/neuro_nauten-media/tiktok/callback.html"
KEY = os.environ.get("TT_CLIENT_KEY", "").strip()  # beim Einfügen rutscht leicht ein Zeilenumbruch mit
SECRET = os.environ.get("TT_CLIENT_SECRET", "").strip()
MAX_LATE = dt.timedelta(hours=12)
MAX_TRIES = 3


def clean(s):
    """Entfernt Geheimnisse aus Fehlertexten."""
    s = str(s)
    for v in [SECRET, KEY] + [v for v in (_tok or {}).values() if isinstance(v, str) and len(v) > 20]:
        if v:
            s = s.replace(v, "***")
    return s


_tok = None


def read_token():
    global _tok
    if not os.path.exists(TOK):
        return None
    out = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-a", "-A",
                          "-pass", "env:TT_CLIENT_SECRET", "-in", TOK], capture_output=True, check=True)
    _tok = json.loads(out.stdout)
    return _tok


def write_token(tok):
    global _tok
    _tok = tok
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-salt", "-a", "-A",
                    "-pass", "env:TT_CLIENT_SECRET", "-out", TOK], input=json.dumps(tok).encode(), check=True)


def http(method, url, data=None, headers=None, raw=False, timeout=120):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, (body if raw else (json.loads(body) if body else {}))
    except urllib.error.HTTPError as e:
        raise RuntimeError(clean(f"TikTok {e.code}: {e.read().decode(errors='replace')[:400]}")) from None


def oauth(**params):
    data = urllib.parse.urlencode(dict(client_key=KEY, client_secret=SECRET, **params)).encode()
    _, r = http("POST", f"{API}/oauth/token/", data, {"Content-Type": "application/x-www-form-urlencoded"})
    if "access_token" not in r:
        raise RuntimeError(clean(f"Token-Fehler: {r.get('error')} {r.get('error_description')}"))
    t = now()
    return {"access_token": r["access_token"], "refresh_token": r["refresh_token"], "open_id": r.get("open_id"),
            "scope": r.get("scope"), "expires_at": (t + dt.timedelta(seconds=r["expires_in"])).isoformat(),
            "refresh_expires_at": (t + dt.timedelta(seconds=r["refresh_expires_in"])).isoformat()}


def access_token():
    tok = read_token()
    if not tok:
        return None
    if dt.datetime.fromisoformat(tok["expires_at"]) - now() < dt.timedelta(minutes=15):
        new = oauth(grant_type="refresh_token", refresh_token=tok["refresh_token"])
        new["since"] = tok.get("since")
        write_token(new)
        tok = new
    return tok["access_token"]


def api(path, token, body):
    _, r = http("POST", f"{API}/{path}", json.dumps(body).encode(),
                {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"})
    err = r.get("error", {})
    if err.get("code") not in (None, "ok"):
        raise RuntimeError(clean(f"{path}: {err.get('code')} {err.get('message')}"))
    return r.get("data", {})


def creator(token):
    return api("post/publish/creator_info/query/", token, {})


def video_file(m):
    if m.startswith("http"):
        with urllib.request.urlopen(m, timeout=180) as r:
            return r.read()
    with open(os.path.join(ROOT, m.lstrip("/")), "rb") as f:
        return f.read()


def publish(item, token, info):
    data = video_file(item["media"][0])
    size = len(data)
    opts = info.get("privacy_level_options", [])
    privacy = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in opts else "SELF_ONLY"
    title = limit_tags(item.get("caption", ""))
    while len(title.encode("utf-16-le")) // 2 > 2200:
        title = title[:-10]
    post_info = {"title": title, "privacy_level": privacy, "disable_duet": False, "disable_stitch": False,
                 "disable_comment": bool(info.get("comment_disabled")), "video_cover_timestamp_ms": 1500,
                 "brand_content_toggle": False, "brand_organic_toggle": False, "is_aigc": True}
    if size <= 64 * 1024 * 1024:
        chunk, count = size, 1
    else:
        chunk = 32 * 1024 * 1024
        count = size // chunk
    d = api("post/publish/video/init/", token, {"post_info": post_info, "source_info": {
        "source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": count}})
    pid, url = d["publish_id"], d["upload_url"]
    for i in range(count):
        a = i * chunk
        b = size if i == count - 1 else a + chunk
        http("PUT", url, data[a:b], {"Content-Type": "video/mp4", "Content-Length": str(b - a),
                                     "Content-Range": f"bytes {a}-{b - 1}/{size}"}, raw=True, timeout=600)
    for _ in range(60):
        st = api("post/publish/status/fetch/", token, {"publish_id": pid})
        s = st.get("status")
        if s == "PUBLISH_COMPLETE":
            return pid, privacy
        if s == "FAILED":
            raise RuntimeError(f"Veröffentlichung fehlgeschlagen: {st.get('fail_reason')}")
        time.sleep(10)
    return pid, privacy + " (Status noch offen)"


def connect():
    code = os.environ.get("TT_CODE", "")
    if not code and os.environ.get("GITHUB_EVENT_PATH"):  # aus dem Ereignis lesen, damit der Code nicht im öffentlichen Log steht
        code = json.load(open(os.environ["GITHUB_EVENT_PATH"])).get("inputs", {}).get("code", "")
    code = urllib.parse.unquote(code.strip())
    if not (KEY and SECRET and code):
        sys.exit("TT_CLIENT_KEY, TT_CLIENT_SECRET (Secrets) und der Code werden gebraucht.")
    tok = oauth(grant_type="authorization_code", code=code, redirect_uri=REDIRECT)
    tok["since"] = now().isoformat()
    write_token(tok)
    lines = [now().isoformat(), "TikTok verbunden."]
    try:
        info = creator(tok["access_token"])
        lines.append(f"Konto: @{info.get('creator_username')}, erlaubte Sichtbarkeit: {', '.join(info.get('privacy_level_options', []))}")
    except Exception as e:
        lines.append(f"Kontoabfrage fehlgeschlagen: {clean(e)}")
    print("\n".join(lines))
    with open(STATUS, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    if not (KEY and SECRET and os.path.exists(TOK)):
        print("TikTok noch nicht verbunden, nichts zu tun.")
        return
    queue, posted = load(Q, []), load(TP, {})
    since = dt.datetime.fromisoformat(read_token().get("since") or now().isoformat())
    t = now()
    due = []
    for item in queue:
        if item.get("type") != "REEL" or item.get("tiktok") is False:
            continue
        st = posted.get(item["id"], {})
        if st.get("publish_id") or st.get("skipped") or st.get("tries", 0) >= MAX_TRIES:
            continue
        at = dt.datetime.fromisoformat(item["at"])
        if at > t or at < since or ("ready_after" in item and dt.datetime.fromisoformat(item["ready_after"]) > t):
            continue
        if t - at > MAX_LATE:
            posted[item["id"]] = {"skipped": "zu spät", "at": t.isoformat()}
            continue
        due.append(item)
    if not due:
        save(TP, posted)
        return
    token = access_token()
    info = creator(token)
    for item in sorted(due, key=lambda i: i["at"]):
        st = posted.setdefault(item["id"], {})
        st["tries"] = st.get("tries", 0) + 1
        try:
            st["publish_id"], st["privacy"] = publish(item, token, info)
            st["posted_at"] = now().isoformat()
            st.pop("error", None)
            print(f"[{item['id']}] auf TikTok: {st['privacy']}")
        except Exception as e:
            st["error"] = clean(e)[:500]
            print(f"[{item['id']}] TikTok-Fehler: {st['error']}")
        save(TP, posted)


if __name__ == "__main__":
    try:
        connect() if sys.argv[1:] == ["connect"] else main()
    except Exception as e:
        print("TikTok-Fehler:", clean(e))
        sys.exit(1)
