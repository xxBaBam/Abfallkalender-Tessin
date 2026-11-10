# Abfallkalender Tessin (Landkreis Rostock)

Ein Kalender-Abo (ICS) für **Tessin (bei Sanitz)**, das sich selbst aktualisiert: schwarze Tonne (alle 4 Wochen),
gelbe Tonne (alle 2 Wochen) und blaue Tonne (alle 4 Wochen). Einmal abonnieren, fertig.

**Seite zum Abonnieren (iPhone, Android, PC):** https://xxbabam.github.io/Abfallkalender-Tessin/

| | Abo-Adresse |
|---|---|
| Ohne Erinnerung (für Google Kalender) | `https://xxbabam.github.io/Abfallkalender-Tessin/abfall.ics` |
| Mit Erinnerung am Vorabend, 18 Uhr | `https://xxbabam.github.io/Abfallkalender-Tessin/abfall-erinnerung.ics` |

> **Umgezogen:** Der Abfallkalender Rostock-Warnemünde ist jetzt in
> [Abfallkalender-Warnemuende](https://github.com/xxBaBam/Abfallkalender-Warnemuende), der Kreuzfahrt-Kalender in
> [Kreuzfahrtschiffe-Warnemuende](https://github.com/xxBaBam/Kreuzfahrtschiffe-Warnemuende). Unter `docs/warnemuende/`
> und `docs/kreuzfahrt/` liegen nur noch Umzugshinweise für alte Abos.

---

## In Google Kalender abonnieren (am PC)

1. [calendar.google.com](https://calendar.google.com) öffnen.
2. Links neben „Weitere Kalender“ auf **+** klicken → **Per URL**.
3. Die Adresse **ohne Erinnerung** einfügen und **Kalender hinzufügen**.
   Der Kalender erscheint auch auf dem Handy in der Google-Kalender-App
   (falls nicht: in der App unter Einstellungen → Kalender → **Synchronisieren** einschalten).

**Erinnerung optional:** Google Kalender ignoriert Erinnerungen, die in abonnierten Kalendern stehen. Deshalb dort:
Zahnrad → Einstellungen → links unter „Weitere Kalender“ den Kalender anklicken → bei den Benachrichtigungen für
**ganztägige Termine** z. B. „1 Tag vorher um 18:00“ eintragen. iPhone, Outlook und Thunderbird können direkt die
Adresse **mit Erinnerung** abonnieren.

> Google holt abonnierte Kalender nur etwa alle 12–24 Stunden neu ab. Änderungen erscheinen also mit etwas Verzögerung.

---

## Wie es funktioniert

- Der Workflow **„Kalender aktualisieren“** (`.github/workflows/build.yml`) läuft jeden Montag automatisch
  (und per Hand über Actions → „Kalender aktualisieren“ → „Run workflow“).
- Er liest auf https://www.abfall-lro.de/de/abfuhrtermine/ den Ortscode aus (der kann sich jedes Jahr ändern; die
  bekannten Codes stehen in `state.json`) und lädt die Termine für **dieses und das nächste Jahr**. Das nächste Jahr
  kommt automatisch dazu, sobald der Landkreis es veröffentlicht.
- Alles wird zu einer ICS mit festen Termin-IDs zusammengeführt (keine Doppelten; geänderte Termine werden ersetzt).
  Vergangene Termine werden nie gelöscht.
- Committet wird nur, wenn sich etwas geändert hat, plus einmal im Monat ein kleiner Eintrag in `state.json`.
  Sonst würde GitHub den Zeitplan nach 60 Tagen ohne Aktivität abschalten.
- Die Jahre zählen automatisch mit (2027, 2028, …), solange der Landkreis seine Kalender-Schnittstelle beibehält.

## Wenn etwas schiefgeht

- Scheitert der Abruf oder hat sich die Seite geändert, **bleibt der Kalender unverändert** und der Workflow schlägt
  fehl. GitHub schickt dir dann eine E-Mail.
- Ab dem **15. Dezember** schlägt der Workflow außerdem jeden Montag fehl, solange der Landkreis noch keine Termine
  fürs nächste Jahr hat (als Hinweis). Der Kalender bleibt trotzdem bis Jahresende gültig.

## Kosten

Keine. Das Repo ist öffentlich, und dafür sind GitHub Actions (Standard-Runner) und GitHub Pages kostenlos und
zählen **nicht** gegen das Freikontingent (2.000 Minuten/Monat gilt nur für private Repos). Würde das Repo privat
geschaltet, bräuchte Pages einen bezahlten Plan.

## Einstellungen ändern

In `config.json`:

| Feld | Bedeutung | Werte |
|---|---|---|
| `ort` | Ort wie auf abfall-lro.de geschrieben | z. B. `"Tessin"`, `"Teschow (Teterow)"` |
| `schwarz` / `gruen` | Rhythmus | `"4w"`, `"2w"` oder `""` (keine Tonne) |
| `schwarz_saison` / `gruen_saison` | Saison-Leerungen | `true` / `false` |
| `gelb` / `blau` | aufnehmen? | `true` / `false` |
| `erinnerung_uhrzeit` | Erinnerung am Vorabend (nur in `abfall-erinnerung.ics`) | z. B. `"18:00"` |

Die `id` nie ändern, sonst gibt es doppelte Termine. Nach dem Speichern läuft der Workflow von selbst.

`debug/`, `scripts/explore.py` und der Workflow „Erkundung (manuell)“ dienen nur der Fehlersuche, falls der Landkreis
seine Seite umbaut.
