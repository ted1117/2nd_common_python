import math
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

        self.calculator = Calculator()

        self.waiting_operand: list = []
        self.waiting_operator = None

        self.operands: list = []
        self.operators: list = []

        self.current_expression: str = ''
        self.stacked_expression: list = []

    def _init_ui(self):
        self.setWindowTitle('계산기')
        self.setGeometry(300, 300, 300, 400)

        grid = QGridLayout()
        self.setLayout(grid)

        # 상단: 왼쪽 모드 라벨 + 오른쪽 디스플레이
        top_layout = QHBoxLayout()
        self.mode_label = QLabel('DEG')
        self.mode_label.setStyleSheet('font-size: 14px; color: #aaa;')
        self.mode_label.setFixedWidth(40)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)  # type: ignore
        self.display.setStyleSheet('font-size: 30px; border: none; height: 50px;')

        top_layout.addWidget(self.mode_label)
        top_layout.addWidget(self.display)
        grid.addLayout(top_layout, 0, 0, 1, 10)

        buttons = [
            '(', ')', 'mc', 'm+', 'm-', 'mr', '<-', 'AC', '%', '÷',
            '2nd', 'x²', 'x³', 'xʸ', 'eˣ', '10ˣ', '7', '8', '9', '×',
            '1/x', '√x', '∛x', 'ʸ√', 'ln', 'log₁₀', '4', '5', '6', '−',
            'x!', 'sin', 'cos', 'tan', 'e', 'EE', '1', '2', '3', '+',
            'Rand', 'sinh', 'cosh', 'tanh', 'π', 'Deg', '±', '0', '.', '=',
        ]  # fmt: skip

        positions = [(i, j) for i in range(1, 6) for j in range(10)]

        for position, button in zip(positions, buttons):
            if button == '':
                continue

            btn = QPushButton(button)
            row, col = position

            # 색상 스킴
            if col <= 5:
                color = '#1c1d1f'
            elif row == 1 and col in (6, 7, 8):
                color = '#666666'
            elif col == 9:
                color = '#cc8400'
            else:
                color = '#1e2024'

            btn.setStyleSheet(
                f'font-size: 20px; color: #fff; height: 50px; background-color: {color};'
            )
            btn.clicked.connect(self._button_clicked)
            grid.addWidget(btn, position[0], position[1])

    def _update_display(self, text: str):
        self.display.setText(text)

    # ---------- 공통 유틸 ----------
    def _parse_buffer(self) -> float | None:
        """waiting_operand를 float로 파싱. '30%' → 0.3, '1e3' 허용."""
        if not self.waiting_operand:
            return None
        token = ''.join(self.waiting_operand)
        try:
            if token.endswith('%'):
                return float(token[:-1]) / 100.0
            return float(token)
        except ValueError:
            return None

    def _apply_unary(self, label: str, func, *, trig_mode: bool = False):
        """단항 연산: 화면에는 label(x) 표시, 내부에는 결과 숫자를 waiting_operand로 보관."""
        try:
            take_from_operands = False
            if self.waiting_operand:
                x = self._parse_buffer()
                if x is None:
                    return
            elif self.operands:
                x = float(self.operands.pop())
                take_from_operands = True
            else:
                return

            shown_x = Calculator._format_number(x)
            self.display.setText(f'{label}({shown_x})')

            y = func(x, self.calculator.angle_mode) if trig_mode else func(x)
            s = Calculator._format_number(y)

            self.waiting_operand = list(s)
            if take_from_operands:
                pass
        except Exception:
            self.display.setText('정의되지 않음')
            self.reset(update_display=False)

    def _insert_constant(self, value: float):
        s = Calculator._format_number(value)
        if self.waiting_operand:
            self.waiting_operand += list(s)
        else:
            self.waiting_operand = list(s)
        self.display.setText(''.join(self.waiting_operand))

    def _handle_EE(self):
        if not self.waiting_operand:
            return
        token = ''.join(self.waiting_operand)
        if token.endswith('%') or 'e' in token or 'E' in token:
            return
        self.waiting_operand.append('e')
        self.display.setText(''.join(self.waiting_operand))

    # ---------- 버튼 처리 ----------
    def _button_clicked(self):
        button = self.sender()
        button_text = button.text()  # type: ignore

        match button_text:
            # 숫자/기본
            case num if num.isdigit():
                self._handle_number_input(num)
            case '.':
                self._handle_float_input()
            case '±':
                self._negative_positive()
            case '<-':
                if self.waiting_operand:
                    self.waiting_operand.pop()
                    self.display.setText(''.join(self.waiting_operand) or '0')
            case 'AC':
                self.reset()

            # 퍼센트 토글(해석은 연산 직전)
            case '%':
                if self.waiting_operand:
                    if self.waiting_operand[-1] == '%':
                        self.waiting_operand.pop()
                    else:
                        self.waiting_operand.append('%')
                    self.display.setText(''.join(self.waiting_operand))

            # 계산/사칙
            case '=':
                self._equal()
            case '+' | '−' | '×' | '÷':
                self._handle_operator_input(button_text)

            # 단항: 화면 표기 + 내부 숫자 보관
            case 'x²':
                self._apply_unary('x²', Calculator._square)
            case 'x³':
                self._apply_unary('x³', Calculator._cube)
            case '1/x':
                self._apply_unary('1/x', Calculator._reciprocal)
            case '√x':
                self._apply_unary('√', Calculator._sqrt)
            case '∛x':
                self._apply_unary('∛', Calculator._cuberoot)
            case 'eˣ':
                self._apply_unary('eˣ', Calculator._exp)
            case '10ˣ':
                self._apply_unary('10ˣ', Calculator._pow10)
            case 'ln':
                self._apply_unary('ln', Calculator._ln)
            case 'log₁₀':
                self._apply_unary('log₁₀', Calculator._log10)

            # 삼각(각도 모드 반영)
            case 'sin':
                self._apply_unary('sin', Calculator._sin, trig_mode=True)
            case 'cos':
                self._apply_unary('cos', Calculator._cos, trig_mode=True)
            case 'tan':
                self._apply_unary('tan', Calculator._tan, trig_mode=True)

            # 하이퍼볼릭
            case 'sinh':
                self._apply_unary('sinh', Calculator._sinh)
            case 'cosh':
                self._apply_unary('cosh', Calculator._cosh)
            case 'tanh':
                self._apply_unary('tanh', Calculator._tanh)

            # 상수/EE/각도 모드
            case 'π':
                self._insert_constant(math.pi)
            case 'e':
                self._insert_constant(math.e)
            case 'Rand':
                import random

                self._insert_constant(random.random())
            case 'EE':
                self._handle_EE()
            case 'Deg':
                self._toggle_angle_mode()

            # 이항 특수: xʸ, ʸ√ (2단계 입력)
            case 'xʸ':
                # x 확정 → 연산자 'xʸ' 표기 → y 입력 대기
                if self.waiting_operand:
                    tok = ''.join(self.waiting_operand)
                    try:
                        x = float(tok[:-1]) / 100.0 if tok.endswith('%') else float(tok)
                    except ValueError:
                        return
                    self.operands.append(x)
                    self.waiting_operand.clear()
                    self.operators.append('xʸ')
                    self.display.setText('')
                elif self.operands:
                    self.operators.append('xʸ')
                    self.display.setText('')
            case 'ʸ√':
                # x 확정 → 연산자 'ʸ√' 표기 → y 입력 대기
                if self.waiting_operand:
                    tok = ''.join(self.waiting_operand)
                    try:
                        x = float(tok[:-1]) / 100.0 if tok.endswith('%') else float(tok)
                    except ValueError:
                        return
                    self.operands.append(x)
                    self.waiting_operand.clear()
                    self.operators.append('ʸ√')
                    self.display.setText('')
                elif self.operands:
                    self.operators.append('ʸ√')
                    self.display.setText('')

            # 미구현(보류)
            case '2nd' | '(' | ')' | 'mc' | 'm+' | 'm-' | 'mr':
                pass

    # ---------- 기존 숫자/연산 흐름 ----------
    def _handle_number_input(self, number: str):
        self._set_text(float(number))
        self.waiting_operand.append(number)
        if self.waiting_operator is not None:
            self.operators.append(self.waiting_operator)
            self.waiting_operator = None

    def _handle_float_input(self):
        current_text = self.display.text()
        if '.' in current_text:
            return
        if self.waiting_operand:
            self.display.setText(current_text + '.')
        else:
            self.display.setText(current_text + '0.')
        self.waiting_operand.append('.')

    def _handle_operator_input(self, operator: str):
        if self.waiting_operand:
            if '%' in self.waiting_operand:
                operand = ''.join(self.waiting_operand)
                self.operands.append(operand)
                self._percent()
            else:
                operand = float(''.join(self.waiting_operand))
                self.operands.append(operand)
        self.waiting_operand.clear()
        self.operators.append(operator)
        self.display.setText('')

    def _equal(self):
        if self.waiting_operand:
            token = ''.join(self.waiting_operand)
            if '%' in token:
                self.operands.append(token)
                self._percent()
            else:
                self.operands.append(float(token))
            self.waiting_operand.clear()

        if len(self.operators) == len(self.operands):
            self.operators.pop()

        result = self.calculator._calculate(self.operators[:], self.operands[:])

        if result is not None:
            self.display.setText(Calculator._format_number(result))
            self.operands = [result]
            self.operators.clear()
        else:
            self.display.setText('정의되지 않음')
            self.reset(update_display=False)

    def _percent(self):
        token = ''.join(self.waiting_operand) if self.waiting_operand else None
        if token is None:
            if (
                self.operands
                and isinstance(self.operands[-1], str)
                and '%' in self.operands[-1]
            ):
                token = self.operands[-1]
            else:
                return

        # 'a%b' → 모듈러
        if '%' in token and not token.endswith('%'):
            try:
                a_str, b_str = token.split('%', 1)
                a = float(a_str)
                b = float(b_str)
                modv = Calculator._modulo(a, b)
                if modv is None:
                    return
                if (
                    self.operands
                    and isinstance(self.operands[-1], str)
                    and self.operands[-1] == token
                ):
                    self.operands[-1] = modv
                else:
                    self.operands.append(modv)
                self.waiting_operand.clear()
                self.display.setText('')
                return
            except Exception:
                return

        # 'n%' → 초항/+/− 비율 처리
        if token.endswith('%'):
            try:
                n = float(token[:-1])
            except ValueError:
                return

            last_op = self.operators[-1] if self.operators else None

            if self.operators and last_op in ('+', '−'):
                base = self.calculator._calculate(
                    self.operators[:-1], self.operands[:-1]
                )
                if base is None:
                    return
                delta = base * (n / 100.0)
                tmp = base + delta if last_op == '+' else base - delta
                self.operands = [tmp]
                self.operators.clear()
                self.waiting_operand.clear()
                self.display.setText('')
                return
            else:
                frac = n / 100.0
                if (
                    self.operands
                    and isinstance(self.operands[-1], str)
                    and self.operands[-1] == token
                ):
                    self.operands[-1] = frac
                else:
                    self.operands.append(frac)
                self.waiting_operand.clear()
                self.display.setText('')
                return

    def _negative_positive(self):
        current_text = self.display.text()
        if self.waiting_operand:
            if self.waiting_operand[0] == '-':
                self.waiting_operand.pop(0)
                new_text = current_text[1:]
            else:
                self.waiting_operand.insert(0, '-')
                new_text = '-' + current_text
            self.display.setText(new_text)

    def _toggle_angle_mode(self):
        self.calculator.angle_mode = (
            'DEG' if self.calculator.angle_mode == 'RAD' else 'RAD'
        )
        self.mode_label.setText(self.calculator.angle_mode)

    def reset(self, update_display: bool = True):
        self.operators.clear()
        self.operands.clear()
        self.waiting_operand.clear()
        self.waiting_operator = None
        if update_display:
            self.display.setText('0')

    def _set_text(self, number: float):
        if number == int(number):
            number = int(number)
        text = self.display.text()
        if text == '0':
            self.display.setText(str(number))
        else:
            self.display.setText(self.display.text() + str(number))


class Calculator:
    def __init__(self):
        super().__init__()

        self.waiting_operand: list = []
        self.waiting_operator = None

        self.operands: list = []
        self.operators: list = []

        self.current_expression: str = ''
        self.stacked_expression: list = []

        self.angle_mode = 'DEG'

    def _calculate(self, operators: list, operands: list):
        try:
            if not operands:
                return
            i = 0
            while i < len(operators):
                op = operators[i]
                if op in ('×', '÷', 'xʸ', 'ʸ√'):
                    a, b = operands[i], operands[i + 1]
                    match op:
                        case '×':
                            result = Calculator._multiply(a, b)
                        case '÷':
                            result = Calculator._divide(a, b)
                        case 'xʸ':
                            result = Calculator._power(a, b)  # a ** b
                        case 'ʸ√':
                            result = Calculator._yth_root(a, b)  # a ** (1/b)

                    if result is None:
                        raise ZeroDivisionError

                    operands[i] = result
                    operators.pop(i)
                    operands.pop(i + 1)
                else:
                    i += 1

            # 남은 +, − 처리
            while operators:
                op = operators.pop(0)
                a = operands.pop(0)
                if not operands:
                    result = a
                else:
                    b = operands.pop(0)
                    result = (
                        Calculator._add(a, b)
                        if op == '+'
                        else Calculator._subtract(a, b)
                    )
                operands.insert(0, result)

            return operands[0]

        except ZeroDivisionError:
            return None
        except Exception as e:
            print(e)
            return None

    # ---------- 기본 연산 ----------
    @staticmethod
    def _add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def _subtract(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def _multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def _divide(a: float, b: float) -> float | None:
        if b == 0:
            raise ZeroDivisionError
        return a / b

    @staticmethod
    def _modulo(a: float, b: float) -> float | None:
        if b == 0:
            raise ZeroDivisionError
        return a % b

    # ---------- 거듭제곱/루트 ----------
    @staticmethod
    def _power(x: float, y: float = 2) -> float:
        return x**y

    @staticmethod
    def _square(x: float):
        return Calculator._power(x, 2)

    @staticmethod
    def _cube(x: float):
        return Calculator._power(x, 3)

    @staticmethod
    def _exp(x: float):
        return Calculator._power(math.e, x)

    @staticmethod
    def _pow10(x: float):
        return Calculator._power(10, x)

    @staticmethod
    def _reciprocal(x: float):
        if x == 0:
            raise ZeroDivisionError
        return Calculator._power(x, -1)

    @staticmethod
    def _sqrt(x: float):
        return math.sqrt(x)

    @staticmethod
    def _cuberoot(x: float):
        return math.copysign(abs(x) ** (1 / 3), x)

    @staticmethod
    def _yth_root(x: float, y: float):
        if y == 0:
            raise ZeroDivisionError
        return Calculator._power(x, 1 / y)

    # ---------- 로그 ----------
    @staticmethod
    def _ln(x: float):
        return math.log(x)

    @staticmethod
    def _log10(x: float):
        return math.log10(x)

    @staticmethod
    def _log(x: float, y: float):
        return math.log(x, y)

    # ---------- 팩토리얼 ----------
    @staticmethod
    def _factorial(x: float):
        if x <= 0:
            raise ValueError
        return math.factorial(int(x))

    # ---------- 삼각/하이퍼볼릭 ----------
    @staticmethod
    def _sin(x: float, mode: str = 'RAD') -> float:
        if mode == 'DEG':
            x = math.radians(x)
        return math.sin(x)

    @staticmethod
    def _cos(x: float, mode: str = 'RAD') -> float:
        if mode == 'DEG':
            x = math.radians(x)
        return math.cos(x)

    @staticmethod
    def _tan(x: float, mode: str = 'RAD') -> float:
        if mode == 'DEG':
            x = math.radians(x)
        return math.tan(x)

    @staticmethod
    def _sinh(x: float) -> float:
        return math.sinh(x)

    @staticmethod
    def _cosh(x: float) -> float:
        return math.cosh(x)

    @staticmethod
    def _tanh(x: float) -> float:
        return math.tanh(x)

    # ---------- 출력 포맷 ----------
    @staticmethod
    def _format_number(number: float) -> str:
        if number == int(number):
            return str(int(number))
        s = f'{number:.6f}'
        return s.rstrip('0').rstrip('.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = CalculatorUI()
    calc.show()
    sys.exit(app.exec_())
