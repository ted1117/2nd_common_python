import os
import zipfile

import cv2


class MasImageHelper:
    def __init__(self, img_dir: str) -> None:
        self.img_dir = img_dir

        self.img_files = sorted(
            f for f in os.listdir(img_dir) if f.lower().endswith(('png', 'jpg', 'jpeg'))
        )

        if not self.img_files:
            raise FileNotFoundError

        self.cur_index = 0

    def show_and_navigate(self):
        while True:
            img_path = self.img_dir + '/' + self.img_files[self.cur_index]
            img = cv2.imread(img_path)

            if img is not None:
                cv2.imshow('', img)
            else:
                print('경고: 파일이 없음요')
                return

            key = cv2.waitKeyEx(0)  # 키 코드 반환

            # 키 조작
            match key:
                case 63235:  # 오른쪽 화살표
                    self.cur_index = (self.cur_index + 1) % len(self.img_files)
                case 63234:  # 왼쪽 화살표
                    self.cur_index = (self.cur_index - 1) % len(self.img_files)
                case 27:  # ESC
                    break
                case _:
                    continue

        cv2.destroyAllWindows()


def main():
    zip_file = 'Course5/Step4/cctv.zip'
    extract_folder = 'Course5/Step4/CCTV'

    if os.path.exists(zip_file):
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zf.extractall(extract_folder)
    else:
        print('엥')
        return

    try:
        window = MasImageHelper(extract_folder)
        window.show_and_navigate()
    except FileNotFoundError as e:
        print(e)


if __name__ == '__main__':
    main()
