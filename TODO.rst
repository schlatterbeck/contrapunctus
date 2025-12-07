TO DO
======

Allgemein
---------

+ Takt auf zwei Ganze (Brevis)
+ Bewegungsrichtungen definieren
+ Punktierte
- nicht ständig die Tonlänge ändern (mehr Gruppen von Achteln oder Vierteln)?
+ Synkopen (kurz-lang(-lang-lang-...)-kurz)

+ Notenmaterial (akzidenzien) und ambitus
+ Durchgang, Wechselnote Regeln
+ Vorhalt
+ Cambiata
- Schlüsse und Zwischenkadenzen? -> Halbtonanschluss und Akzidenzien als
  Aufforderung zur Kadenz

  * verschiedene Varianten als Liste oder so
  * evtl. Markierung beim C.F.?
- Wenn ein Cantus Firmus vorgegeben wird, sollte die Tonart erkannt
  werden und auch das Resultat in dieser Tonart stehen
- Wenn CF mit L=1/4 oder anderen Werten vorgegeben wird sollte das in
  1/8 umgerechnet werden (beim Einlesen). Für Regression-Tests (von CF +
  CP) reichts wenn das nur in 1/8 geht.
- Allow more different note lengths in CF: Allow 1/2 notes and syncopes:
  1/2 bound to another 1/2 in next bar (or when our bar is length 2
  allow 1/1 on half time) In addition allow dotted 1/2 and 1/1, when a
  dotted 1/2 is seen an 1/4 after that is allowed. After dotted no
  syncope is allowed.
  
Was dürfen Achteln und wieso steht das nirgends?
Dürfen Achteln nicht jumpen? Haben wir das schon?
  
[- Ténor einbauen?]
- C.F. soll auch Halbe können (extra Regel für Synkopen?)

Done
++++

+ Takt bis Achteln erweitern
+ schwere, leichte und halbschwere Taktzeiten definieren
+ diff und dist auf Melodie- und Melodie-/Harmonieintervalle umbenennen
+ erstes Intervall ist erstes Intervall, auch wenn erster Ton CF Pause ist
+ C.F. auch angeben zu können wäre gut
+ Oktav-Parallelen 
+ Quint-Parallelen (?)
+ Falsche Intervalle Modulo 12 (!) 

wichtige Rand-/ Zwischennotizen
--------------------------------

+ Vorhalte:

  * bei Septim- und Quartvorhalten bleibt immer die Oberstimme liegen,
    Unterstimme schreitet zum nächsten Ton vor und erzeugt so Dissonanz
  * beim Sekundvorhalt bleibt immer die Unterstimme liegen

- keine parallelen großen Terzen -> sonst entsteht Tritonus

  * z.B. c' und e', dann d' und fis' -> zwischen c' und fis' ü4 (Tritonus)

- alterierte Töne nur bei Terz und Sext möglich
+ Viertel müssen auf leichte Zeit einsetzen (=leichte Halbe)

Features
--------

+ Allow specified --cantus-firmus tune to be transposed before use
- Better searching for CP for given CF for the last 4 bars, this
  currently uses a fixed combination of tone lengths

Features Done
+++++++++++++

+ Permit Pause in tunes, the current checks cannot deal with this

Tests
-----

- test transpose on tune output
- add a test that falls back to the meter ('M') field in case the 'L'
  field is missing
- output abc without 'id' field in voice
- Read tune and/or gene from stdin (using '-' as filename)
- Write output to stdout
- Test accessing self.tune in Contrapunctus, this is currently unused
