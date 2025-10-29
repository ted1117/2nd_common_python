import os
import zipfile

import cv2


class MasImageHelper:
    def __init__(self, img_dir: str) -> None:
        self.img_dir = img_dir

        self.person_detector = cv2.HOGDescriptor()
        self.person_detector.setSVMDetector(
            cv2.HOGDescriptor_getDefaultPeopleDetector()  # type: ignore
        )

        self.img_files = sorted(
            f
            for f in os.listdir(img_dir)
            if cv2.imread(os.path.join(img_dir, f)) is not None
        )

        if not self.img_files:
            raise FileNotFoundError(
                '이미지 디렉토리에서 유효한 이미지 파일을 찾을 수 없습니다.'
            )

        print(*self.img_files, sep='\n')

    def search_for_people(self):
        person_found_and_displayed = False

        for img_file in self.img_files:
            img_path = os.path.join(self.img_dir, img_file)
            img = cv2.imread(img_path)

            if img is None:
                continue

            # 이 함수는 (감지된 사각형 목록, 신뢰도 점수 목록)을 반환합니다.
            rects, _ = self.person_detector.detectMultiScale(
                img,
                winStride=(4, 4),  # 스캔 윈도우의 이동 간격
                padding=(8, 8),  # 스캔 윈도우 주변의 여백
                scale=1.05,  # 이미지 피라미드 스케일
            )

            # 3. 한 명이라도 사람이 검출되었다면
            if len(rects) > 0:
                print(
                    f"'{img_file}' 파일에서 사람을 찾았습니다. 화면에 이미지를 출력합니다."
                )
                person_found_and_displayed = True

                for x, y, w, h in rects:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

                cv2.imshow('Person Detected', img)

                # 키 입력을 대기합니다.
                key = cv2.waitKey(0)

                if key == 13:  # Enter 키를 누르면
                    print('다음 사진을 계속 검색합니다...')
                    cv2.destroyWindow('Person Detected')
                    continue
                elif key == 27:  # ESC 키를 누르면
                    print('검색을 중단합니다.')
                    break

        if not person_found_and_displayed:
            print('모든 사진을 확인했지만 사람을 찾지 못했습니다.')
        else:
            print('모든 사진 검색이 끝났습니다.')

        cv2.destroyAllWindows()


def main():
    zip_file = 'Course5/Step4/cctv.zip'
    extract_folder = 'Course5/Step4/CCTV/'

    if os.path.exists(zip_file):
        if not os.path.exists(extract_folder):
            os.makedirs(extract_folder)
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zf.extractall(extract_folder)
    else:
        print(f"'{zip_file}'을 찾을 수 없습니다.")
        return

    try:
        window = MasImageHelper(extract_folder)
        window.search_for_people()
    except FileNotFoundError as e:
        print(e)


if __name__ == '__main__':
    main()
