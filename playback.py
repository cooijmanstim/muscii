import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import collections
import time

import fluidsynth

import events as ev

def load_library(fs):
    fluidgm = fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
    kbhstrings = fs.sfload("/home/tim/SF/strings/kbh-strings.sf2")
    florestan_woodwinds = fs.sfload("/home/tim/SF/wind/Woodwinds/florestan_woodwinds.sf2")

    instruments = dict(
        drums=(fluidgm, 128, 40),

        kbhstrings=(kbhstrings, 0, 0), # one octave too low
        florestan_bassoon=(florestan_woodwinds, 0, 70),

        french_horns=(fluidgm, 0, 60),
        brass=(fluidgm, 0, 61),
        strings=(fluidgm, 0, 48), slow_strings=(fluidgm, 0, 49),
        ahhchoir=(fluidgm, 0, 52),
        ohhchoir=(fluidgm, 0, 53),

        drawbar_organ=(fluidgm, 0, 16),
        harmonica=(fluidgm, 0, 22),

        nylon_guitar=(fluidgm, 0, 24),
        jazz_guitar=(fluidgm, 0, 26),
        muted_guitar=(fluidgm, 0, 28),
        overdrive_guitar=(fluidgm, 0, 29),
        distortion_guitar=(fluidgm, 0, 30),
        guitar_harmonics=(fluidgm, 0, 31),

        acoustic_bass=(fluidgm, 0, 32),
        fingered_bass=(fluidgm, 0, 33),
        fretless_bass=(fluidgm, 0, 35),

        violin=(fluidgm, 0, 40), slow_violin=(fluidgm, 8, 40),
        viola=(fluidgm, 0, 41),
        cello=(fluidgm, 0, 42),
        contrabass=(fluidgm, 0, 43),
        pizzicato=(fluidgm, 0, 45),

        trumpet=(fluidgm, 0, 56),
        trombone=(fluidgm, 0, 57),
        tuba=(fluidgm, 0, 58),
        muted_trumpet=(fluidgm, 0, 59),

        soprano_sax=(fluidgm, 0, 64),
        alto_sax=(fluidgm, 0, 65),
        tenor_sax=(fluidgm, 0, 66),
        baritone_sax=(fluidgm, 0, 67),

        oboe=(fluidgm, 0, 68),
        english_horn=(fluidgm, 0, 69),
        bassoon=(fluidgm, 0, 70),
        clarinet=(fluidgm, 0, 71),
        piccolo=(fluidgm, 0, 72),
        flute=(fluidgm, 0, 73),
        pan_flute=(fluidgm, 0, 75),

        taiko_drum=(fluidgm, 0, 116), # has low frequencies
        timpani=(fluidgm, 0, 47),
        concert_bass_drum=(fluidgm, 8, 116),
    )

    return instruments

def prepare_channels(fs, voice_instruments):
    library = load_library(fs)

    voice_channels = dict()
    channel = 0
    for voice, instruments in voice_instruments.iteritems():
        if isinstance(instruments, basestring):
            instruments = instruments.split()
        for instrument in instruments:
            channel += 1
            fs.program_select(channel, *library[instrument])
            voice_channels.setdefault(voice, []).append(channel)
    return voice_channels

def play_voices(voice_sequences, voice_instruments, bpm=120):
    fs = fluidsynth.Synth()
    fs.start(driver="alsa")

    voice_channels = prepare_channels(fs, voice_instruments)
    events = collect_events(voice_sequences, voice_channels)
    play_events(fs, events, bpm=bpm)

    fs.delete()

def collect_events(voice_sequences, voice_channels):
    def sortfun(event):
        if isinstance(event, ev.NoteOff):
            # ensure noteoffs occur before noteons so that new noteons
            # are not immediately cancelled.
            return event.time - 1e-5
        else:
            return event.time

    events = []
    for name, sequence in voice_sequences.iteritems():
        for channel in voice_channels[name]:
            events.extend(sequence.get_events(channel))
    events.sort(key=sortfun)
    return events

def play_events(fs, events, bpm=120):
    beat_duration = 60.0/bpm
    t = events[0].time
    for event in events:
        dt = event.time - t
        if dt > 0:
            time.sleep(dt * beat_duration)
        t = event.time
        logger.warn("event %s from %s" % (event, event.source))
        event.occur(fs)
