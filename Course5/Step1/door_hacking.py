# door_hacking.py

import itertools
import sys
import time
import zipfile
import zlib  # 1. zlib 라이브러리를 임포트합니다.
from pathlib import Path


def unlock_zip(zip_filename='emergency_storage_key.zip', result_filename='result.txt'):
    """
    숫자와 소문자 알파벳으로 구성된 6자리 암호를 브루트포스 방식으로 찾아
    zip 파일의 압축을 해제하고 암호를 파일에 저장합니다.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    password_length = 6

    print('=' * 50)
    print(f"'{zip_filename}' 파일의 암호 해독을 시작합니다.")
    print(f'암호 조합: 숫자(0-9), 소문자 알파벳(a-z), 길이 {password_length}자리')
    print('=' * 50)

    start_time = time.time()
    attempts = 0

    try:
        zip_file = zipfile.ZipFile(zip_filename, 'r')
    except FileNotFoundError:
        print(f"오류: '{zip_filename}' 파일을 찾을 수 없습니다.")
        print('스크립트와 같은 폴더에 파일이 있는지 확인해주세요.')
        return
    except zipfile.BadZipFile:
        print(f"오류: '{zip_filename}' 파일이 유효한 ZIP 파일이 아닙니다.")
        return

    try:
        for p in itertools.product(chars, repeat=password_length):
            attempts += 1
            password = ''.join(p)

            elapsed_time = time.time() - start_time
            print(
                f' > 시도 횟수: {attempts:,} | 진행 시간: {elapsed_time:.2f}초 | 현재 암호: {password}',
                end='\r',
            )
            sys.stdout.flush()

            try:
                zip_file.extractall(pwd=password.encode('utf-8'))

                end_time = time.time()
                total_elapsed_time = end_time - start_time

                print(' ' * 80, end='\r')

                print('\n' + '=' * 50)
                print('성공! 암호를 찾았습니다.')
                print(f' > 최종 암호: {password}')
                print(f' > 총 시도 횟수: {attempts:,}회')
                print(f' > 총 걸린 시간: {total_elapsed_time:.2f}초')
                print('=' * 50)

                try:
                    with open(result_filename, 'w') as f:
                        f.write(password)
                    print(f"'{result_filename}' 파일에 암호를 성공적으로 저장했습니다.")
                except IOError as e:
                    print(f"오류: '{result_filename}' 파일 저장에 실패했습니다. ({e})")

                break

            # 2. 여기에 zlib.error를 추가하여 암호가 틀렸을 때의 오류를 처리합니다.
            except (RuntimeError, zipfile.BadZipFile, zlib.error):
                continue

        else:
            print('\n' + '=' * 50)
            print('실패. 가능한 모든 조합을 시도했지만 암호를 찾지 못했습니다.')
            print('암호의 구성 조건(길이, 문자셋)을 다시 확인해주세요.')
            print('=' * 50)

    finally:
        print('\n작업을 종료하며 리소스를 정리합니다.')
        zip_file.close()


if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent
    file_path = str(BASE_DIR / 'emergency_storage_key.zip')
    unlock_zip(zip_filename=file_path)
