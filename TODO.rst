TO DO
======

- Takt auf zwei Ganze (Brevis)
+ Takt bis Achteln erweitern
+ schwere, leichte und halbschwere Taktzeiten definieren
+ diff und dist auf Melodie- und Melodie-/Harmonieintervalle umbenennen
- Kategorien für perfekte und imperfekte Konsonanzen und Dissonanzen machen
- Bewegungsrichtungen definieren
- Punktierte
- nicht ständig die Tonlänge ändern (mehr Gruppen von Achteln oder Vierteln)?
- Synkopen (kurz-lang(-lang-lang-...)-kurz)

- Notenmaterial (akzidenzien) und ambitus
- Durchgang, Vorhalt, Wechselnote Regeln
- Cambiata
- Schlüsse und Zwischenkadenzen? -> Halbtonanschluss und Akzidenzien als Aufforderung zur Kadenz

  * verschiedene Varianten als Liste oder so
  * evtl. Markierung beim C.F.?
  
Was dürfen Achteln und wieso steht das nirgends?
  
- erstes Intervall ist erstes Intervall, auch wenn erster Ton CF Pause ist

- Ténor einbauen?
- C.F. soll auch Halbe können (extra Regel für Synkopen?)
- C.F. auch angeben zu können wäre gut

wichtige Rand-/ Zwischennotizen
--------------------------------

- Vorhalte:

  * bei Septim- und Quartvorhalten bleibt immer die Oberstimme liegen, Unterstimme schreitet zum nächsten Ton vor und erzeugt so Dissonanz
  * beim Sekundvorhalt bleibt immer die Unterstimme liegen

- keine parallelen großen Terzen -> sonst entsteht Tritonus

  * z.B. c' und e', dann d' und fis' -> zwischen c' und fis' ü4 (Tritonus)

- alterierte Töne nur bei Terz und Sext möglich
- Viertel müssen auf leichte Zeit einsetzen (=leichte Halbe)

Features
--------

- Allow specified --cantus-firmus tune to be transposed before use
- Permit Pause in tunes, the current checks cannot deal with this
- Better searching for CP for given CF for the last 4 bars, this
  currently uses a fixed combination of tone lengths

Tests
-----

- test transpose on tune output
- add a test that falls back to the meter ('M') field in case the 'L'
  field is missing
- output abc without 'id' field in voice
- Read tune and/or gene from stdin (using '-' as filename)
- Write output to stdout
- Test accessing self.tune in Contrapunctus, this is currently unused
