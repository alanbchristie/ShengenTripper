"""Types that can be used with argparse.
"""
import argparse
from datetime import date
from typing import Any, Callable

from dateutil.parser import parse
from dateutil.parser import ParserError


def ap_ranged_type(value_type: Any, min_value: Any, max_value: Any) -> Callable:
    """A custom type (a range-checker) for use with argparse."""

    def range_checker(arg: str) -> Any:
        try:
            f = value_type(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Must be a valid {value_type}")
        if f < min_value or f > max_value:
            raise argparse.ArgumentTypeError(f"Must be {min_value} .. {max_value}")
        return f

    return range_checker


def ap_date_type() -> Callable:
    """A custom type for use with argparse."""

    def date_checker(arg: str) -> date:
        try:
            f = str(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Must be a valid str")
        try:
            parse(f)
        except ParserError:
            raise argparse.ArgumentTypeError(f"Not a valid date [{arg}]")
        return parse(f).date()

    return date_checker
