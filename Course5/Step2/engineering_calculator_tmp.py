import math
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QLineEdit, QPushButton, QWidget


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

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)  # type: ignore
        self.display.setStyleSheet('font-size: 30px; border: none; height: 50px;')
        grid.addWidget(self.display, 0, 0, 1, 10)

        buttons = [
            '(', ')', 'mc', 'm+', 'm-', 'mr', '<-', 'AC', '%', '÷',
            '2nd', 'x²', 'x³', 'xʸ', 'eˣ', '10ˣ', '7', '8', '9', '×',
            '1/x', '√x', '∛x', 'ln', 'ln', 'log₁₀', '4', '5', '6', '−',
            'x!', 'sin', 'cos', 'tan', 'e', 'EE', '1', '2', '3', '+',
            'Rand', 'sinh', 'cosh', 'tanh', 'π', 'Deg', '±', '0', '.', '=',
        ]  # fmt: skip

        positions = [(i, j) for i in range(1, 6) for j in range(10)]

        for position, button in zip(positions, buttons):
            if button == '':
                continue

            btn = QPushButton(button)
            row, col = position  # 위치 분해

            # 색상 조건 분기
            if col <= 5:  # 왼쪽 6열
                color = '#1c1d1f'
            elif row == 1 and col in (6, 7, 8):  # 첫 번째 행의 7~9열
                color = '#aaaaaa'
            elif col == 9:  # 마지막 열
                color = 'orange'
            else:  # 나머지
                color = '#2d2f34'

            btn.setStyleSheet(
                f'font-size: 20px; color: #fff; height: 50px; background-color: {color};'
            )

            btn.clicked.connect(self._button_clicked)

            grid.addWidget(btn, position[0], position[1])

    def _update_display(self, text: str):
        self.display.setText(text)

    def _button_clicked(self):
        button = self.sender()
        button_text = button.text()  # type: ignore

        match button_text:
            case num if num.isdigit():
                self._handle_number_input(num)
            case 'AC':
                self.reset()
            case '%':
                if self.waiting_operand:
                    self.waiting_operand.append('%')
                    self.display.setText(''.join(self.waiting_operand))
            case '=':
                self._equal()
            case '.':
                self._handle_float_input()
            case '±':
                self._negative_positive()
            case '+' | '−' | '×' | '÷':
                self._handle_operator_input(button_text)

    def _handle_number_input(self, number: str):
        self._set_text(float(number))
        self.waiting_operand.append(number)
        if self.waiting_operator is not None:
            self.operators.append(self.waiting_operator)
            self.waiting_operator = None

    def _handle_float_input(self):
        # 앞에 연산자 혹은 아무런 숫자 입력이 없다면 '0.' 추가
        # 숫자가 있으면 그냥 . 추가
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
        # self.waiting_operator = operator
        # self.display.setText(self.display.text() + operator)

    def _equal(self):
        if self.waiting_operand:
            token = ''.join(self.waiting_operand)
            # 퍼센트 토큰이면 먼저 해석
            if '%' in token:
                # 일단 토큰을 operands에 문자열로 넣어두고 _percent가 치환하도록
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
            # 다음 계산을 위해 결과만 남기기
            self.operands = [result]
            self.operators.clear()
        else:
            self.display.setText('정의되지 않음')
            self.reset(update_display=False)

    def _percent(self):
        # 우선 현재 입력 버퍼 기준으로 토큰 확보
        token = ''.join(self.waiting_operand) if self.waiting_operand else None

        # 직전에 _handle_operator_input 에서 이미 operands에 문자열로 넣은 경우 처리
        if token is None:
            if (
                self.operands
                and isinstance(self.operands[-1], str)
                and '%' in self.operands[-1]
            ):
                token = self.operands[-1]
            else:
                return  # 처리할 퍼센트 토큰 없음

        # ---------- 규칙 2: 'a%b' 모듈러 ----------
        if '%' in token and not token.endswith('%'):
            try:
                a_str, b_str = token.split('%', 1)
                a = float(a_str)
                b = float(b_str)
                modv = Calculator._modulo(a, b)
                if modv is None:
                    return
                # 마지막 항을 모듈러 결과로 교체
                if (
                    self.operands
                    and isinstance(self.operands[-1], str)
                    and self.operands[-1] == token
                ):
                    self.operands[-1] = modv
                else:
                    # 아직 operands에 안 들어갔다면 push
                    self.operands.append(modv)
                # 입력 버퍼/표시 정리
                self.waiting_operand.clear()
                self.display.setText('')
                return
            except Exception:
                return

        # ---------- 규칙 1: 'n%' 비율 ----------
        if token.endswith('%'):
            # 퍼센트 숫자 파싱
            try:
                n = float(token[:-1])  # '30%' -> 30.0
            except ValueError:
                return

            last_op = self.operators[-1]

            if self.operators and self.operators[-1] in ('+', '−'):
                # base = 마지막 연산자 '직전'까지의 결과
                base = self.calculator._calculate(
                    self.operators[:-1], self.operands[:-1]
                )
                if base is None:
                    return

                delta = base * (n / 100.0)
                tmp = base + delta if last_op == '+' else base - delta

                # 식 전체를 tmp 한 항으로 축약
                self.operands = [tmp]
                self.operators.clear()
                self.waiting_operand.clear()
                self.display.setText('')  # 다음 항 대기
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

    def reset(self, update_display: bool = True):
        self.operators.clear()
        self.operands.clear()
        self.waiting_operand.clear()
        self.waiting_operator = None
        if update_display:
            self.display.setText('0')

    def _set_text(self, number: float):
        print(type(number))
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
                if op in ('×', '÷'):
                    a, b = operands[i], operands[i + 1]

                    match op:
                        case '×':
                            result = Calculator._multiply(a, b)
                        case '÷':
                            result = Calculator._divide(a, b)

                    if result is None:
                        raise ZeroDivisionError

                    operands[i] = result

                    operators.pop(i)
                    operands.pop(i + 1)

                else:
                    i += 1

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

            final_result = operands[0]
            return final_result
        except ZeroDivisionError:
            return None
            # self.display.setText('정의되지 않음')
            # self.reset(update_display=False)
        except Exception as e:
            print(e)
            return None
            # self.display.setText('Error!')
            # self.reset(update_display=False)

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
        return Calculator._power(x, 1 / 3)

    @staticmethod
    def _yth_root(x: float, y: float):
        if y == 0:
            raise ZeroDivisionError
        return Calculator._power(x, 1 / y)

    @staticmethod
    def _ln(x: float):
        return math.log(x)

    @staticmethod
    def _log10(x: float):
        return math.log10(x)

    @staticmethod
    def _log(x: float, y: float):
        return math.log(x, y)

    @staticmethod
    def _factorial(x: float):
        return math.factorial(x)

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
