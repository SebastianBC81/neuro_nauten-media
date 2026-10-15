# Autoposter einrichten (einmalig, ca. 15 Minuten, kostenlos)

Der Autoposter postet die Beiträge von @neuro_nauten direkt über die offizielle Instagram-Schnittstelle.
Er läuft kostenlos auf GitHub (alle 10 Minuten), ohne Metricool-Limit. Instagram erlaubt bis zu 100 Posts pro Tag über die Schnittstelle.

**Wichtig:** Den Zugangsschlüssel (Token) nie in einen Chat, eine Mail oder eine Datei kopieren, nur in GitHub als Secret (Schritt 4). Das Repo ist öffentlich.

## 1. GitHub Pages einschalten (für die Bilder und Videos)
1. github.com/SebastianBC81/neuro_nauten-media öffnen → **Settings** → **Pages**.
2. Bei „Source“ **Deploy from a branch** wählen, Branch **main**, Ordner **/ (root)** → **Save**.

## 2. Instagram-Konto prüfen
In der Instagram-App: Einstellungen → Kontoart. Es muss ein **Business-** oder **Creator-Konto** sein (für Metricool ist das schon so).

## 3. Meta-App anlegen und Token erzeugen
1. developers.facebook.com öffnen und mit deinem Facebook- oder Meta-Konto anmelden (Entwicklerkonto ist kostenlos).
2. **Meine Apps** → **App erstellen**. Name z. B. „neuro_nauten Autoposter“.
3. Anwendungsfall: **Nachrichten und Inhalte auf Instagram verwalten** (englisch: „Manage messaging & content on Instagram“). Ein Business-Portfolio brauchst du nicht.
4. In der App links **Instagram** → **API-Einrichtung mit Instagram-Login**.
5. Bei „Zugriffstokens generieren“ auf **Konto hinzufügen** und mit @neuro_nauten anmelden, Berechtigungen erlauben.
   Falls Instagram eine Tester-Einladung verlangt: in Instagram unter Einstellungen → Website-Berechtigungen → Apps und Websites → Tester-Einladungen annehmen.
6. Neben dem Konto auf **Token generieren** tippen und den Token kopieren.

## 4. Token in GitHub speichern
1. Im Repo: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Name: `IG_TOKEN`, Wert: den Token einfügen → **Add secret**.

## 5. Einschalten
1. Im Repo den Reiter **Actions** öffnen. Falls GitHub fragt, die Workflows aktivieren.
2. Dann Claude im Thread schreiben: **„Autoposter fertig“**. Claude plant ab dann neue Beiträge über den Autoposter statt über Metricool.

## Gut zu wissen
- Der Token gilt 60 Tage und wird jede Woche automatisch verlängert („Instagram-Zugang verlängern“). Schlägt das fehl, einfach Schritt 3.6 und 4 wiederholen.
- Geplante Beiträge stehen in `autopost/queue.json`, erledigte in `autopost/posted.json`.
- GitHub startet geplante Abläufe manchmal ein paar Minuten später, Posts können sich also leicht verschieben.
- Das KI-Kennzeichen setzt der Autoposter über den Text („KI-Figur“, „KI-generiert“); das Instagram-Label „KI-Info“ kannst du bei Bedarf in der App nachträglich setzen.
