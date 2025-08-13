import csv
from pathlib import Path


def main():
    # 파일 경로 설정
    BASE_DIR = Path(__file__).resolve().parent
    csv_file = BASE_DIR / 'mars_base/Mars_Base_Inventory_List.csv'
    result_file = BASE_DIR / 'Mars_Base_Inventory_danger.csv'

    # 데이터 처리
    data_list = read_csv_file(csv_file)

    if data_list is None:
        return

    if not data_list:
        print('처리할 데이터가 없습니다.')
        return

    sorted_data = sort_data_by_flammability_index_desc(data_list)
    filtered_data = filter_data_by_flammability(sorted_data)

    # 결과 저장
    save_data_to_csv(data=filtered_data, csv_file=result_file)


def read_csv_file(csv_file) -> list[str] | None:
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            data_list = process_csv(f)

        return data_list
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {csv_file}')
    except PermissionError:
        print('파일 읽기 권한이 없습니다.')
    except Exception as e:
        print(f'파일을 읽는 과정에서 오류가 발생했습니다: {e}')


def process_csv(content) -> list[str]:
    next(content)

    data_list = [line.rstrip().split(',', 4) for line in content]

    print('\n==================== 첫 번째 출력 =======================')
    print(*data_list, sep='\n', end='\n\n')

    return data_list


def sort_data_by_flammability_index_desc(data: list) -> list[str]:
    sorted_data = sorted(data, key=lambda x: float(x[4]), reverse=True)

    print('\n==================== 두 번째 출력 =======================')
    print(*sorted_data, sep='\n', end='\n\n')

    return sorted_data


def filter_data_by_flammability(data: list, threshold: float = 0.7) -> list[str]:
    filtered_data = list(filter(lambda x: float(x[4]) >= threshold, data))

    print('\n==================== 세 번째 출력 =======================')
    print(*filtered_data, sep='\n', end='\n\n')

    return filtered_data


def save_data_to_csv(data: list, csv_file: Path):
    try:
        with open(csv_file, 'w', encoding='utf-8', newline='') as cf:
            writer = csv.writer(cf)
            writer.writerow(
                [
                    'Substance',
                    'Weight (g/cm³)',
                    'Specific Gravity',
                    'Strength',
                    'Flammability',
                ]
            )

            writer.writerows(data)
    except PermissionError:
        print('파일 쓰기 권한이 없습니다.')
    except Exception as e:
        print(f'파일을 저장하는 과정에서 오류가 발생했습니다.\n오류: {e}')


if __name__ == '__main__':
    main()
