import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QLineEdit, QPushButton, QWidget


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

        self.waiting_operand: list = []
        self.waiting_operator = None

        self.operands: list = []
        self.operators: list = []

        self.current_expression: str = ''
        self.stacked_expression: list = []

        self.reset()

    def _init_ui(self):
        self.setWindowTitle('계산기')
        self.setGeometry(300, 300, 300, 400)

        grid = QGridLayout()
        self.setLayout(grid)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)  # type: ignore
        self.display.setStyleSheet('font-size: 30px; border: none;')
        grid.addWidget(self.display, 0, 0, 1, 4)

        buttons = [
            '<-', 'AC', '%', '÷',
            '7', '8', '9', '×',
            '4', '5', '6', '−',
            '1', '2', '3', '+',
            '±', '0', '.', '=',
        ]  # fmt: skip

        positions = [(i, j) for i in range(1, 6) for j in range(4)]

        for position, button in zip(positions, buttons):
            if button == '':
                continue

            btn = QPushButton(button)
            btn.setStyleSheet('font-size: 20px; height: 50px;')
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
                self.waiting_operator = '%'
            case '=':
                self._handle_equal_input()
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
            operand = float(''.join(self.waiting_operand))
            self.operands.append(operand)
        self.waiting_operand.clear()
        self.waiting_operator = operator
        self.display.setText(self.display.text() + operator)

    def _handle_equal_input(self):
        if self.waiting_operand:
            self.operands.append(float(''.join(self.waiting_operand)))
            self.waiting_operand.clear()
        result = self._calculate()

        if result is not None:
            self.display.setText(Calculator._format_number(result))

    def _negative_positive(self):
        current_text = self.display.text()

        # 오류 상태면 무시
        if current_text in ['정의되지 않음', 'Error!']:
            return

        # 마지막 연산자 인덱스 탐색 유틸 (로컬 함수)
        def _last_op_index(s: str) -> int:
            # 여러 연산자 중 가장 뒤에 있는 위치
            idxs = [s.rfind(op) for op in ['+', '−', '×', '÷']]
            return max(idxs)

        # 화면에 보여줄 표기 생성 (음수면 괄호)
        def _display_number(val: float) -> str:
            s = self._format_number(val)
            return f'({s})' if val < 0 else s

        # 내부 버퍼용 표기(괄호 없음, 불필요한 0 제거, 부호는 -만)
        def _canon_number(val: float) -> str:
            return self._format_number(val)  # 음수면 '-'가 포함된 문자열

        # 1) 현재 숫자 입력 중: waiting_operand 를 기반으로 토글
        if self.waiting_operand:
            number_str = ''.join(self.waiting_operand)
            try:
                cur = float(number_str)
            except ValueError:
                return

            if cur == 0:
                return  # 0은 ± 눌러도 변화 없음(아이폰 계산기 동작과 유사)

            new_val = -cur
            # 디스플레이에서 마지막 항만 교체 (표현 비교 X, 위치 교체 O)
            last_idx = _last_op_index(current_text)
            prefix = current_text[: last_idx + 1] if last_idx >= 0 else ''
            new_display = prefix + _display_number(new_val)
            self._update_display(new_display)

            # 내부 버퍼는 괄호 없이 정규화된 문자열로
            self.waiting_operand = list(_canon_number(new_val))
            return

        # 2) 숫자 입력이 끝난 상태: 디스플레이의 마지막 항을 토글
        display_text = current_text
        last_idx = _last_op_index(display_text)
        prefix = display_text[: last_idx + 1] if last_idx >= 0 else ''
        last_token = display_text[last_idx + 1 :].strip()

        # 괄호가 있을 수 있으므로 제거 후 파싱 시도
        try:
            val = float(last_token.strip('()'))
        except ValueError:
            # 전체가 숫자 하나일 수 있으니 한 번 더 시도
            try:
                val = float(display_text.strip('()'))
                prefix = ''  # 전체가 숫자였던 경우
            except ValueError:
                return

        if val == 0:
            return

        new_val = -val
        new_display = prefix + _display_number(new_val)
        self._update_display(new_display)

        # operands 동기화: 마지막 항을 실제 값으로 교체
        if self.operands:
            self.operands[-1] = new_val
        else:
            # 아직 operands가 비어있다면 현재 표시 값을 반영
            self.operands.append(new_val)

    def _percent(self):
        self.waiting_operator = '%'
        # 1. 모듈러 연산

        # 2. 퍼센티지 연산

        ...

    def reset(self, update_display: bool = True):
        self.operators.clear()
        self.operands.clear()
        self.waiting_operand.clear()
        self.waiting_operator = None
        if update_display:
            self.display.setText('0')

    def _calculate(self) -> float | None:
        try:
            if not self.operands:
                return
            i = 0
            while i < len(self.operators):
                op = self.operators[i]
                if op in ('×', '÷', '%'):
                    a, b = self.operands[i], self.operands[i + 1]

                    match op:
                        case '×':
                            result = Calculator._multiply(a, b)
                        case '÷':
                            result = Calculator._divide(a, b)
                        case '%':
                            result = Calculator._modulo(a, b)

                    if result is None:
                        raise ZeroDivisionError

                    self.operands[i] = result

                    self.operators.pop(i)
                    self.operands.pop(i + 1)

                else:
                    i += 1

            while self.operators:
                op = self.operators.pop(0)
                a = self.operands.pop(0)
                if not self.operands:
                    result = a
                else:
                    b = self.operands.pop(0)
                    result = (
                        Calculator._add(a, b)
                        if op == '+'
                        else Calculator._subtract(a, b)
                    )
                self.operands.insert(0, result)

            final_result = self.operands[0]
            return final_result

        except ZeroDivisionError:
            self.display.setText('정의되지 않음')
            self.reset(update_display=False)
        except Exception as e:
            print(e)
            self.display.setText('Error!')
            self.reset(update_display=False)

    def _set_text(self, number: float):
        print(type(number))
        if number == int(number):
            number = int(number)
        text = self.display.text()
        if text == '0':
            self.display.setText(str(number))
        else:
            self.display.setText(self.display.text() + str(number))

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
    def _format_number(number: float) -> str:
        return str(number).rstrip('0').rstrip('.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
