# 🎛️ Tims Launchpad MK2 (RGB) for FL Studio

Ein vollständig synchronisiertes **Launchpad MK2 MIDI Script** für **FL Studio**, das die Channel-Rack-Zustände (Mute / Aktiv) live auf deinem Launchpad visualisiert – in den **echten RGB-Farben** der Channels.

---

## ✨ Features

- 🔄 **Bidirektionale Synchronisation**  
  Änderungen am Launchpad oder im FL Studio Channel Rack werden automatisch aufeinander abgestimmt.

- 🎨 **Echte RGB-Farben aus FL Studio**  
  Jede LED zeigt die Originalfarbe des zugehörigen FL-Channels (nicht nur feste Launchpad-Farben).

- 💡 **Deutliche Statusanzeige**  
  - **Aktiv (unmuted):** volle FL-Farbe  
  - **Deaktiviert (muted):** gleiche Farbe, aber um 75 % gedimmt  

- 🎹 **64-Channel Grid Mapping (8×8)**  
  Alle Kanäle werden automatisch auf das Launchpad-Grid gemappt.

- 🧠 **Automatische Aktualisierung**  
  Änderungen an Mute-Status oder Channel-Farbe in FL Studio werden sofort auf das Launchpad übertragen (`OnRefresh`).

---

## ⚙️ Installation

1. **Script-Datei speichern**

   Lade oder kopiere die Datei  
   👉 `Tims Launchpad MK2 (RGB).py`

   in folgenden FL-Studio-Ordner:


  `C:\Users<DEIN_NAME>\Documents\Image-Line\FL Studio\Settings\Hardware\`


oder unter macOS:

  `~/Documents/Image-Line/FL Studio/Settings/Hardware/`


2. **In FL Studio auswählen**

- Öffne **MIDI Settings (F10 → MIDI)**  
- Wähle dein **Launchpad MK2** unter *Input*  
- Aktiviere ✅ *Enable*  
- Wähle als **Script:**  
  `Novation-Launchpad-Mk2-for-FL-Studio`

3. **Fertig!**  
Das Launchpad sollte nun automatisch mit den FL Studio Channel-Farben leuchten.

---

## 🧩 Funktionsweise

| Event | Beschreibung |
|--------|---------------|
| `OnInit()` | Wird beim Laden des Scripts aufgerufen. Initialisiert Pads und schaltet LEDs aus. |
| `buildPads()` | Erstellt das Pad–Channel-Mapping (64 Kanäle max.). |
| `OnNoteOn()` | Wird bei Pad-Druck ausgeführt – toggelt Channel Mute/Unmute. |
| `OnRefresh()` | Aktualisiert Launchpad, wenn FL Studio Änderungen meldet (z. B. Farbe oder Mute). |
| `getAdjustedPadColor()` | Berechnet LED-Farbe (RGB 0–63), abhängig vom Channel-Status. |

---

## 🎨 Farbverhalten

| Zustand | Beschreibung | LED |
|----------|---------------|-----|
| Aktiv (unmuted) | FL-Channel ist aktiv | volle Channel-Farbe |
| Deaktiviert (muted) | Channel ist gemutet | gleiche Farbe, aber gedimmt (25 % Helligkeit) |

> Das Launchpad nutzt echte **RGB SysEx-Nachrichten** (`F0 00 20 29 02 18 0B ... F7`),  
> wodurch alle FL-Farben präzise dargestellt werden.

---

## 🧠 Technische Details

- **Launchpad Layout:** Session Mode (8×8 Grid)  
- **FL API:** `channels`, `device`  
- **MIDI Kommunikation:**  
- `midiOutSysex()` → RGB LED Updates  
- `midiOutMsg()` → Clear / Reset  
- **Farbskala:** 0–255 (FL Studio) → 0–63 (Launchpad)  

---

## 💡 Tipps

- Wenn du mehr als 64 Channels hast, werden nur die ersten 64 angezeigt.  
- Um Überlastung zu vermeiden, werden LED-Befehle mit einer kurzen Pause (1 ms) gesendet.  
- Du kannst in der Funktion `getAdjustedPadColor()` die Helligkeit oder das Verhalten bei „aus“ leicht anpassen (z. B. graue Farbe statt gedimmt).

---

## 🧑‍💻 Autor

**Tim**  
Custom Launchpad MK2 Integration for FL Studio  
Made with ❤️ and Python MIDI Scripting

---

## 📜 Lizenz

Dieses Script darf frei verwendet, angepasst und weitergegeben werden.  
