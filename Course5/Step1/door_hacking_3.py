# door_hacking.py
"""
- emergency_storage_key.zip 암호(소문자 a-z + 숫자 0-9, 길이 6) 브루트포스
- pyzipper(AES 지원) + 멀티프로세스(범위 분할)
- 출력: 전역(전체) 진행률만 0.5초마다 갱신 (총 시도/퍼센트)
- 성공 시: 암호를 콘솔에 출력하고, BASE_DIR에 password.txt, result.txt 저장
"""

import datetime
import multiprocessing as mp
import platform
import string
import time
from pathlib import Path
from typing import Optional, Tuple

import pyzipper  # pip install pyzipper

# ==============================
# 경로/상수
# ==============================
BASE_DIR = Path(__file__).resolve().parent
ZIP_PATH = BASE_DIR / 'emergency_storage_key.zip'
PASS_TXT = BASE_DIR / 'password.txt'
RESULT_TXT = BASE_DIR / 'result.txt'

ALPHABET = (
    string.ascii_lowercase + string.digits
)  # "abcdefghijklmnopqrstuvwxyz0123456789"
PWD_LEN = 6
BASE = len(ALPHABET)  # 36
TOTAL_SPACE = BASE**PWD_LEN  # 36^6

# 진행 관련
PROGRESS_INTERVAL = 100_000  # 각 워커가 N회 시도하면 전역 카운터에 반영
GLOBAL_PROGRESS_INTERVAL_SEC = 0.5  # 전역 진행률 출력 주기(초)


# ==============================
# 유틸
# ==============================
def _safe_write_text(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(f'\n[오류] 파일 저장 실패: {path} -> {e}')


def _pick_smallest_member(zf: pyzipper.AESZipFile) -> Optional[str]:
    """가장 작은 파일 항목 선택(복호화 비용 최소화)"""
    try:
        infos = [i for i in zf.infolist() if not str(i.filename).endswith('/')]
        if not infos:
            return None
        infos.sort(key=lambda x: getattr(x, 'file_size', 0))
        return infos[0].filename
    except Exception:
        return None


def _int_to_pwd(n: int) -> str:
    """정수(0 <= n < 36^6) → 길이 6의 base-36 문자열(a-z0-9)"""
    buf = ['a'] * PWD_LEN
    for i in range(PWD_LEN - 1, -1, -1):
        n, r = divmod(n, BASE)
        buf[i] = ALPHABET[r]
    return ''.join(buf)


def _try_password_pyzipper(zf: pyzipper.AESZipFile, member: str, pwd: str) -> bool:
    """pyzipper로 암호 시도: 성공 시 True (1바이트만 읽어 검증)"""
    try:
        with zf.open(member, 'r', pwd=pwd.encode('utf-8')) as fp:
            _ = fp.read(1)
        return True
    except Exception:
        return False


# ==============================
# 워커(범위 분할)
# ==============================
def _worker_range(
    zip_path: Path,
    start_idx: int,
    end_idx: int,
    found_evt,
    attempts_total,  # 모든 워커 합산 시도 수
    found_queue: mp.Queue,  # 찾은 암호를 메인으로 전달
):
    """
    [start_idx, end_idx) 구간을 직선 탐색.
    - PROGRESS_INTERVAL마다 전역 카운터에 누적
    - 성공 시 found_queue에 암호 전달 + found_evt set
    - 워커는 화면 출력 없음(메인만 출력)
    """
    BATCH = 5_000  # 전역 카운터 증가 배치 크기
    batch = 0
    attempt_local = 0
    try:
        with pyzipper.AESZipFile(str(zip_path)) as zf:
            member = _pick_smallest_member(zf)
            if not member:
                return

            i = start_idx
            while i < end_idx and not found_evt.is_set():
                pwd = _int_to_pwd(i)
                attempt_local += 1
                batch += 1

                if _try_password_pyzipper(zf, member, pwd):
                    # 남은 배치 반영
                    if batch:
                        with attempts_total.get_lock():
                            attempts_total.value += batch
                        batch = 0
                    # 결과 보고 및 종료
                    try:
                        found_queue.put_nowait(pwd)
                    except Exception:
                        pass
                    found_evt.set()
                    return

                # 전역 카운터 배치 반영
                if attempt_local % PROGRESS_INTERVAL == 0 or batch >= BATCH:
                    with attempts_total.get_lock():
                        attempts_total.value += batch
                    batch = 0

                i += 1

            # 루프 종료 시 남은 배치 반영
            if batch:
                with attempts_total.get_lock():
                    attempts_total.value += batch

    except KeyboardInterrupt:
        pass
    except Exception:
        # 워커 에러는 조용히 무시(안정성 우선)
        pass


# ==============================
# 병렬 브루트포스(범위 분할 + 전역 진행률 출력)
# ==============================
def _default_workers_for_machine() -> int:
    """M1(arm64/macOS)은 기본 4 워커 권장, 그 외에는 cpu_count()"""
    try:
        if platform.system() == 'Darwin' and platform.machine() == 'arm64':
            return 4
        return max(1, mp.cpu_count())
    except Exception:
        return 4


def unlock_zip_parallel_range(
    zip_path: Path = ZIP_PATH, workers: Optional[int] = None
) -> Optional[str]:
    # ZIP 사전 점검
    try:
        with pyzipper.AESZipFile(str(zip_path)) as zf:
            member = _pick_smallest_member(zf)
            if not member:
                print('[오류] ZIP 내부에 파일 항목이 없습니다.')
                return None
    except FileNotFoundError:
        print(f'[오류] ZIP 파일을 찾을 수 없습니다: {zip_path}')
        return None
    except Exception as e:
        print(f'[오류] ZIP 파일을 열 수 없습니다: {zip_path} -> {e}')
        return None

    if workers is None or workers <= 0:
        workers = _default_workers_for_machine()

    # 범위 계산
    ranges: list[Tuple[int, int]] = []
    for k in range(workers):
        s = (TOTAL_SPACE * k) // workers
        e = (TOTAL_SPACE * (k + 1)) // workers
        ranges.append((s, e))

    start_dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    t0 = time.perf_counter()

    print('#' * 60)
    print(f'[시작] ZIP: {zip_path.name}')
    print(f'[시작] 시작 시각: {start_dt}')
    print(f'[시작] 탐색 공간: {TOTAL_SPACE:,} (36^{PWD_LEN})')
    print(f'[시작] 프로세스 수: {workers}')
    print(f'[설정] PROGRESS_INTERVAL(횟수): {PROGRESS_INTERVAL:,}')
    print('#' * 60)

    found_evt = mp.Event()
    attempts_total = mp.Value('Q', 0)  # unsigned long long
    found_queue: mp.Queue = mp.Queue(maxsize=workers)

    procs: list[mp.Process] = []
    for s, e in ranges:
        p = mp.Process(
            target=_worker_range,
            args=(zip_path, s, e, found_evt, attempts_total, found_queue),
        )
        p.start()
        procs.append(p)

    found_password: Optional[str] = None
    last_global_print = 0.0

    try:
        while True:
            # 1) 워커가 보낸 암호 수신 시 즉시 처리
            try:
                found_password = found_queue.get_nowait()
                found_evt.set()
            except Exception:
                pass

            # 2) 전역 진행률 주기적 출력(한 줄 덮어쓰기)
            now = time.perf_counter()
            if now - last_global_print >= GLOBAL_PROGRESS_INTERVAL_SEC:
                with attempts_total.get_lock():
                    done = attempts_total.value
                pct = 100.0 * done / TOTAL_SPACE
                line = f'[총 진행] 시도 {done:,}/{TOTAL_SPACE:,} ({pct:6.3f}%) | 경과 {now - t0:8.2f}s'
                print('\r' + line, end='', flush=True)
                last_global_print = now

            # 3) 성공 시 마무리
            if found_password:
                print()  # 진행 줄 개행
                elapsed = time.perf_counter() - t0
                print('\n' + '=' * 60)
                print(f'[성공] 비밀번호: {found_password}')
                print(f'[성공] 총 경과: {elapsed:.2f}s')
                print('=' * 60)
                _safe_write_text(PASS_TXT, found_password)
                _safe_write_text(RESULT_TXT, found_password)
                break

            # 4) 모든 프로세스 종료 확인
            if not any(p.is_alive() for p in procs):
                break

            time.sleep(0.02)

    except KeyboardInterrupt:
        print('\n[중단] 사용자에 의해 취소. 프로세스 종료 중...')
        found_evt.set()
    finally:
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
        for p in procs:
            try:
                p.join()
            except Exception:
                pass

    if not found_password:
        print('\n[결과] 비밀번호를 찾지 못했습니다.')
    return found_password


# ==============================
# main
# ==============================
def main():
    unlock_zip_parallel_range(ZIP_PATH)


if __name__ == '__main__':
    try:
        mp.set_start_method('spawn', force=True)  # macOS/Windows 안정화
    except RuntimeError:
        pass
    mp.freeze_support()
    main()
