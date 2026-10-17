# TikTok-Autoposter einrichten (einmalig, kostenlos)

Danach gehen die Reels um 12:00 und die Nova-Videos um 17:00 automatisch auch auf TikTok.
Du gibst nirgends ein Passwort an Claude weiter. Die Menünamen bei TikTok können leicht abweichen.

## 1. Entwickler-App anlegen (am PC, ca. 15 Minuten)
Die Werte unten genau so kopieren (am besten mit Kopieren/Einfügen). Die Menünamen sind aus TikToks Entwickler-Doku übernommen, nicht von Claude live geprüft; kleine Abweichungen sind möglich.

**1.1 Entwickler-Konto**
1. https://developers.tiktok.com öffnen → oben rechts **Log in**.
2. Mit dem TikTok-Konto **neuro_nauten** anmelden (oder mit E-Mail `insta.ki@mailbox.org` registrieren, dann das TikTok-Konto später als Testkonto verbinden).
3. Falls gefragt: Nutzungsbedingungen für Entwickler akzeptieren. Kostet nichts.

**1.2 App anlegen**
1. Oben rechts auf dein Profilbild → **Manage apps**.
2. **Connect an app** (oder „Create app“) klicken.
3. Bei „App owner“ / „Who owns this app“: **Individual** (Einzelperson) wählen, keine Organisation → **Confirm**.
4. Du landest auf der Seite der App. Bereich **Basic information** ausfüllen:
   - **App icon:** Bild hier speichern und hochladen: https://raw.githubusercontent.com/SebastianBC81/neuro_nauten-media/main/tiktok/app-icon.png
   - **App name:** `neuro_nauten Autoposter`
   - **Category:** `Education`
   - **Description:** `Lädt eigene Lernvideos automatisch in das eigene Konto @neuro_nauten hoch.`
   - **Terms of Service URL:** `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/nutzungsbedingungen.html`
   - **Privacy Policy URL:** `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/datenschutz.html`
   - **Platforms:** nur Haken bei **Web** (nicht Android/iOS/Desktop).
   - Im Feld **Website URL** (erscheint bei Web): `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/verbinden.html`
5. Falls bei einer URL **Verify** steht und TikTok eine Datei oder einen Code verlangt: Datei-Namen bzw. Code an Claude schicken. Claude legt sie ins Repo, dann **Verify** klicken.
6. Unten **Save** klicken.

**1.3 Produkte hinzufügen**
1. Links oder unten **Products** → **Add products**.
2. **Login Kit** → **Add**. Dann **Content Posting API** → **Add**.
3. Bei **Login Kit** unter **Web** → **Redirect URI**: `https://sebastianbc81.github.io/neuro_nauten-media/tiktok/callback.html` eintragen (genau so, ohne Leerzeichen am Ende).
4. Bei **Content Posting API** den Schalter **Direct Post** einschalten.
5. Bereich **Scopes**: Haken bei `user.info.basic` und `video.publish`. Sind sie schon drin, nichts tun. Andere Scopes nicht nötig.
6. **Save**. Auf **Submit for review** jetzt **nicht** klicken (das ist die Prüfung, später).

**1.4 Sandbox (Testmodus, ohne Prüfung nutzbar)**
1. Oben auf der App-Seite vom Reiter **Production** auf **Sandbox** wechseln → **Create Sandbox** → Name z. B. `test` → bestätigen.
2. In der Sandbox prüfen, ob Basic information, Products, Redirect URI, Direct Post und Scopes wie in 1.2 und 1.3 eingetragen sind. Fehlt etwas: genauso nachtragen und **Save**.
3. Bereich **Target Users** (Testnutzer) → **Add account** → im Fenster mit dem TikTok-Konto **neuro_nauten** anmelden und bestätigen.
4. Oben in der Sandbox stehen **Client key** und **Client secret** (beim Secret ggf. auf das Auge klicken). Beide gleich in Schritt 2 eintragen, nicht in den Chat schreiben.

**Vermutlich wichtig:** Laut TikToks Doku dürfen ungeprüfte Apps nur privat posten, und es gibt dort den Fehler „unaudited_client_can_only_post_to_private_accounts“. Kommt dieser Fehler, müsste das TikTok-Konto bis zur Prüfung auf privat stehen. Ob das bei uns zutrifft, sieht Claude im ersten Testlauf; dann entscheidest du.

## 2. Schlüssel bei GitHub hinterlegen
1. Öffne https://github.com/SebastianBC81/neuro_nauten-media/settings/secrets/actions
2. **New repository secret**: Name `TT_CLIENT_KEY`, Wert = Client Key → speichern.
3. Noch einmal: Name `TT_CLIENT_SECRET`, Wert = Client Secret → speichern.

## 3. Konto verbinden (2 Minuten, am Handy oder PC)
1. Öffne https://sebastianbc81.github.io/neuro_nauten-media/tiktok/verbinden.html
2. Client Key eintragen (aus der **Sandbox**) → **Weiter zu TikTok** → bei TikTok **Erlauben**.
3. Auf der Seite „Fast geschafft!“ den Code kopieren und den Knopf zu GitHub tippen.
4. Bei GitHub **Run workflow** → Code einfügen → grün **Run workflow**. Der Code gilt nur kurz, also direkt machen.
5. Schreib Claude „TikTok verbunden“. Claude prüft dann, ob alles läuft.

## Wichtig: Videos sind zuerst privat
Solange TikTok die App nicht geprüft hat, erlaubt TikTok nur **private** Beiträge („Nur ich“).
So machst du ein Video öffentlich: TikTok-App → Profil → Video öffnen → **…** → **Datenschutzeinstellungen** → „Wer kann dieses Video ansehen“ → **Alle**.
Die Prüfung durch TikTok (kostenlos) können wir später beantragen; dann laufen die Videos ganz automatisch öffentlich.

## Trennen
Jederzeit in der TikTok-App: Einstellungen und Datenschutz → Sicherheit → **Apps und Dienste** → neuro_nauten Autoposter entfernen.
