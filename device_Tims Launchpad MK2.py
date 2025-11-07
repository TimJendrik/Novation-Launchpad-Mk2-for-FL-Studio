# name=Novation-Launchpad-Mk2-for-FL-Studio
# Author: Tim
# Beschreibung:
# Dieses Script synchronisiert das Launchpad MK2 mit dem FL Studio Channel Rack.
# Jede Pad-LED zeigt die FL-Channel-Farbe in echter RGB-Darstellung.
# Aktive Channels leuchten hell, gemutete werden abgedunkelt angezeigt.

import channels
import device

# ==========================================================
# Konfiguration
# ==========================================================
GRID_WIDTH = 8  # Anzahl Spalten
GRID_HEIGHT = 8  # Anzahl Reihen
START_NOTE = 11  # Unterste linke Pad-Note im Session-Layout
MAX_PADS = GRID_WIDTH * GRID_HEIGHT
COLOR_OFF = (0, 0, 0)  # LED aus (RGB = Schwarz)

# Globale Pad-Daten
pads = []


# ==========================================================
# Hilfsfunktionen
# ==========================================================
last_channel_count = -1


def calc_note_from_index(idx):
    """Rechnet Channel-Index (0–63) zurück in Launchpad-Note (11–88)."""
    row = GRID_HEIGHT - 1 - (idx // GRID_WIDTH)
    col = idx % GRID_WIDTH
    return START_NOTE + row * 10 + col


def get_fl_color_rgb(idx):
    """Liest FL-Studio-Channel-Farbe und wandelt sie in 0–63 RGB um."""
    fl_color = channels.getChannelColor(idx)
    r = (fl_color >> 16) & 0xFF
    g = (fl_color >> 8) & 0xFF
    b = fl_color & 0xFF
    return r >> 2, g >> 2, b >> 2  # Schnellere Division durch 4


def light_pad_rgb(note, r, g, b):
    """Sendet RGB-Wert (0–63) an Launchpad MK2."""
    device.midiOutSysex(
        bytes(
            [
                0xF0,
                0x00,
                0x20,
                0x29,
                0x02,
                0x18,
                0x0B,
                note,
                int(r) & 0x3F,
                int(g) & 0x3F,
                int(b) & 0x3F,
                0xF7,
            ]
        )
    )


def light_pad(note, color):
    """Aktualisiert LED-Farbe für ein Pad."""
    r, g, b = color
    light_pad_rgb(note, r, g, b)


def get_adjusted_pad_color(pad):
    """Berechnet LED-Farbe abhängig vom Mute-Zustand."""
    r, g, b = get_fl_color_rgb(pad["index"])
    if not pad["activated"]:
        r, g, b = r // 4, g // 4, b // 4  # 75% dunkler bei Mute
    return (r, g, b)


def get_pad_by_note(note):
    """Findet das Pad-Objekt zur gegebenen Note."""
    for pad in pads:
        if pad["note"] == note:
            return pad
    return None


# ==========================================================
# Pad-Verwaltung
# ==========================================================


def build_pads():
    """Initialisiert alle Pads mit Channel-Zuordnung und LED-Farbe."""
    pads.clear()
    count = min(channels.channelCount(), MAX_PADS)

    # 1) Nur existierende Channels neu aufbauen & LED setzen
    for idx in range(count):
        note = calc_note_from_index(idx)
        active = not channels.isChannelMuted(idx)
        pad = {"note": note, "index": idx, "activated": active}
        pad["color"] = get_adjusted_pad_color(pad)
        pads.append(pad)
        light_pad(note, pad["color"])

    # 2) Restliche Pads (falls früher mehr Channels existierten) ausschalten
    for idx in range(count, MAX_PADS):
        note = calc_note_from_index(idx)
        light_pad_rgb(note, 0, 0, 0)


def invert_activated_state(pad):
    """Wechselt Mute-Zustand und aktualisiert LED."""
    pad["activated"] = not pad["activated"]
    channels.muteChannel(pad["index"], not pad["activated"])
    pad["color"] = get_adjusted_pad_color(pad)
    light_pad(pad["note"], pad["color"])


# ==========================================================
# FL Studio Hooks
# ==========================================================


def OnInit():
    global last_channel_count
    # Alle LEDs aus
    for n in range(11, 99):
        light_pad_rgb(n, 0, 0, 0)
    build_pads()
    last_channel_count = channels.channelCount()


def OnNoteOn(event):
    """Reagiert auf Pad-Druck am Launchpad (NoteOffs ignoriert)."""
    if event.data2 == 0:  # Velocity 0 = NoteOff
        event.handled = True
        return

    pad = get_pad_by_note(event.note)
    if pad:
        invert_activated_state(pad)
    event.handled = True


def OnNoteOff(event):
    """Ignoriere NoteOff komplett (vermeidet Rückkopplungen)."""
    event.handled = True


def OnRefresh(flags):
    """
    Wird aufgerufen, wenn FL Studio Änderungen an Channels erkannt hat.
    Aktualisiert nur geänderte Pads → reduziert MIDI-Traffic deutlich.
    """
    global last_channel_count

    current_count = channels.channelCount()

    # 0) Wurde ein Channel hinzugefügt oder entfernt?
    if current_count != last_channel_count:
        last_channel_count = current_count
        build_pads()  # aber MAXIMAL einmal – danach wieder sparsam!
        return

    # 1) Bestehende Pads prüfen (Mute/Farbe)
    for pad in pads:
        idx = pad["index"]

        # Mute-State
        new_active = not channels.isChannelMuted(idx)
        if new_active != pad["activated"]:
            pad["activated"] = new_active
            pad["color"] = get_adjusted_pad_color(pad)
            light_pad(pad["note"], pad["color"])
            continue

        # Farbänderung
        r, g, b = get_fl_color_rgb(idx)
        expected = (r, g, b) if pad["activated"] else (r // 4, g // 4, b // 4)
        if expected != pad["color"]:
            pad["color"] = expected
            light_pad(pad["note"], pad["color"])
