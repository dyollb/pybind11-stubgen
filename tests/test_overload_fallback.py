"""Tests for overload fallback stub emission."""

from pybind11_stubgen.structs import (
    Argument,
    Decorator,
    Function,
    Identifier,
    QualifiedName,
    ResolvedType,
    Module,
)
from pybind11_stubgen.printer import Printer


def _make_overload_function(type_name: str) -> Function:
    return Function(
        name=Identifier("func"),
        args=[
            Argument(
                name=Identifier("x"),
                annotation=ResolvedType(QualifiedName.from_str(type_name)),
            )
        ],
        returns=ResolvedType(QualifiedName.from_str(type_name)),
        decorators=[Decorator("typing.overload")],
    )


def _render_module(*, print_overload_fallback: bool) -> str:
    printer = Printer(
        invalid_expr_as_ellipses=True,
        print_value_comments=False,
        print_overload_fallback=print_overload_fallback,
    )
    module = Module(
        name=Identifier("test_module"),
        functions=[
            _make_overload_function("int"),
            _make_overload_function("str"),
        ],
    )
    return "\n".join(printer.print_module(module))


def test_overload_fallback_enabled() -> None:
    output_str = _render_module(print_overload_fallback=True)

    assert "@typing.overload" in output_str
    assert output_str.count("def func") == 3
    assert "typing.Any" in output_str

    lines = output_str.split("\n")
    last_def_idx = max(i for i, line in enumerate(lines) if "def func" in line)
    if last_def_idx > 0:
        assert "@overload" not in lines[last_def_idx - 1].strip()


def test_overload_fallback_disabled() -> None:
    output_str = _render_module(print_overload_fallback=False)

    assert output_str.count("def func") == 2
