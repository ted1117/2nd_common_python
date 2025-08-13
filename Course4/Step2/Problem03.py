from pathlib import Path

import numpy as np
from numpy.typing import NDArray


def load_data(files: tuple):
    try:
        array_list = [
            np.genfromtxt(
                file,
                dtype=[('parts', 'U64'), ('strength', 'i4')],
                delimiter=',',
                skip_header=1,
                encoding='utf-8',
                autostrip=True,
            )
            for file in files
        ]

        return np.concatenate(array_list)
    except FileNotFoundError:
        print(f'파일이 존재하지 않습니다: {files}')
    except PermissionError:
        print('파일 읽기 권한이 없습니다.')
    except Exception as e:
        print(f'파일을 읽는 과정에서 오류가 발생했습니다: {e}')


def calculate_means_per_parts(array: NDArray) -> NDArray:
    unique_parts = np.unique(array['parts'])
    strength_list = []

    for part in unique_parts:
        strengths = array['strength'][array['parts'] == part]
        strength_mean = np.mean(strengths)
        print(f'{part}의 평균 강도: {strength_mean:.3f}')
        strength_list.append((part, strength_mean))

    result_dtype = [('parts', 'U64'), ('strength', 'f8')]

    strength_mean_array = np.array(strength_list, dtype=result_dtype)

    return strength_mean_array


def filter_value(array: NDArray, file_path: Path, upper_bound: float = 50.0):
    filter_mask = array['strength'] < upper_bound

    output_array = array[filter_mask]

    if output_array.size == 0:
        print(f'strength가 {upper_bound}보다 작은 데이터가 없습니다.')
    else:
        print(output_array)

    header = 'parts,strength'

    try:
        np.savetxt(
            fname=file_path,
            X=output_array,
            fmt=['%s', '%f'],
            delimiter=',',
            header=header,
            comments='',
            encoding='utf-8',
        )
    except PermissionError:
        print('파일 쓰기 권한이 없습니다.')
    except Exception as e:
        print(f'파일을 저장하는 과정에서 오류가 발생했습니다: {e}')


def main():
    BASE_DIR = Path(__file__).resolve().parent
    files = (
        BASE_DIR / 'mars_base/mars_base_main_parts-001.csv',
        BASE_DIR / 'mars_base/mars_base_main_parts-002.csv',
        BASE_DIR / 'mars_base/mars_base_main_parts-003.csv',
    )

    output_file = BASE_DIR / 'parts_to_work_on.csv'

    # 데이터 불러오기
    parts = load_data(files)

    if parts is None:
        print('파일 처리 중에 오류가 발생했습니다.')
        return

    if parts.size == 0:
        print('데이터가 없습니다.')
        return

    # part별 강도 평균 구하기
    parts_mean_array = calculate_means_per_parts(parts)

    # 평균 강도가 50보다 작은 part만 분류해서 저장
    filter_value(parts_mean_array, output_file, 50)


if __name__ == '__main__':
    main()
