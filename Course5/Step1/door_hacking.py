import multiprocessing as mp
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


def is_unzipped(zf, smallest_file, pwd) -> bool:
    try:
        zf.read(smallest_file, pwd=pwd.encode('utf-8'))
        return True
    except Exception:
        return False


def unzip_file(args):
    file_content, start, end = args
    zf = None
    try:
        zf = pyzipper.AESZipFile(BytesIO(file_content))
        smallest = search_smallest_file(zf)
        for i in range(start, end + 1):
            pwd = create_password(i)

            if i % 100000 == 0:
                print(f'PID {mp.current_process().pid}: {pwd}')

            if is_unzipped(zf, smallest, pwd):
                print(f'Found by PID {mp.current_process().pid}: {pwd}')
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


def save_password_to_file(pwd: str, filename: str = 'result.txt'):
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

    try:
        with mp.Pool(processes=workers) as pool:
            for res in pool.imap_unordered(unzip_file, ranges):
                if res is not None:
                    found = res
                    pool.terminate()
                    break

        print('암호:', found)

        if found:
            save_password_to_file(found)
        else:
            print('암호를 찾지 못했습니다.')

    except KeyboardInterrupt:
        print('\nKeyboard Interrupt Detected')
        if pool is not None:
            try:
                pool.terminate()
                pool.join()
            except:
                pass


if __name__ == '__main__':
    main()
