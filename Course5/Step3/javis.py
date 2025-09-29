import datetime
import os

import speech_recognition as sr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDS_DIR = os.path.join(BASE_DIR, 'records')


class RecordAudio:
    def __init__(self, device_index: int) -> None:
        self.recognizer = sr.Recognizer()
        self.records_dir = RECORDS_DIR
        self.device_index = device_index

    def save(self, audio: sr.AudioData):
        """지정된 경로에 녹음파일을 wav 파일로 저장"""
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S')
        file_path = os.path.join(RECORDS_DIR, f'{timestamp}.wav')

        os.makedirs(self.records_dir, exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(audio.get_wav_data())

    def record(self) -> sr.AudioData:
        """지정된 마이크로 음성 녹음"""
        print('녹음을 시작합니다.')
        with sr.Microphone(device_index=self.device_index) as source:
            audio: sr.AudioData = self.recognizer.listen(source)  # type: ignore

        return audio

    def record_and_save(self):
        audio = self.record()
        self.save(audio)


def main():
    print('=' * 10 + ' 마이크 목록' + '=' * 10)
    names: list = sr.Microphone.list_microphone_names() or []
    for idx, name in enumerate(names):
        print(f'{idx + 1}: {name}')

    while True:
        num_input = input('마이크를 선택하세요: ')

        try:
            choice = int(num_input) - 1

            if choice not in range(len(names)):
                raise ValueError
        except ValueError:
            if num_input.lower() == 'q':
                print('프로그램을 종료합니다.')
                quit()
            else:
                print('잘못 입력하셨습니다.\n다시 입력하세요.')
                continue

        break

    recorder = RecordAudio(device_index=choice)
    recorder.record_and_save()


if __name__ == '__main__':
    main()
