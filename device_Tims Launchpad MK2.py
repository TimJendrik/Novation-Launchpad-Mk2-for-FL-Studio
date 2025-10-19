# name=Tims Launchpad MK2 (RGB)
# Author: Tim
# Beschreibung:
# Dieses Script synchronisiert das Launchpad MK2 mit dem FL Studio Channel Rack.
# Jede Pad-LED zeigt die FL-Channel-Farbe in echter RGB-Darstellung.
# Aktive Channels leuchten hell, gemutete werden abgedunkelt angezeigt.

import time

import channels
import device

# ----------- Konfiguration -----------
GRID_WIDTH = 8  # 8 Spalten
GRID_HEIGHT = 8  # 8 Reihen
START_NOTE = 11  # Unterste linke Pad-Note im Session-Layout
COLOR_OFF = (0, 0, 0)  # LED aus (RGB = Schwarz)

# ----------- Globale Daten -----------
pads = []  # Liste mit Zuordnung: Channel ↔ Pad


# ==========================================================
# Hilfsfunktionen
# ==========================================================


def note_to_channel_index(note):
    """
    Rechnet eine Launchpad-Note (z. B. 81, 82, 83 …)
    zurück in den passenden FL-Channel-Index.
    """
    offset = note - START_NOTE
    row = offset // 10
    col = offset % 10
    if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
        index = (GRID_HEIGHT - 1 - row) * GRID_WIDTH + col
        return index
    return None


def note_to_led_index(note):
    """
    Für Launchpad MK2 kann die Note direkt als LED-ID genutzt werden.
    """
    return note


def calcNoteFromIndex(idx):
    """
    Rechnet Channel-Index (0–63) zurück in Launchpad-Note (11–88).
    """
    row = GRID_HEIGHT - 1 - (idx // GRID_WIDTH)
    col = idx % GRID_WIDTH
    return START_NOTE + row * 10 + col


def lightPadRGB(pad_id, r, g, b):
    """
    Sendet eine RGB-Farbe (0–63) an ein bestimmtes Launchpad-Pad.
    """
    msg = [
        0xF0,
        0x00,
        0x20,
        0x29,
        0x02,
        0x18,
        0x0B,
        pad_id,
        int(r) & 0x3F,
        int(g) & 0x3F,
        int(b) & 0x3F,
        0xF7,
    ]
    device.midiOutSysex(bytes(msg))
    time.sleep(0.001)  # kurze Pause zur Entlastung


def getFLColorRGB(idx):
    """
    Holt die FL-Studio-Farbe des Channels als (r, g, b) in 0–63 Skala.
    """
    fl_color = channels.getChannelColor(idx)
    r = (fl_color >> 16) & 0xFF
    g = (fl_color >> 8) & 0xFF
    b = fl_color & 0xFF
    # Skaliere 0–255 → 0–63 (Launchpad-Farbraum)
    return round(r / 4), round(g / 4), round(b / 4)


def getAdjustedPadColor(pad):
    """
    Gibt die RGB-Farbe eines Pads abhängig vom Mute-Zustand zurück:
    - aktiv: Originalfarbe
    - stummgeschaltet: abgedunkelte Farbe
    """
    r, g, b = getFLColorRGB(pad["index"])
    if not pad["activated"]:
        # Abdunkeln für „aus“ (ca. 25 % der Helligkeit)
        r, g, b = int(r * 0.25), int(g * 0.25), int(b * 0.25)
    return (r, g, b)


def lightPad(note, color_tuple):
    """
    Aktualisiert die LED-Farbe eines Pads.
    """
    r, g, b = color_tuple
    lightPadRGB(note_to_led_index(note), r, g, b)


# ==========================================================
# Pad-Verwaltung
# ==========================================================


def buildPads():
    """
    Erstellt die interne Liste aller Pads mit ihren Channel-Zuordnungen
    und initialisiert deren Farben.
    """
    pads.clear()
    count = min(channels.channelCount(), 64)

    for idx in range(count):
        note = calcNoteFromIndex(idx)
        muted = channels.isChannelMuted(idx)
        pad = {
            "note": note,
            "index": idx,
            "activated": not muted,
        }
        pad["color"] = getAdjustedPadColor(pad)
        pads.append(pad)
        lightPad(note, pad["color"])


def invertActivatedState(pad):
    """
    Wechselt den Zustand eines Channels (Mute an/aus)
    und aktualisiert LED-Farbe auf dem Launchpad.
    """
    pad["activated"] = not pad["activated"]
    channels.muteChannel(pad["index"], not pad["activated"])
    pad["color"] = getAdjustedPadColor(pad)
    lightPad(pad["note"], pad["color"])


# ==========================================================
# FL Studio Hooks
# ==========================================================


def OnInit():
    """
    Wird beim Laden des Scripts aufgerufen.
    """
    for n in range(11, 99):
        lightPadRGB(n, 0, 0, 0)  # alle LEDs aus
    buildPads()


def OnNoteOn(event):
    """
    Reagiert auf Pad-Druck am Launchpad.
    """
    if event.data2 == 0:
        # Velocity 0 = NoteOff → ignorieren
        return

    pad = getPadByNote(event.note)
    if pad:
        invertActivatedState(pad)
    event.handled = True


def OnRefresh(flags):
    """
    Wird aufgerufen, wenn FL Studio den Channel-Zustand oder Farben ändert.
    (z. B. Mute, Solo, Farbänderung)
    """
    for pad in pads:
        fl_state = not channels.isChannelMuted(pad["index"])
        pad["activated"] = fl_state
        pad["color"] = getAdjustedPadColor(pad)
        lightPad(pad["note"], pad["color"])


def getPadByNote(note):
    """
    Findet das Pad-Objekt zur gegebenen Note.
    """
    for pad in pads:
        if pad["note"] == note:
            return pad
    return None
