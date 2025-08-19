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


def calculate_range(workers: int = 6):
    for i in range(workers):
        term = TOTAL_CASE // workers
        start = term * i
        end = term * (i + 1) - 1

    return start, end


def main(): ...


if __name__ == '__main__':
    main()
