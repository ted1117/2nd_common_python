import json
from datetime import datetime
from typing import Any


def main():
    # file_path = input('파일 이름을 입력하세요: ')
    file_path = './mission_computer_main.log'
    json_file = './mission_computer_main.json'
    report_file_path = './log_analysis.md'

    try:
        preprocessed = read_log_file(file_path)
        sorted_log = sort_by_timestamp_desc(preprocessed)
        # log_dict = convert_list_to_dict(sorted_log)
        log_dict = convert_list_dict_without_nested(sorted_log)
        save_dict_to_json(json_file, log_dict)
        publish_analysis_report(sorted_log, report_file_path)
        # print_log_desc(file_path)
    except FileNotFoundError:
        print('해당 파일이 없습니다.')
    except UnicodeDecodeError:
        print('디코딩 과정에서 오류가 발생했습니다.')
    except Exception as e:
        print(e)


def read_log_file(path) -> list[Any]:
    """로그 파일을 읽기"""
    with open(path, 'r', encoding='utf-8') as f:
        preprocessed = preprocess_data(f)

    return preprocessed


def preprocess_data(f) -> list[Any]:
    """로그를 리스트 객체로 변환"""
    preprocessed = []
    next(f)  # 첫 줄 건너뛰기
    for line in f:
        if not line.strip():
            continue
        timestamp, level, msg = line.rstrip().split(',', 2)
        preprocessed.append([timestamp, level, msg])
    print('######### 로그 출력 #########')
    print(*preprocessed, sep='\n', end='\n\n')

    return preprocessed


def sort_by_timestamp_desc(preprocessed: list) -> list[Any]:
    """로그를 시간 역순으로 정렬"""
    log_list = sorted(
        preprocessed,
        key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'),
        reverse=True,
    )
    print('######### 시간 역순 출력 #########')
    print(*log_list, sep='\n', end='\n\n')
    # print()

    return log_list


def convert_list_to_dict(data: list) -> dict:
    """리스트를 dict로 변환"""
    analyzed_dict = {
        i: {'timestamp': timestamp, 'level': level, 'msg': msg}
        for i, (timestamp, level, msg) in enumerate(data)
    }

    print('######### dict 출력 #########')
    print(*analyzed_dict.values(), sep='\n', end='\n\n')

    return analyzed_dict


def convert_list_dict_without_nested(data: list) -> dict:
    analyzed_dict = {timestamp: msg for timestamp, _, msg in data}

    print('######### dict 출력 #########')
    # print(analyzed_dict, sep='\n', end='\n\n')
    for key, value in analyzed_dict.items():
        print(key, value)

    return analyzed_dict


def save_dict_to_json(json_file, log_dict):
    """dict를 json으로 변환 후 저장"""
    try:
        with open(json_file, 'w', encoding='utf-8') as jf:
            json.dump(log_dict, jf, ensure_ascii=False, indent=4)
        print(f"'{json_file}' 파일이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f'Error: JSON 파일 저장 중 오류 발생: {e}')


def publish_analysis_report(sorted_logs: list, file_path: str):
    """사고 원인 분석 보고서 작성"""
    report_content = """
# 사고 원인 분석 보고서

## 1. 개요

본 보고서는 `mission_computer_main.log` 파일을 기반으로 로켓 임무 수행 중 발생한 사고의 원인을 분석하기 위한 보고서이다.

## 2. 사고 발생 타임라인
"""
    key_events = []
    for log in sorted_logs:
        timestamp, _, message = log
        if (
            'explosion' in message
            or 'unstable' in message
            or 'landed' in message
            or 'completed' in message
        ):
            key_events.append(f'- **{timestamp}**: {message}')

    key_events.reverse()

    report_content += '\n'.join(key_events)

    report_content += """

## 3. 사고 원인 분석

1.  **임무 완료 후 문제 발생**: 로그에 따르면 로켓은 **11:28:00**에 안전하게 착륙(`Touchdown confirmed. Rocket safely landed.`)했고, **11:30:00**에 임무 성공(`Mission completed successfully.`)이 선언되었다.
2.  **산소 탱크 이상 징후**: 착륙 7분 후인 **11:35:00**에 `Oxygen tank unstable` 로그가 기록되며 산소 탱크가 불안정한 상태임이 처음으로 감지되었다.
3.  **폭발 발생**: 이상 징후 감지 5분 후인 **11:40:00**에 `Oxygen tank explosion` 로그가 기록되며 실제 폭발이 발생했다.

## 4. 결론

사고의 직접적인 원인은 **산소 탱크의 폭발**이다.

로켓이 지상에 안전하게 착륙했으나, 산소 탱크에 원인 불명의 문제로 인해 불안정한 상태가 발발되었고, 폭발로 이어졌다.

"""

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
    except Exception as e:
        raise IOError(f'Markdown 보고서 파일 저장 중 오류 발생: {e}')


def print_log_desc(file_path):
    print('\n######### 로그 역순 출력 #########')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in reversed(lines):
            print(line.strip())

    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f'파일을 읽는 중 오류가 발생했습니다: {e}')
    finally:
        print('#########\n')


def save_dict_with_danger_keywords(log_dict: dict) -> dict:
    list_with_danger_keywords = []
    danger_keywords = ('explosion', 'high temperature', 'leak', 'Oxygen')
    for log in log_dict.values():
        msg = log.get('msg', None)
        for keyword in danger_keywords:
            if keyword in msg:
                list_with_danger_keywords.append(log)
    dict_with_danger_keywords = {
        i: log for i, log in enumerate(list_with_danger_keywords)
    }

    return dict_with_danger_keywords


if __name__ == '__main__':
    main()
