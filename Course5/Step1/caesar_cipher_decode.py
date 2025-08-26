def read_txt(file: str) -> str | None:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = f.read().strip()

        return data
    except Exception as e:
        print(e)


def caesar_cipher_decode(target_text: str) -> list[str]:
    result = []
    uppercases = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lowercases = 'abcdefghijklmnopqrstuvwxyz'

    for i in range(1, 27):
        decoded = []
        ttu = uppercases[i:] + uppercases[:i]
        ttl = lowercases[i:] + lowercases[:i]
        for ch in target_text:
            if ch == ' ':
                decoded.append(' ')
            elif ch.isupper():
                decoded.append(uppercases[ttu.index(ch)])
            else:
                decoded.append(lowercases[ttl.index(ch)])
        # decoded.append('\n')
        decoded_txt = ''.join(decoded)
        print(f'{i}) {decoded_txt}', end='\n')
        result.append(decoded_txt)

    return result


def save_password(txt: str, filename: str = 'Course5/Step1/result.txt'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(txt)
            print(f"'{txt}'를 'result.txt'에 저장했습니다.")
    except Exception as e:
        print(e)


def save_passwords(data: list, filename: str = 'Course5/Step1/result.txt'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(data)
    except Exception as e:
        print(e)


def main():
    encoded_txt = read_txt('Course5/Step1/password.txt')
    if encoded_txt is None:
        return
    result = caesar_cipher_decode(encoded_txt)
    while True:
        try:
            choice = int(input('저장할 암호 번호를 입력하세요: '))
            if choice < 1 or choice > len(result):
                raise ValueError
            break
        except ValueError:
            print('숫자를 다시 입력하세요.')

    save_password(result[choice - 1])


if __name__ == '__main__':
    main()
