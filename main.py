import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import copy
import itertools as it

import music as mu
import matrix as mx
import events as ev
import playback as pb

voice_sequences = dict()

voice_sequences.update(mx.parse_matrix("""
&WoodBlock  .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
&Claves     .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
&Maraca     .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
&Cabasa     .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
&PedalHihat .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
&SideStick  .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
&BassDrum1  .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
"""))

#   C6      D7      GM7     E-      CM7     F#      B-      B7      E       AM7     Eb-     G#      C#-     AM7     G#
voice_sequences.update(mx.parse_matrix("""
=a5 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   vv  .   .   .   .   .   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   vvvv.v v. vv.v  . vvvv  .   v   .   .   .   .   .   .   .   .   
=g5 .   .   .   .   .   .   .   .   .   .   .  v.   .   .   .   .   .   . v .   .   .   .   .   .   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   . v vv  .   .   .   .   .   .   .   . v vv  .   .   .v  .   .   .   .   .   .   .   .   
=f5 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
=e5 .   .   .   .   .   .   .   .   vvvvvvvv.   . vvvvv .   .   .   .   .   .   .  v.   .   .   . v .   .  v.  v.   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .  v.  vvvv . v vvv .   .   .   .   .   
=d5 .   vvvvvvvvvv  .   .   .   .  v.   .   .   .   .  vvvvv.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .  vv   .   vvv .   .   .   .   
=c5 .   .   .   . vvvvvv.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   . v .   .   .   .   .   vvvvvvvvvvvv.   
=b4 .   .   .   .   .   vvvvvvvv. v .   .   .   .   .   .   .   . vv.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .    
    .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
=a4 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .v  .   .   .   .   .   .   .   .   .
=g4 .   .   .   .   .   .   .   .v  .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .     
"""))

#   C6  D7  GM7 E-  CM7 F#  B-  B7  E   AM7 Eb- G#  C#- AM7 G#
voice_sequences.update(mx.parse_matrix("""
    .   .   .   .   .   .   .   .   .   .   .   wwwwwwwwwwwwwwwwwwww
=g5 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .     
    .   .   .   .   .   .   .   .   .   .   wwww.   .   .   .   .   
=f5 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
=e5 .   .   .   .   . wwwwww.   .   wwwwwwww.   .   uuuuuuuu.   .   
    .   .   .   .   .   .   .   wwww.   .   .   .   .   .   uuuuuuuu
=d5 .   .   .   .   .   .   wwww.   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   xxxxxxxx.   xxxxxxxxxxxx.   
=c5 .   xxxxxx  .   ww  .   .   .   .   .   .   xxxx.   .   .   xxxx
=b4 .   .   . xxxxxxxxxx.   xxxxxxxxxxxx.   .   .   .   .   .   .   
    .   .   .   .   .   xxxx.   .   .   .   .   .   .   .   .   .   
=a4 xxxx.   .   .   .   .   .   .   .   yyyyyyyy.   .   .   .   .   
    .   .   .   .   .   .   .   .   yyyy.   .   yyyyyyyyyyyyyyyyyyyy
=g4 .   .   .   yyyyyyyy.   .   .   .   .   .   .   .   .   .   .   
    .   yyyyyyyy.   .   yyyyyyyyyyyy.   .   .   .   .   .   .   .   
=f4 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
=e4 yyyy.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   zzz .   .   .   .   .   
=d4 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   .   .   zzzz.   .   .   
=c4 zzzz.   .   .   zzzz.   .   .   .   .   .   .   .   .   .   .   
=b3 .   .   .   .   .   .   zzzz.   .   .   .   .   .   .   .   .   
    .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
=a3 .   zzzz.   .   .   .   .   zzzz.   zzzz.  z.   .   zzzz.   .   
    .   .   .   .   .   .   .   .   .   .   .   zzzz.   .   zzzzzzzz
=g3 .   .   zzzz.   .   .   .   .   .   .   .   .   .   .   .   .   
    .   .   .   .   .   zzzz.   .   .   .   .   .   .   .   .   .   
=f3 .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   
=e3 .   .   .   zzzz.   .   .   .   zzzz.   .   .   .   .   .   .   
""", transforms=[mu.Scale("duration", 2)]))

voice_instruments = dict(
    z="pizzicato contrabass drawbar_organ",
    y="cello tuba",
    x="viola trombone",
    w="violin french_horns",
    u="slow_violin",
    v="jazz_guitar",
)

pb.play_voices(voice_sequences, voice_instruments)
