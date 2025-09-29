import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QLineEdit, QPushButton, QWidget


class Calculator:
    def __init__(self):
        self.current_input = ''
        self.expression = []
        self.result = '0'
        self.reset()

    def reset(self):
        self.current_input = ''
        self.expression = []
        self.result = '0'

    def get_display_text(self) -> str:
        """디스플레이에 텍스트 표시"""
        if (
            self.result in ['정의되지 않음', 'Error!']
            and not self.expression
            and not self.current_input
        ):
            return self.result

        base_expression = self._format_expression()

        # 현재 입력 중인 항은 그대로 표시
        if self.current_input:
            return base_expression + self.current_input

        # 입력 중이 아닐 때만 표현식이나 결과 표시
        if self.expression:
            return base_expression

        return self._format_number(float(self.result))

    def process_button(self, button_text: str):
        if self.result in ['정의되지 않음', 'Error!'] and button_text != 'AC':
            return

        match button_text:
            case num if num.isdigit():
                self.current_input += button_text
            case '.':
                self._handle_float_input()
            case 'AC':
                self.reset()
            case '±':
                self._negative_positive()
            case '+' | '−' | '×' | '÷':
                self._handle_operator_input(button_text)
            case '%':
                self._handle_percent_input()
            case '=':
                self._handle_equal_input()

    def _handle_float_input(self):
        if '.' not in self.current_input:
            self.current_input = self.current_input or '0'
            self.current_input += '.'

    def _negative_positive(self):
        if self.current_input:
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            elif self.current_input.startswith('('):
                self.current_input = self.current_input[2:-1]
            else:
                if isinstance(self.expression[-1], str):
                    self.current_input = f'(-{self.current_input})'
                else:
                    self.current_input = '-' + self.current_input

    def _handle_operator_input(self, operator: str):
        if self.current_input:
            try:
                self.expression.append(float(self.current_input))
                self.current_input = ''
            except ValueError:
                return  # '-'만 입력된 상태에서 연산자 누르면 무시

        if not self.expression:
            self.expression.append(float(self.result))

        if self.expression and isinstance(self.expression[-1], str):
            self.expression[-1] = operator
        else:
            self.expression.append(operator)

    def _handle_percent_input(self):
        if self.current_input:
            try:
                self.expression.append(float(self.current_input))
                self.expression.append('%')
                self.current_input = ''
            except ValueError:
                return

    def _handle_equal_input(self):
        if self.current_input:
            try:
                if self.current_input.startswith('(') and self.current_input.endswith(
                    ')'
                ):
                    self.current_input = self.current_input[1:-1]
                self.expression.append(float(self.current_input))
                self.current_input = ''
            except ValueError:
                # = 을 눌렀는데 current_input이 '-' 같은 상태면 무시
                self.current_input = ''
                return

        if not self.expression:
            return

        try:
            if isinstance(self.expression[-1], str) and self.expression[-1] != '%':
                self.expression.pop()

            final_result = self._calculate(self.expression)
            self.result = str(final_result)
            self.expression = []
        except (ZeroDivisionError, ValueError):
            self.result = '정의되지 않음'
            self.expression = []
            self.current_input = ''
        except Exception:
            self.result = 'Error!'
            self.expression = []
            self.current_input = ''

    def _calculate(self, expression: list) -> float:
        temp_expr = list(expression)

        i = 0
        while i < len(temp_expr):
            if temp_expr[i] == '%':
                percent_number = temp_expr[i - 1]

                if i > 1 and temp_expr[i - 2] in ('+', '−'):
                    sub_calc_expr = temp_expr[: i - 2]
                    base_value = self._calculate_simple(sub_calc_expr)
                    calculated_percent = base_value * (percent_number / 100.0)
                    temp_expr = (
                        temp_expr[: i - 1] + [calculated_percent] + temp_expr[i + 1 :]
                    )
                else:
                    calculated_percent = percent_number / 100.0
                    temp_expr = (
                        temp_expr[: i - 1] + [calculated_percent] + temp_expr[i + 1 :]
                    )

                i = 0
                continue
            i += 1

        return self._calculate_simple(temp_expr)

    def _calculate_simple(self, expression: list) -> float:
        if not expression:
            return 0
        if len(expression) == 1 and isinstance(expression[0], (int, float)):
            return expression[0]

        temp_expr = list(expression)
        i = 0
        while i < len(temp_expr):
            op = temp_expr[i]
            if op in ('×', '÷'):
                a, b = temp_expr[i - 1], temp_expr[i + 1]
                result = self._multiply(a, b) if op == '×' else self._divide(a, b)
                temp_expr = temp_expr[: i - 1] + [result] + temp_expr[i + 2 :]
                i = 0
                continue
            i += 1

        result = temp_expr[0]
        for i in range(1, len(temp_expr), 2):
            op, b = temp_expr[i], temp_expr[i + 1]
            result = self._add(result, b) if op == '+' else self._subtract(result, b)

        return result

    def _format_expression(self) -> str:
        items = []
        for item in self.expression:
            if isinstance(item, (int, float)):
                formatted = self._format_number(item)
                items.append(f'({formatted})' if item < 0 else formatted)
            else:
                items.append(item)
        return ''.join(items)

    @staticmethod
    def _format_number(number: float) -> str:
        """최종 결과나 표현식의 숫자를 깔끔하게 포맷"""
        return f'{number:g}'

    # --- 연산 메소드 ---
    @staticmethod
    def _add(a, b):
        return a + b

    @staticmethod
    def _subtract(a, b):
        return a - b

    @staticmethod
    def _multiply(a, b):
        return a * b

    @staticmethod
    def _divide(a, b):
        if b == 0:
            raise ZeroDivisionError
        return a / b


class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = Calculator()  # 계산 로직 클래스 인스턴스 생성
        self._init_ui()

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

        for position, button_text in zip(positions, buttons):
            if button_text == '':
                continue

            # 백스페이스 버튼은 별도 처리
            if button_text == '<-':
                btn = QPushButton(button_text)
                btn.setStyleSheet('font-size: 20px; height: 50px;')
                btn.clicked.connect(self._handle_backspace)
            else:
                btn = QPushButton(button_text)
                btn.setStyleSheet('font-size: 20px; height: 50px;')
                btn.clicked.connect(self._button_clicked)

            grid.addWidget(btn, position[0], position[1])

        self._update_display()

    def _update_display(self):
        """계산기 로직에서 텍스트를 가져와 화면 업데이트"""
        self.display.setText(self.calculator.get_display_text())

    def _button_clicked(self):
        """버튼 클릭 이벤트를 처리하고 계산 로직 호출"""
        button = self.sender()
        button_text = button.text()  # type: ignore

        self.calculator.process_button(button_text)
        self._update_display()

    def _handle_backspace(self):
        """백스페이스 입력을 처리"""
        if self.calculator.current_input:
            self.calculator.current_input = self.calculator.current_input[:-1]
        self._update_display()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc_ui = CalculatorUI()
    calc_ui.show()
    sys.exit(app.exec_())
