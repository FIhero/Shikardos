import datetime
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

T = TypeVar("T", bound=Callable[..., Any])


def log(filename: Optional[str] = None) -> Callable[[T], T]:
    """Автоматически логирует начало и конец выполнения функции, а также ее результаты или возникшие ошибки"""

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            args_repr = [repr(arg) for arg in args]
            kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)

            start_msg = f"{timestamp} - {func_name} - START\nArgs: {signature}\n"
            if filename:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(start_msg)
            else:
                print(start_msg, end="")

            try:
                result = func(*args, **kwargs)

                success_msg = f"{timestamp} - {func_name} - Result: {result!r}\nEND\n"
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(success_msg)
                else:
                    print(success_msg, end="")

                return result

            except Exception as e:
                error_msg = f"{timestamp} - {func_name} - Error: {type(e).__name__}: {e}\nEND\n"
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(error_msg)
                else:
                    print(error_msg, end="")
                raise

        return cast(T, wrapper)

    return decorator
