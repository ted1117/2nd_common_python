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
    with pyzipper.AESZipFile(BytesIO(file_content)) as zf:
        smallest = search_smallest_file(zf)
        for i in range(start, end + 1):
            pwd = create_password(i)
            if is_unzipped(zf, smallest, pwd):
                print(f'Found by PID {mp.current_process().pid}: {pwd}')
                return pwd
    return None


def calculate_ranges(file_content, workers=6):
    term = TOTAL_CASE // workers
    ranges = []
    for i in range(workers):
        start = term * i
        end = TOTAL_CASE - 1 if i == workers - 1 else term * (i + 1) - 1
        ranges.append((file_content, start, end))
    return ranges


def main():
    file_path = 'Course5/Step1/emergency_storage_key.zip'
    workers = 6

    with open(file_path, 'rb') as f:
        file_content = f.read()

    ranges = calculate_ranges(file_content, workers)

    found = None
    with mp.Pool(processes=workers) as pool:
        for res in pool.imap_unordered(unzip_file, ranges):
            if res is not None:
                found = res
                pool.terminate()
                break
        pool.join()

    print('FOUND:', found)


if __name__ == '__main__':
    main()
