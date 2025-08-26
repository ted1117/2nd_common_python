import multiprocessing as mp
import time
from datetime import datetime
from io import BytesIO

import pyzipper

PWD_LEN = 6
ALPHANUM = 'abcdefghijklmnopqrstuvwxyz0123456789'
NUMALPHA = '0123456789abcdefghijklmnopqrstuvwxyz'
BASE = len(NUMALPHA)
TOTAL_CASE = BASE**PWD_LEN  # 36^6


def create_password(index: int) -> str:
    tmp = ['a'] * PWD_LEN
    for i in range(PWD_LEN - 1, -1, -1):
        index, r = divmod(index, BASE)
        tmp[i] = ALPHANUM[r]
    return ''.join(tmp)


def search_smallest_file(zf):
    return min(zf.infolist(), key=lambda x: x.file_size).filename


def is_unzipped(zf, file, pwd) -> bool:
    try:
        zf.read(file, pwd=pwd.encode('utf-8'))
        return True
    except Exception:
        return False


def unlock_zip(args):
    file_content, start, end = args
    zf = None
    start_time = time.time()

    try:
        zf = pyzipper.AESZipFile(BytesIO(file_content))
        smallest = search_smallest_file(zf)
        for i in range(start, end + 1):
            pwd = create_password(i)

            if i % 100000 == 0:
                elapsed_time = time.time() - start_time
                print(
                    f'PID {mp.current_process().pid}: 시도 횟수 {i}, 현재 암호 {pwd}, 경과 시간 {elapsed_time:.2f}초'
                )

            if is_unzipped(zf, smallest, pwd):
                elapsed_time = time.time() - start_time
                print(
                    f'PID {mp.current_process().pid}에서 암호 발견: {pwd} (시도 횟수: {i}, 경과 시간: {elapsed_time:.2f}초)'
                )
                return pwd
    except KeyboardInterrupt:
        return None
    finally:
        if zf is not None:
            try:
                zf.close()
            except:
                pass
    return None


def calculate_ranges(file_content, workers=6) -> list[tuple]:
    term = TOTAL_CASE // workers
    ranges = []
    for i in range(workers):
        start = term * i
        end = TOTAL_CASE - 1 if i == workers - 1 else term * (i + 1) - 1
        ranges.append((file_content, start, end))
    return ranges


def save_password_to_file(pwd: str, filename: str = 'password.txt'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(pwd)
        print(f'{filename}에 암호가 저장되었습니다.')
    except Exception as e:
        print(f'암호를 파일로 저장하는데 오류가 발생했습니다: {e}')


def main():
    file_path = 'Course5/Step1/emergency_storage_key.zip'
    workers = 6

    with open(file_path, 'rb') as f:
        file_content = f.read()

    ranges = calculate_ranges(file_content, workers)

    found = None
    pool = None

    # 시작 시간 기록
    start_time = time.time()
    start_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'암호 해독 시작: {start_datetime}')
    print(f'총 {TOTAL_CASE:,}개의 조합을 {workers}개 프로세스로 시도합니다.')
    print('-' * 50)

    try:
        with mp.Pool(processes=workers) as pool:
            for res in pool.imap_unordered(unlock_zip, ranges):
                if res is not None:
                    found = res
                    pool.terminate()
                    break

        total_elapsed = time.time() - start_time
        end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print('-' * 50)
        print(f'암호 해독 종료: {end_datetime}')
        print(f'총 소요 시간: {total_elapsed:.2f}초')
        print(f'발견된 암호: {found}')

        if found:
            save_password_to_file(found)
        else:
            print('암호를 찾지 못했습니다.')

    except KeyboardInterrupt:
        total_elapsed = time.time() - start_time
        end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('\n' + '-' * 50)
        print('Keyboard Interrupt Detected')
        print(f'중단 시간: {end_datetime}')
        print(f'진행 시간: {total_elapsed:.2f}초')
        if pool is not None:
            try:
                pool.terminate()
                pool.join()
            except:
                pass


if __name__ == '__main__':
    main()
