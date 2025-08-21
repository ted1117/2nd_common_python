import multiprocessing as mp

import pyzipper

PWD_LEN = 6
ALPHANUM = 'abcdefghijklmnopqrstuvwxyz0123456789'
NUMALPHA = '0123456789abcdefghijklmnopqrstuvwxyz'

BASE = len(NUMALPHA)
TOTAL_CASE = BASE**PWD_LEN  # 36^6


def create_password(index: int):
    tmp = ['a'] * PWD_LEN
    for i in range(PWD_LEN - 1, -1, -1):
        index, remainder = divmod(index, BASE)
        tmp[i] = NUMALPHA[remainder]
    return ''.join(tmp)


def calculate_range(filepath, workers: int = 6):
    ranges = []
    for i in range(workers):
        term = TOTAL_CASE // workers
        start = term * i
        end = term * (i + 1) - 1
        ranges.append((filepath, start, end))

    return ranges


def search_smallest_file(zf):
    info_list = sorted(zf.infolist(), key=lambda x: x.file_size)
    return info_list[0].filename


def is_unzipped(zf, smallest_file, pwd):
    try:
        zf.read(smallest_file, pwd=pwd.encode('utf-8'))

        return True
    except RuntimeError:
        return False


def unzip_file(file_path, start, end):
    try:
        with pyzipper.AESZipFile(file_path) as zf:
            smallest_file = search_smallest_file(zf)
            for i in range(start, end + 1):
                pwd = create_password(i)

                if is_unzipped(zf, smallest_file, pwd):
                    return pwd

    except Exception as e:
        print(e)


def main():
    try:
        # print(calculate_range())
        file_path = 'Course5/Step1/emergency_storage_key.zip'
        # file_path = 'Course5/Step1/mars_base.zip'
        workers = 6
        ranges = calculate_range(file_path)
        with mp.Pool(processes=workers) as pool:
            print('pool start')
            results = pool.starmap(unzip_file, ranges)

            print(results)
    except KeyboardInterrupt:
        print('shit!')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
