#!/usr/bin/python 
# based on : www.daniweb.com/code/snippet263775.html
import math
import wave
import struct

# Audio will contain a long list of samples (i.e. floating point numbers describing the
# waveform).  If you were working with a very long sound you'd want to stream this to
# disk instead of buffering it all in memory list this.  But most sounds will fit in 
# memory.
sample_rate = 44100.0


def append_sinewave(
        audio,
        freq=440.0, 
        duration_milliseconds=500, 
        volume=1.0):
    """
    The sine wave generated here is the standard beep.  If you want something
    more aggresive you could try a square or saw tooth waveform.   Though there
    are some rather complicated issues with making high quality square and
    sawtooth waves... which we won't address here :) 
    """ 

    num_samples = duration_milliseconds * (sample_rate / 1000.0)
    fade_portion = num_samples / 10

    for x in range(int(num_samples)):
        point = volume * math.sin(2 * math.pi * freq * ( x / sample_rate ))
        if x <= fade_portion:
            fade_multiplier = x / fade_portion
            point *= fade_multiplier

        elif x >= num_samples - fade_portion:
            start = num_samples - fade_portion
            fade_multiplier = (fade_portion - (x - start)) / fade_portion
            point *= fade_multiplier

        audio.append(point)

    return


def save_wav(audio, file_name):
    # Open up a wav file
    wav_file=wave.open(file_name,"w")

    # wav params
    nchannels = 1

    sampwidth = 2

    # 44100 is the industry standard sample rate - CD quality.  If you need to
    # save on file size you can adjust it downwards. The stanard for low quality
    # is 8000 or 8kHz.
    nframes = len(audio)
    comptype = "NONE"
    compname = "not compressed"
    wav_file.setparams((nchannels, sampwidth, sample_rate, nframes, comptype, compname))

    # WAV files here are using short, 16 bit, signed integers for the 
    # sample size.  So we multiply the floating point data we have by 32767, the
    # maximum value for a short integer.  NOTE: It is theortically possible to
    # use the floating point -1.0 to 1.0 data directly in a WAV file but not
    # obvious how to do that using the wave module in python.
    for sample in audio:
        wav_file.writeframes(struct.pack('h', int( sample * 32767.0 )))

    wav_file.close()

    return

for i in range(1, 100):
    audio = []
    print(i)
    hz = i * 10
    vol = 1 / (i ** 0.5)
    # volume = 1 / (i
    append_sinewave(audio, freq=hz, duration_milliseconds=100)

    path = "{:02d}.wav".format(i - 1)
    save_wav(audio, path)
