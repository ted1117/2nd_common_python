import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QLineEdit, QPushButton, QWidget


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

        self.waiting_operand = []
        self.waiting_operator = None

        self.operands = []
        self.operators = []

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

    def _button_clicked(self):
        button = self.sender()
        button_text = button.text()  # type: ignore

        match button_text:
            case num if num.isdigit():
                self._handle_number_input(num)
                print(self.operands)
            case 'AC':
                self.reset()
            case '%':
                ...
            case '=':
                self._handle_equal_input()
            case '.':
                self._handle_float_input()
            case '±':
                ...
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
        if current_text[-1] == '.':
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

    def _negative_positive(self): ...

    def _percent(self):
        # 1. 아무런 입력이 없었을 땐, 그냥 퍼센티지 계산값만 보여주면 됨
        if not self.waiting_operator:
            operand = float(''.join(self.waiting_operand))
            result = operand / 100
            self.display.setText(str(result))
            return result
        # 2. 앞에 연산식이 있으면 해당 결과값에 퍼센티지 계산
        else:
            operand = float(''.join(self.waiting_operand))
            ...

        # ex) 200 + 30% + 100 + 30% = 468
        # 3. 모듈러 연산

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
                if op in ('×', '÷'):
                    a, b = self.operands[i], self.operands[i + 1]

                    if op == '×':
                        result = Calculator._multiply(a, b)
                    else:
                        result = Calculator._divide(a, b)

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
                b = self.operands.pop(0)
                result = (
                    Calculator._add(a, b) if op == '+' else Calculator._subtract(a, b)
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
    def _format_number(number: float) -> str:
        return str(number).rstrip('0').rstrip('.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
