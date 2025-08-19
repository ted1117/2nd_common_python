import json
import platform
import random
import time

import humanize
import psutil


class DummySensor:
    def __init__(self) -> None:
        self._env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0,
        }

    def set_env(self):
        self._env_values['mars_base_internal_temperature'] = random.uniform(18, 30)
        self._env_values['mars_base_external_temperature'] = random.uniform(0, 21)
        self._env_values['mars_base_internal_humidity'] = random.uniform(50, 60)
        self._env_values['mars_base_external_illuminance'] = random.uniform(500, 715)
        self._env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self._env_values['mars_base_internal_oxygen'] = random.uniform(4, 7)

    def get_env(self) -> dict:
        self.set_env()
        return self._env_values


class MissionComputer:
    def __init__(
        self,
        sensor_data,
        name: str = 'Computer',
    ) -> None:
        self.name = name

        self._env_values = {}

        self._system_info = self._collect_system_info()

        self.sensor = sensor_data

    def get_sensor_data(self):
        try:
            while True:
                self._env_values = self.sensor.get_env()

                json_data = json.dumps(self._env_values, indent=4)

                print('\n' + '#' * 10, f'[{self.name}] 센서 데이터', '#' * 10)
                print(json_data)

                time.sleep(5)
        except KeyboardInterrupt:
            print(f'\n[{self.name}] Keyboard Interrupt detected.')
        except Exception as e:
            print(f'오류 발생: {e}')

    def _collect_system_info(self) -> dict:
        self._system_info = {
            'os': platform.system(),
            'os_version': platform.mac_ver()[0],
            'cpu_type': platform.machine(),
            'cpu_core': psutil.cpu_count(),  # 물리 코어
            'memory_size': humanize.naturalsize(
                psutil.virtual_memory().total, binary=True
            ),
        }

        return self._system_info

    def get_mission_computer_info_old(self):
        try:
            info_json = json.dumps(self._system_info, indent=4)

            print('\n' + '#' * 10, f'[{self.name}] 컴퓨터 정보', '#' * 10)
            print(info_json)

        except KeyboardInterrupt:
            print(f'\n[{self.name}] Keyboard Interrupt detected.')

    def get_mission_computer_load_old(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = humanize.naturalsize(
                psutil.Process().memory_info().rss, binary=True
            )

            computer_load = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
            }

            load_json = json.dumps(computer_load, indent=4)

            print('\n' + '#' * 10, f'[{self.name}] 실시간 CPU/메모리 사용률', '#' * 10)
            print(load_json)

        except KeyboardInterrupt:
            print(f'\n[{self.name}] Keyboard Interrupt detected.')

    def get_mission_computer_info(self):
        try:
            while True:
                info_json = json.dumps(self._system_info, indent=4)

                print('\n' + '#' * 10, f'[{self.name}] 컴퓨터 정보', '#' * 10)
                print(info_json)

                # time.sleep(20)
                time.sleep(10)
        except KeyboardInterrupt:
            print(f'\n[{self.name}] Keyboard Interrupt detected.')

    def get_mission_computer_load(self):
        try:
            while True:
                cpu_usage = psutil.cpu_percent(interval=0.1)
                memory_usage = humanize.naturalsize(
                    psutil.Process().memory_info().rss, binary=True
                )

                computer_load = {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                }

                load_json = json.dumps(computer_load, indent=4)

                print(
                    '\n' + '#' * 10, f'[{self.name}] 실시간 CPU/메모리 사용률', '#' * 10
                )
                print(load_json)

                # time.sleep(20)
                time.sleep(10)
        except KeyboardInterrupt:
            print(f'\n[{self.name}] Keyboard Interrupt detected.')


if __name__ == '__main__':
    ###############################################################
    ########################### 공통 ###############################
    ds = DummySensor()

    ###############################################################
    ########################## 문제 1 ##############################
    # ds.set_env()
    # print(ds.get_env())

    ###############################################################
    ########################## 문제 2 ##############################
    # RunComputer = MissionComputer(sensor_data=ds, name='문제 2')
    # RunComputer.get_sensor_data()

    ###############################################################
    ########################## 문제 3 ##############################
    # runComputer = MissionComputer(sensor_data=ds, name='문제 3')
    # runComputer.get_mission_computer_info_old()
    # runComputer.get_mission_computer_load_old()

    ###############################################################
    ########################## 문제 4 ##############################
    # import threading

    # runComputer = MissionComputer(sensor_data=ds, name='문제 4')
    # tasks = [
    #     runComputer.get_sensor_data,
    #     runComputer.get_mission_computer_info,
    #     runComputer.get_mission_computer_load,
    # ]

    # threads = []

    # for task in tasks:
    #     thread = threading.Thread(target=task)
    #     # thread.daemon = True
    #     thread.start()
    #     threads.append(thread)

    # try:
    #     for thread in threads:
    #         thread.join()
    # except KeyboardInterrupt:
    #     print('\nKeyboard Interrupt detected.')

    ###############################################################
    ########################## 문제 4 ##############################
    import multiprocessing

    runComputer1 = MissionComputer(sensor_data=ds, name='Computer01')
    runComputer2 = MissionComputer(sensor_data=ds, name='Computer02')
    runComputer3 = MissionComputer(sensor_data=ds, name='Computer03')

    tasks = [
        runComputer1.get_sensor_data,
        runComputer2.get_mission_computer_info,
        runComputer3.get_mission_computer_load,
    ]

    processes = []

    for task in tasks:
        process = multiprocessing.Process(target=task)
        process.start()
        processes.append(process)

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print('Keyboard Interrupt detected.')
