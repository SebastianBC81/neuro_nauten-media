# TikTok-Autoposter einrichten (einmalig, kostenlos)

Danach gehen die Reels um 12:00 und die Nova-Videos um 17:00 automatisch auch auf TikTok.
Du gibst nirgends ein Passwort an Claude weiter. Die Menünamen bei TikTok können leicht abweichen.

## 1. Entwickler-App anlegen (am PC am einfachsten)
1. Öffne https://developers.tiktok.com und melde dich mit dem TikTok-Konto **neuro_nauten** an.
2. Oben rechts **Manage apps** → **Connect an app** (oder „Create app“). Typ: **Individual / Einzelperson**.
3. Trag ein:
   - **App name:** `neuro_nauten Autoposter`
   - **App icon:** https://raw.githubusercontent.com/SebastianBC81/neuro_nauten-media/main/tiktok/app-icon.png (speichern, dann hochladen)
   - **Category:** Education
   - **Description:** `Lädt eigene Lernvideos automatisch in das eigene Konto @neuro_nauten hoch.`
   - **Terms of Service URL:** `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/nutzungsbedingungen.html`
   - **Privacy Policy URL:** `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/datenschutz.html`
   - **Platforms:** nur **Web**, Website URL `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/verbinden.html`
4. **Add products:** **Login Kit** und **Content Posting API**.
   - Bei Login Kit unter **Redirect URI** (Web): `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/callback.html`
   - Bei Content Posting API den Schalter **Direct Post** einschalten.
   - **Scopes:** `user.info.basic` und `video.publish` müssen dabei sein.
5. Oben auf **Sandbox** umschalten → **Create Sandbox**. Unter **Target Users** dein Konto **neuro_nauten** hinzufügen.
6. In der Sandbox stehen **Client Key** und **Client Secret**. Die brauchst du in Schritt 2.

## 2. Schlüssel bei GitHub hinterlegen
1. Öffne https://github.com/SebastianBC81/neuro_nauten-media/settings/secrets/actions
2. **New repository secret**: Name `TT_CLIENT_KEY`, Wert = Client Key → speichern.
3. Noch einmal: Name `TT_CLIENT_SECRET`, Wert = Client Secret → speichern.

## 3. Konto verbinden (2 Minuten, am Handy oder PC)
1. Öffne https://sebastianbc81.github.io/neuro_nauten-media/tiktok/verbinden.html
2. Client Key eintragen → **Weiter zu TikTok** → bei TikTok **Erlauben**.
3. Auf der Seite „Fast geschafft!“ den Code kopieren und den Knopf zu GitHub tippen.
4. Bei GitHub **Run workflow** → Code einfügen → grün **Run workflow**. Der Code gilt nur kurz, also direkt machen.
5. Schreib Claude „TikTok verbunden“. Claude prüft dann, ob alles läuft.

## Wichtig: Videos sind zuerst privat
Solange TikTok die App nicht geprüft hat, erlaubt TikTok nur **private** Beiträge („Nur ich“).
So machst du ein Video öffentlich: TikTok-App → Profil → Video öffnen → **…** → **Datenschutzeinstellungen** → „Wer kann dieses Video ansehen“ → **Alle**.
Die Prüfung durch TikTok (kostenlos) können wir später beantragen; dann laufen die Videos ganz automatisch öffentlich.

## Trennen
Jederzeit in der TikTok-App: Einstellungen und Datenschutz → Sicherheit → **Apps und Dienste** → neuro_nauten Autoposter entfernen.
