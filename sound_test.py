import winsound

NOTES = {
    "A3": 220,  "B3": 247,
    "C4": 261,  "D4": 294,
    "E4": 329,  "F4": 349,
    "G4": 392,  "A4": 440,
}

MELODY = [
    ("E4", 434),
    ("B3", 217),
    ("C4", 217),
    ("D4", 434),
    ("C4", 217),
    ("B3", 194),
    ("A3", 434),
    ("A3", 212),
    ("C4", 217),
    ("E4", 434),
    ("D4", 217),
    ("C4", 217),
    ("B3", 651),
    ("C4", 217),
    ("D4", 434),
    ("E4", 434),
    ("C4", 434),
    ("A3", 425),
    ("A3", 1085),
    ("D4", 434),
    ("F4", 212),
    ("A4", 434),
    ("G4", 217),
    ("F4", 217),
    ("E4", 651),
    ("C4", 217),
    ("E4", 434),
    ("D4", 217),
    ("C4", 217),
    ("B3", 651),
    ("C4", 217),
    ("D4", 434),
    ("E4", 434),
    ("C4", 434),
    ("A3", 434),
    ("A3", 868),
]

def play_note(name, duration_ms):
    freq = NOTES.get(name)
    if freq is None:
        return

    winsound.Beep(freq, duration_ms)

def play_melody_loop():
    print("Presiona CTRL+C para salir.")
    try:
        while True:
            for note, duration in MELODY:
                play_note(note, duration)
    except KeyboardInterrupt:
        print("\nsalida.")

if __name__ == "__main__":
    play_melody_loop()

