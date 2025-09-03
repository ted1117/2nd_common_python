import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QLineEdit, QPushButton, QWidget


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.waiting_operand = []
        self.waiting_operator = None

        self.operands = []
        self.operators = []

        self.reset()

    def initUI(self):
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
            btn.clicked.connect(self.button_clicked)

            grid.addWidget(btn, position[0], position[1])

    @staticmethod
    def format_number(number: float) -> str:
        return str(number).rstrip('0').rstrip('.')

    def set_text(self, number: float):
        print(type(number))
        if number == int(number):
            number = int(number)
        text = self.display.text()
        if text == '0':
            self.display.setText(str(number))
        else:
            self.display.setText(self.display.text() + str(number))

    def button_clicked(self):
        button = self.sender()
        button_text = button.text()  # type: ignore

        match button_text:
            case num if num.isdigit():
                self.set_text(num)
                self.waiting_operand.append(num)
                if self.waiting_operator is not None:
                    self.operators.append(self.waiting_operator)
                    self.waiting_operator = None
                print(self.operands)
            case 'AC':
                self.reset()
            case '%':
                ...
            case '=':
                if self.waiting_operand:
                    self.operands.append(float(''.join(self.waiting_operand)))
                    self.waiting_operand.clear()
                self.equal()
            case '.':
                ...
            case '±':
                ...
            case '+' | '−' | '×' | '÷':
                if self.waiting_operand:
                    operand = float(''.join(self.waiting_operand))
                    self.operands.append(operand)
                self.waiting_operand.clear()
                self.waiting_operator = button_text
                self.display.setText(self.display.text() + button_text)

    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float | None:
        if b == 0:
            raise ZeroDivisionError
        return a / b

    def reset(self):
        self.operators.clear()
        self.operands.clear()
        self.waiting_operand.clear()
        self.waiting_operator = None
        self.display.setText('0')

    def negative_positive(self): ...
    def percent(self, number: float):
        result = number / 100
        self.display.setText(str(result))

    def equal(self):
        try:
            if not self.operands:
                return
            i = 0
            while i < len(self.operators):
                op = self.operators[i]
                if op in ('×', '÷'):
                    a, b = self.operands[i], self.operands[i + 1]

                    if op == '×':
                        result = Calculator.multiply(a, b)
                    else:
                        result = Calculator.divide(a, b)

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
                    Calculator.add(a, b) if op == '+' else Calculator.subtract(a, b)
                )
                self.operands.insert(0, result)

            final_result = self.operands[0]
            self.display.setText(self.format_number(final_result))
        except Exception as e:
            print(e)
            self.display.setText('Error!')

    def calculate(self): ...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
