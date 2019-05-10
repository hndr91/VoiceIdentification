import pyaudio
import wave
import os


class RecordingFile(object):
    """
    Write voice using PyAudio
    """

    def __init__(self, fname, mode, channels, rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, trackback):
        self.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def record(self, duration):
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                    channels=self.channels,
                                    rate=self.rate,
                                    input=True,
                                    frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None


class Recorder(object):

    def __init__(self, channels=1, rate=16000, frames_per_buffer=1024):
        """Recorder class to record voice based on webrtc criteria

        :param channels: audio channel should be 1
        :param rate: audi frame rate should be 8kHz, 16kHz, 32kHz, or 48kHz
        :param frames_per_buffer: frames per buffer default value is 1024
        """
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate, self.frames_per_buffer)


def voice_record(dur=5, person='test'):
    path = 'raw/'
    fname = person + '.wav'

    if not os.path.exists(path):
        os.makedirs(path)

    full_path = path + fname

    rec = Recorder(channels=1)
    with rec.open(full_path, 'wb') as rec:
        rec.record(duration=dur)

    print('done')
    return full_path
