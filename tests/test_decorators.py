import os
from tempfile import NamedTemporaryFile

import pytest
from _pytest.capture import CaptureFixture

from src.decorators import log


# Вспомогательные функции с аннотациями типов
def successful_func(a: int, b: int) -> int:
    return a + b


def failing_func(a: int, b: int) -> int:
    raise ValueError("Test error message")


class TestLogDecorator:
    def test_console_logging(self, capsys: CaptureFixture) -> None:
        @log()
        def decorated_func(a: int, b: int) -> int:
            return a + b

        result = decorated_func(2, 3)

        captured = capsys.readouterr()
        output = captured.out

        assert "decorated_func - START" in output
        assert "Args: 2, 3" in output
        assert "Result: 5" in output
        assert "END" in output
        assert result == 5

    def test_console_error_logging(self, capsys: CaptureFixture) -> None:
        @log()
        def decorated_func(a: int, b: int) -> int:
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            decorated_func(2, 3)

        captured = capsys.readouterr()
        output = captured.out

        assert "Error: ValueError" in output
        assert "Test error" in output
        assert "END" in output

    def test_file_logging(self) -> None:
        with NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:

            @log(filename=tmp_path)
            def decorated_func(a: int, b: int) -> int:
                return a + b

            decorated_func(2, 3)

            with open(tmp_path, "r") as f:
                content = f.read()

            assert "decorated_func - START" in content
            assert "Args: 2, 3" in content
            assert "Result: 5" in content
            assert "END" in content
        finally:
            os.unlink(tmp_path)

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (1, 2, 3),
            (0, 0, 0),
            (-1, 1, 0),
        ],
    )
    def test_parametrized(self, a: int, b: int, expected: int, capsys: CaptureFixture) -> None:
        @log()
        def decorated_func(a: int, b: int) -> int:
            return a + b

        result = decorated_func(a, b)

        captured = capsys.readouterr()
        output = captured.out

        assert f"Args: {a}, {b}" in output
        assert f"Result: {expected}" in output
        assert "END" in output
        assert result == expected
