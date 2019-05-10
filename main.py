import VoiceRecorder
import VoiceVad
import ExtractFeatures
import sys
import argparse
import time


def check_args(args=None):
    parser = argparse.ArgumentParser(description="Extract Voice Features")

    parser.add_argument('-D', '--duration',
                        help="Voice recording duration",
                        type=int,
                        default=5,
                        required=True)

    parser.add_argument('-S', '--subject',
                        help="Subject's name",
                        required=True
                        )

    parser.add_argument('-N', '--number',
                        help="Voice capture trial number",
                        type=int,
                        default=5,
                        required=5
                        )

    result = parser.parse_args()
    return result.duration, result.subject, result.number


def trial_record(dur, subject, trial=5):
    voice_list = []

    print('Perekaman suara akan dilakukan sebanyak %i kali' % trial)
    time.sleep(3)

    for i in range(1, trial+1):
        print('Perekaman ke %i' % i)
        for counter in range(5, 0, -1):
            print('Perekaman akan dilakukan dalam %i' % counter, end='\r')
            time.sleep(1)
        full_path = subject + '_' + str(i)
        voice = VoiceRecorder.voice_record(dur, full_path)
        print(voice)
        print('\n\n')
        voice_list.append(voice)

    return voice_list


def trial_vad(voice_path_list):
    vad_list = []

    for i in range(0, len(voice_path_list)):
        path = voice_path_list[i]
        print(type(path))
        vad = VoiceVad.get_vad(path)
        vad_list.append(vad)

    return vad_list


def trial_model(vad_path_list):
    for i in enumerate(vad_path_list):
        ExtractFeatures.generate_model(i)


def main():
    duration, subject, trial = check_args(sys.argv[1:])
    voice = trial_record(duration, subject, trial)
    vad = trial_vad(voice)
    trial_vad(vad)


if __name__ == '__main__':
    main()
