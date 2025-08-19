import io
import itertools
import multiprocessing
import os
import string
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue


def print_progress(message, end='\n', flush=True):
    """
    진행 상황을 실시간으로 업데이트하는 출력 함수
    """
    if end == '\r':
        # 현재 줄을 지우고 새로운 내용으로 덮어쓰기
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.write(message)
    else:
        print(message, end=end)

    if flush:
        sys.stdout.flush()


def format_time(seconds):
    """시간을 보기 좋게 포맷팅"""
    if seconds < 60:
        return f'{seconds:.1f}초'
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f'{minutes}분 {secs:.1f}초'
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f'{hours}시간 {minutes}분'


# 전역 변수로 상태 관리
found_password = None
stop_flag = threading.Event()
stats_lock = threading.Lock()
total_attempts = 0


def test_password_batch(args):
    """
    암호 배치를 테스트하는 워커 함수 (프로세스용)
    """
    zip_data, password_batch, process_id = args

    global found_password, stop_flag

    if stop_flag.is_set() or found_password:
        return None

    # 메모리에서 ZIP 파일 작업
    zip_buffer = io.BytesIO(zip_data)

    for password in password_batch:
        if stop_flag.is_set() or found_password:
            return None

        try:
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.setpassword(password.encode('utf-8'))
                # 첫 번째 파일 읽기 시도
                file_list = zip_ref.namelist()
                if file_list:
                    zip_ref.read(file_list[0])

                # 성공! 암호 발견
                print(f'\n🎉 프로세스 {process_id}에서 암호 발견!')
                return password

        except (RuntimeError, zipfile.BadZipFile):
            # 잘못된 암호 - 계속 시도
            continue
        except Exception:
            # 기타 오류 - 계속 시도
            continue

    return None


def test_password_thread(zip_data, password_batch, thread_id, result_queue):
    """
    암호 배치를 테스트하는 워커 함수 (스레드용)
    """
    global found_password, stop_flag, total_attempts

    if stop_flag.is_set() or found_password:
        return

    # 메모리에서 ZIP 파일 작업
    zip_buffer = io.BytesIO(zip_data)
    local_attempts = 0

    for password in password_batch:
        if stop_flag.is_set() or found_password:
            break

        local_attempts += 1

        try:
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.setpassword(password.encode('utf-8'))
                # 첫 번째 파일 읽기 시도
                file_list = zip_ref.namelist()
                if file_list:
                    zip_ref.read(file_list[0])

                # 성공! 암호 발견
                print(f'\n🎉 스레드 {thread_id}에서 암호 발견!')
                result_queue.put(password)
                stop_flag.set()
                return

        except (RuntimeError, zipfile.BadZipFile):
            # 잘못된 암호 - 계속 시도
            continue
        except Exception:
            # 기타 오류 - 계속 시도
            continue

    # 전역 시도 횟수 업데이트
    with stats_lock:
        global total_attempts
        total_attempts += local_attempts


def generate_password_batches(charset, length, batch_size):
    """
    암호 조합을 배치 단위로 생성하는 제너레이터
    """
    batch = []
    for password_tuple in itertools.product(charset, repeat=length):
        password = ''.join(password_tuple)
        batch.append(password)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    # 마지막 배치 처리
    if batch:
        yield batch


def unlock_zip():
    """
    병렬 처리를 이용한 ZIP 파일 암호 해독 함수
    """
    global found_password, stop_flag, total_attempts

    zip_filename = 'Course5/Step1/emergency_storage_key.zip'

    # 초기화
    found_password = None
    stop_flag.clear()
    total_attempts = 0

    # ZIP 파일 존재 확인
    try:
        if not os.path.exists(zip_filename):
            print(f'❌ 오류: {zip_filename} 파일을 찾을 수 없습니다.')
            return False
    except Exception as e:
        print(f'❌ 파일 확인 중 오류: {e}')
        return False

    # ZIP 파일을 메모리로 로드 (I/O 최적화)
    try:
        with open(zip_filename, 'rb') as f:
            zip_data = f.read()
        print(f'📁 ZIP 파일 ({len(zip_data):,} bytes)을 메모리로 로드했습니다.')
    except Exception as e:
        print(f'❌ ZIP 파일 로드 중 오류: {e}')
        return False

    # 암호 문자셋 정의
    charset = string.digits + string.ascii_lowercase
    password_length = 6

    # 시스템 정보
    cpu_count = multiprocessing.cpu_count()
    batch_size = 1000  # 각 배치당 암호 개수
    max_workers = min(cpu_count * 2, 16)  # 최대 워커 수 제한

    print('🔓 병렬 ZIP 파일 암호 해독을 시작합니다...')
    print(f'📁 대상 파일: {zip_filename}')
    print(f'🔤 문자셋: {charset}')
    print(f'📏 암호 길이: {password_length}자리')
    print(f'🔢 총 가능한 조합 수: {len(charset) ** password_length:,}개')
    print(f'💻 CPU 코어 수: {cpu_count}')
    print(f'🚀 워커 스레드 수: {max_workers}')
    print(f'📦 배치 크기: {batch_size:,}개')
    print('-' * 60)

    start_time = time.time()
    result_queue = Queue()
    last_update_time = start_time

    try:
        # 스레드풀을 이용한 병렬 처리
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            batch_count = 0

            print('🔍 암호 해독 진행 중...')
            print()  # 진행 상황용 빈 줄

            # 배치 생성 및 스레드에 할당
            for batch in generate_password_batches(
                charset, password_length, batch_size
            ):
                if stop_flag.is_set() or found_password:
                    break

                batch_count += 1
                future = executor.submit(
                    test_password_thread, zip_data, batch, batch_count, result_queue
                )
                futures.append(future)

                # 실시간 진행 상황 업데이트 (1초마다)
                current_time = time.time()
                if current_time - last_update_time >= 1.0:
                    elapsed_time = current_time - start_time
                    estimated_attempts = batch_count * batch_size
                    rate = estimated_attempts / elapsed_time if elapsed_time > 0 else 0

                    # 현재 테스트 중인 암호 예상
                    current_batch_start = (batch_count - 1) * batch_size
                    progress_percent = (
                        estimated_attempts / (len(charset) ** password_length)
                    ) * 100

                    progress_msg = (
                        f'⏱️  배치: {batch_count:,} | '
                        f'시도: {estimated_attempts:,} | '
                        f'진행률: {progress_percent:.3f}% | '
                        f'경과: {format_time(elapsed_time)} | '
                        f'속도: {rate:,.0f}/초'
                    )

                    print_progress(progress_msg, end='\r')
                    last_update_time = current_time

                # 결과 확인
                if not result_queue.empty():
                    found_password = result_queue.get()
                    stop_flag.set()
                    break

            # 완료될 때까지 대기하거나 암호 발견 시 중단
            while not stop_flag.is_set() and not result_queue.empty():
                try:
                    found_password = result_queue.get_nowait()
                    stop_flag.set()
                    break
                except:
                    time.sleep(0.1)

            # 모든 futures 완료 대기 (타임아웃 포함)
            for future in as_completed(futures, timeout=1):
                if stop_flag.is_set():
                    break

    except Exception as e:
        print(f'❌ 병렬 처리 중 오류: {e}')
        return False

    end_time = time.time()
    total_time = end_time - start_time

    # 결과 처리
    print_progress('', end='\n')  # 진행 상황 줄 마무리

    if found_password:
        print('\n' + '=' * 60)
        print('🎉 암호 해독 성공!')
        print(f'🔑 발견된 암호: {found_password}')
        print(f'⏱️  처리된 배치: {batch_count:,}개')
        print(f'🔢 예상 시도 횟수: {batch_count * batch_size:,}회')
        print(f'⌛ 총 소요 시간: {total_time:.2f}초')
        if total_time > 0:
            print(
                f'📊 평균 속도: {(batch_count * batch_size) / total_time:.0f} 시도/초'
            )
        print(f'🚀 병렬 처리로 인한 성능 향상: 약 {max_workers}배')
        print('=' * 60)

        # password.txt에 암호 저장
        try:
            with open('password.txt', 'w', encoding='utf-8') as f:
                f.write(found_password)
            print('💾 암호가 password.txt에 저장되었습니다.')
        except Exception as e:
            print(f'❌ password.txt 저장 중 오류: {e}')

        # result.txt에 최종 결과 저장
        try:
            with open('result.txt', 'w', encoding='utf-8') as f:
                f.write('병렬 ZIP 파일 암호 해독 결과\n')
                f.write(f'{"=" * 40}\n')
                f.write(f'파일명: {zip_filename}\n')
                f.write(f'발견된 암호: {found_password}\n')
                f.write(f'처리된 배치: {batch_count:,}개\n')
                f.write(f'예상 시도 횟수: {batch_count * batch_size:,}회\n')
                f.write(f'소요 시간: {total_time:.2f}초\n')
                if total_time > 0:
                    f.write(
                        f'평균 속도: {(batch_count * batch_size) / total_time:.0f} 시도/초\n'
                    )
                f.write(f'사용된 워커 수: {max_workers}개\n')
                f.write(f'성능 향상: 약 {max_workers}배\n')
            print('📄 최종 결과가 result.txt에 저장되었습니다.')
        except Exception as e:
            print(f'❌ result.txt 저장 중 오류: {e}')

        return True
    else:
        print('\n' + '=' * 60)
        print('❌ 암호 해독 실패')
        print(f'⏱️  처리된 배치: {batch_count:,}개')
        print(f'🔢 총 시도 횟수: {batch_count * batch_size:,}회')
        print(f'⌛ 총 소요 시간: {total_time:.2f}초')
        print('🔍 지정된 문자셋과 길이로는 암호를 찾을 수 없습니다.')
        print('=' * 60)
        return False


def main():
    """메인 실행 함수"""
    print('🚀 병렬 ZIP 파일 암호 해독 프로그램')
    print('⚡ 최적화된 고성능 버전')
    print('=' * 60)

    # 기존 결과 파일들 정리
    files_to_clean = ['password.txt', 'result.txt']
    for filename in files_to_clean:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f'🗑️  기존 {filename} 파일을 삭제했습니다.')
        except Exception as e:
            print(f'⚠️  {filename} 삭제 중 오류: {e}')

    print()

    # 암호 해독 실행
    success = unlock_zip()

    if success:
        print('\n✅ 프로그램이 성공적으로 완료되었습니다!')
    else:
        print('\n❌ 프로그램 실행이 실패했습니다.')


if __name__ == '__main__':
    main()
