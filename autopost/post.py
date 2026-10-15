"""Kostenloser Instagram-Autoposter für @neuro_nauten (läuft als GitHub Action).

Liest autopost/queue.json, veröffentlicht fällige Beiträge über die offizielle
Instagram-API (Instagram-Login, graph.instagram.com) und vermerkt das Ergebnis
in autopost/posted.json. Medien werden über GitHub Pages ausgeliefert, damit
Instagram korrekte Dateitypen bekommt. Fremde Medien-URLs (z. B. Canva-Exporte,
die nach einiger Zeit ablaufen) werden vorher ins Repo gespiegelt.

Eintrag in queue.json:
  {"id": "2026-10-20-reel", "at": "2026-10-20T12:00:00+02:00",
   "type": "REEL" | "FEED" | "STORY",
   "media": ["posts/2026-10-20_x/reel-tools.mp4"] oder https-URLs,
   "caption": "Text mit #Hashtags"}
FEED mit mehreren Bildern wird ein Karussell (max. 10 Bilder, nur JPG).

Umgebung: IG_TOKEN (Secret, Pflicht), PAGES_BASE (z. B. https://sebastianbc81.github.io/neuro_nauten-media/),
DRY_RUN=1 zum Testen ohne Posten.
"""
import datetime as dt, json, os, sys, time, urllib.parse, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = os.path.join(ROOT, "autopost", "queue.json")
P = os.path.join(ROOT, "autopost", "posted.json")
MEDIA_DIR = os.path.join(ROOT, "autopost", "media")
API = "https://graph.instagram.com" + ("/" + os.environ["IG_API_VERSION"] if os.environ.get("IG_API_VERSION") else "")
TOKEN = os.environ.get("IG_TOKEN", "")
PAGES = os.environ.get("PAGES_BASE", "").rstrip("/") + "/"
DRY = os.environ.get("DRY_RUN") == "1"
MAX_LATE = dt.timedelta(hours=12)   # ältere, verpasste Beiträge nicht mehr nachholen
MAX_TRIES = 3


def now():
    return dt.datetime.now(dt.timezone.utc)


def load(path, default):
    try:
        return json.load(open(path))
    except FileNotFoundError:
        return default


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


def api(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"Instagram-API {e.code}: {body[:400]}") from None


def media_url(m):
    return m if m.startswith("http") else PAGES + m.lstrip("/")


def is_own(m):
    return not m.startswith("http") or (PAGES != "/" and m.startswith(PAGES))


def mirror(item):
    """Lädt fremde Medien ins Repo, damit sie nicht ablaufen. True, wenn etwas geändert wurde."""
    changed = False
    for i, m in enumerate(item["media"]):
        if is_own(m):
            continue
        os.makedirs(MEDIA_DIR, exist_ok=True)
        with urllib.request.urlopen(m, timeout=120) as r:
            ctype = r.headers.get("Content-Type", "")
            data = r.read()
        ext = ".mp4" if "video" in ctype else ".jpg"
        name = f"{item['id']}-{i + 1}{ext}"
        with open(os.path.join(MEDIA_DIR, name), "wb") as f:
            f.write(data)
        item["media"][i] = f"autopost/media/{name}"
        changed = True
    if changed:
        # GitHub Pages braucht nach dem Push etwas Zeit; erst im nächsten Lauf posten
        item["ready_after"] = (now() + dt.timedelta(minutes=10)).isoformat()
    return changed


def reachable(url):
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def wait_ready(cid, video):
    """Wartet, bis Instagram den Container verarbeitet hat (Videos brauchen länger)."""
    for _ in range(60 if video else 12):
        st = api("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {cid}: {st}")
        time.sleep(10 if video else 3)
    raise RuntimeError(f"Container {cid} nicht fertig geworden")


def publish(item, uid):
    urls = [media_url(m) for m in item["media"]]
    for u in urls:
        if not reachable(u):
            raise RuntimeError(f"Medium nicht erreichbar: {u}")
    cap = item.get("caption", "")
    t = item["type"]
    if t == "REEL":
        c = api("POST", f"{uid}/media", media_type="REELS", video_url=urls[0], caption=cap, share_to_feed="true")
        wait_ready(c["id"], True)
    elif t == "STORY":
        video = urls[0].endswith(".mp4")
        kw = {"video_url": urls[0]} if video else {"image_url": urls[0]}
        c = api("POST", f"{uid}/media", media_type="STORIES", **kw)
        wait_ready(c["id"], video)
    elif t == "FEED" and len(urls) == 1:
        c = api("POST", f"{uid}/media", image_url=urls[0], caption=cap)
        wait_ready(c["id"], False)
    elif t == "FEED":
        kids = []
        for u in urls[:10]:
            k = api("POST", f"{uid}/media", image_url=u, is_carousel_item="true")
            wait_ready(k["id"], False)
            kids.append(k["id"])
        c = api("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(kids), caption=cap)
        wait_ready(c["id"], False)
    else:
        raise RuntimeError(f"Unbekannter Typ {t}")
    return api("POST", f"{uid}/media_publish", creation_id=c["id"])["id"]


def main():
    queue = load(Q, [])
    posted = load(P, {})
    changed = False
    t = now()

    for item in queue:
        if item["id"] in posted:
            continue
        try:
            changed |= mirror(item)
        except Exception as e:
            print(f"[{item['id']}] Spiegeln fehlgeschlagen: {e}")

    due = []
    for item in queue:
        st = posted.get(item["id"])
        if st and (st.get("media_id") or st.get("skipped") or st.get("tries", 0) >= MAX_TRIES):
            continue
        at = dt.datetime.fromisoformat(item["at"])
        if at > t or ("ready_after" in item and dt.datetime.fromisoformat(item["ready_after"]) > t):
            continue
        if t - at > MAX_LATE:
            posted[item["id"]] = {"skipped": "zu spät", "at": t.isoformat()}
            changed = True
            continue
        due.append(item)

    if due and not TOKEN and not DRY:
        sys.exit("IG_TOKEN fehlt (GitHub-Secret anlegen).")
    uid = None
    for item in sorted(due, key=lambda i: i["at"]):
        st = posted.setdefault(item["id"], {})
        st["tries"] = st.get("tries", 0) + 1
        changed = True
        try:
            if DRY:
                print(f"[{item['id']}] DRY_RUN, würde posten:", [media_url(m) for m in item["media"]])
                st["dry_run"] = t.isoformat()
                continue
            uid = uid or api("GET", "me", fields="user_id")["user_id"]
            st["media_id"] = publish(item, uid)
            st["posted_at"] = now().isoformat()
            st.pop("error", None)
            print(f"[{item['id']}] gepostet: {st['media_id']}")
        except Exception as e:
            st["error"] = str(e)[:500]
            print(f"[{item['id']}] Fehler: {e}")

    if changed:
        save(Q, queue)
        save(P, posted)
    failed = [k for k, v in posted.items() if v.get("error") and v.get("tries", 0) >= MAX_TRIES and not v.get("media_id")]
    if failed:
        print("Endgültig fehlgeschlagen:", ", ".join(failed))


if __name__ == "__main__":
    main()
