import collections
import contextlib
import wave
import webrtcvad
import re
import os


def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_chs = wf.getnchannels()
        assert num_chs == 1, 'Audio should be in mono format'
        sample_width = wf.getsampwidth()
        assert sample_width == 2, 'Sample should be in 2 bytes'
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000), 'Sampling rate should be in 8kHz, 16kHz, 32kHz, or 48kHz'
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_dur_ms, audio, sample_rate):
    n = int(sample_rate * (frame_dur_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    dur = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, dur)
        timestamp += dur
        offset += n


def vad_collector(sample_rate, frame_dur_ms,
                  pad_dur_ms, vad, frames):
    num_pad_frames = int(pad_dur_ms / frame_dur_ms)
    ring_buffer = collections.deque(maxlen=num_pad_frames)
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    """
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    """

    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])


def get_vad(source_path):
    """
    Extract VAD from audio source. Audio source should be match to WebRTC specification

    :param source_path: raw voice directory location. It should from raw/<subject>_<n_trial>.wav
    :return: dest_path : VAD destination directory location. It should go to vad/<subject>/<subject>_<n_trial>.wav
    """
    subject_dir = re.findall(r"[\w']+", source_path)[1]
    fname = re.split("[/.]+", source_path)[1]
    audio, sr = read_wave(source_path)
    vad = webrtcvad.Vad(1)
    frames = frame_generator(30, audio, sr)
    frames = list(frames)
    segments = vad_collector(sr, 30, 300, vad, frames)

    vad_dir = 'vad/'
    full_path = vad_dir + subject_dir + '/'

    if not os.path.exists(vad_dir):
        os.makedirs(vad_dir)

    if not os.path.exists(full_path):
        os.makedirs(full_path)


    # for i, segment in enumerate(segments):
    #     dest_path = '%s-%002d.wav' % (full_path, i)
    #     print(' Writing %s' % (dest_path,))
    #     write_wave(dest_path, segment, sr)

    # Expect only generated 1 VAD every voice record
    dest_path = full_path + '%s.wav' % fname
    print(' Writing %s' % dest_path)
    write_wave(dest_path, next(segments), sr)

    print('extract vad is success!')

    return dest_path
