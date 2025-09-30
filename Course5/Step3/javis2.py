import csv
import datetime
import os

import mlx_whisper
import speech_recognition as sr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDS_DIR = os.path.join(BASE_DIR, 'records')


def format_timestamp(seconds: float) -> str:
    """초를 시:분:초 형식으로 변환"""
    total = int(round(seconds))
    h, m, s = total // 3600, (total % 3600) // 60, total % 60
    return f'{h:02d}:{m:02d}:{s:02d}'


def make_csv_path(audio_path: str) -> str:
    name, _ = os.path.splitext(audio_path)
    return f'{name}.csv'


class AudioRecorder:
    def __init__(self, device_index: int):
        self.recognizer = sr.Recognizer()
        self.records_dir = RECORDS_DIR
        self.device_index = device_index

    def save(self, audio: sr.AudioData) -> str:
        """지정된 경로에 녹음파일을 wav 파일로 저장"""
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S')
        file_path = os.path.join(RECORDS_DIR, f'{timestamp}.wav')

        os.makedirs(self.records_dir, exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(audio.get_wav_data())

        return file_path

    def capture(self) -> sr.AudioData:
        """지정된 마이크로 음성 녹음"""
        print('녹음을 시작합니다.')
        with sr.Microphone(device_index=self.device_index) as source:
            self.recognizer.pause_threshold = 2.5
            audio: sr.AudioData = self.recognizer.listen(source, phrase_time_limit=50)  # type: ignore

        return audio

    def record_and_save(self):
        audio = self.capture()
        self.save(audio)


class SpeechTranscriber:
    def __init__(
        self,
        model_repo: str = 'mlx-community/whisper-large-v3-mlx',
        language: str = 'ko',
    ) -> None:
        self.model_repo = model_repo
        self.language = language

    def transcribe_audio(self, audio_path: str):
        try:
            result: dict = mlx_whisper.transcribe(
                audio=audio_path,
                path_or_hf_repo=self.model_repo,
                language=self.language,
                word_timestamps=False,
            )

            # dict 선언해서 시작 시간과 텍스트 내용 담기
            segments: list[dict] = result.get('segments', [])
            if not segments:
                return
            data = []
            if segments:
                for segment in segments:
                    start = segment.get('start', 0.0)
                    text = segment.get('text', '').strip()
                    if text:
                        data.append((format_timestamp(float(start)), text))
            else:
                text = result.get('text', '').strip()
                if text:
                    data.append(('00:00:00', text))

            return data

        except Exception as e:
            print(e)

    def to_csv(self, rows: list, csv_path: str):
        try:
            with open(csv_path, 'w', encoding='utf-8', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(['Timestamp', 'Text'])
                writer.writerows(rows)
            print(f'csv 파일이 저장되었습니다.\n{csv_path}')
        except PermissionError:
            print('파일 쓰기 권한이 없습니다.')
        except Exception as e:
            print(f'csv 파일을 저장하는 과정에서 오류가 발생했습니다.\n오류: {e}')


def list_recorded_files() -> str | None:
    print('=' * 10 + ' 파일 목록 ' + '=' * 10)
    files: list = [file for file in os.listdir(RECORDS_DIR) if file.endswith('.wav')]
    files.sort()
    if not files:
        print('녹음된 파일이 없습니다.')
        return

    for idx, file in enumerate(files):
        print(f'{idx + 1}) {file}')

    num_input = input('파일을 선택하세요: ').strip()

    if num_input.strip().lower() == 'q':
        print('프로그램을 종료합니다.')
        return

    try:
        choice = int(num_input) - 1
        file = files[choice]
        return os.path.join(RECORDS_DIR, file)

    except ValueError:
        print('잘못 입력하셨습니다.')


def choose_mic_index() -> int | None:
    print('=' * 10 + ' 마이크 목록' + '=' * 10)
    names: list = sr.Microphone.list_microphone_names() or []
    for idx, name in enumerate(names):
        print(f'{idx + 1}) {name}')

    while True:
        num_input = input('마이크를 선택하세요: ').strip().lower()

        if num_input == 'q':
            return None

        try:
            choice = int(num_input) - 1

            if choice not in range(len(names)):
                raise ValueError
            return choice
        except ValueError:
            print('잘못 입력하셨습니다.\n다시 입력하세요.')


def main():
    while True:
        print('=' * 10 + ' 메뉴 ' + '=' * 10)
        print('1) 파일 목록 불러오기')
        print('2) 새로 녹음하기')
        print('q) 종료')
        sel = input('메뉴를 선택하세요: ').strip().lower()

        match sel:
            case '1':
                audio = list_recorded_files()
                if audio is None:
                    return
                transcriber = SpeechTranscriber()
                data = transcriber.transcribe_audio(audio)
                if data is None:
                    return
                csv_path = make_csv_path(audio)
                transcriber.to_csv(data, csv_path)
            case '2':
                mic_index = choose_mic_index()
                if mic_index is None:
                    print('녹음이 취소됐습니다.')
                    continue

                recorder = AudioRecorder(device_index=mic_index)
                recorder.record_and_save()
            case 'q':
                print('종료합니다.')
                break
            case _:
                print('잘못 입력했습니다.')


if __name__ == '__main__':
    main()
