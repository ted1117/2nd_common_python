import math
import sys

# 전역변수 선언
MATERIAL: str = ''
DIAMETER: float = 0.0
THICKNESS: float = 0.0
AREA: float = 0.0
WEIGHT_ON_MARS: float = 0.0
GRAVITY_ON_MARS = 0.38

kor2eng = {'유리': 'glass', '알루미늄': 'aluminum', '탄소강': 'carbon_steel'}
eng2kor = {'glass': '유리', 'aluminum': '알루미늄', 'carbon_steel': '탄소강'}


def sphere_area(diameter: float, material: str, thickness: float = 1.0):
    global MATERIAL, DIAMETER, THICKNESS, AREA, WEIGHT_ON_MARS, GRAVITY_ON_MARS

    density_dict = {'glass': 2400, 'aluminum': 2700, 'carbon_steel': 7850}
    outer_radius = diameter / 2  # 단위: m
    thickness_in_m = thickness / 100  # 단위 m
    inner_radius = outer_radius - thickness_in_m

    density = density_dict.get(material, 0)

    area = 2 * math.pi * (outer_radius * outer_radius)
    outer_volume = (2 / 3) * math.pi * (outer_radius**3)
    inner_volume = (2 / 3) * math.pi * (inner_radius**3)
    volume = outer_volume - inner_volume
    mass = volume * density
    weight_on_mars = mass * GRAVITY_ON_MARS

    MATERIAL = eng2kor.get(material, '')
    DIAMETER = diameter
    THICKNESS = thickness
    AREA = area
    WEIGHT_ON_MARS = weight_on_mars


def _read_or_quit(prompt: str, is_material: bool = False) -> str:
    while True:
        s = input(prompt).strip()
        if s.lower() == 'q':
            print('프로그램을 종료합니다.')
            sys.exit(0)
        if is_material:
            try:
                return _check_material_ok(s)
            except ValueError as e:
                print(f'입력 오류: {e}')
                continue
        return s


def _check_material_ok(material_in: str) -> str:
    kor2eng = {'유리': 'glass', '알루미늄': 'aluminum', '탄소강': 'carbon_steel'}
    allowed = {'glass', 'aluminum', 'carbon_steel'}

    s = material_in.strip().lower()
    s = kor2eng.get(s, s)

    if s not in allowed:
        raise ValueError(
            '재질은 유리/glass, 알루미늄/aluminum, 탄소강/carbon_steel 중 하나여야 합니다.'
        )
    return s


def main():
    while True:
        try:
            diameter = float(_read_or_quit('지름을 입력하세요(단위: m): '))
            if diameter <= 0:
                raise ValueError('지름은 0보다 커야 합니다.')
            material = _read_or_quit('재질을 입력하세요: ', is_material=True)
            thickness_str = _read_or_quit('두께를 입력하세요(기본값: 1cm, 단위: cm): ')

            thickness = 1.0 if thickness_str == '' else float(thickness_str)

            if thickness <= 0:
                raise ValueError('두께는 0보다 커야 합니다.')
            if thickness >= (diameter / 2) * 100:
                raise ValueError('두께는 반지름보다 크거나 같을 수 없습니다.')

            sphere_area(diameter=diameter, material=material, thickness=thickness)

            print('########## 계산 결과 ##########')
            print(
                f'재질 ⇒ {MATERIAL}, '
                f'지름 ⇒ {DIAMETER}, '
                f'두께 ⇒ {THICKNESS}, '
                f'면적 ⇒ {AREA:.3f} ㎡, '
                f'무게 ⇒ {WEIGHT_ON_MARS:.3f} kg'
            )
        except ValueError as e:
            print(f'입력에 오류가 발생했습니다.\n오류 메시지: {e}')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
