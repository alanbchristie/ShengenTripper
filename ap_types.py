#! /usr/bin/env python
"""Types that can be used with argparse.
"""
import argparse
from datetime import date
from typing import Any, Callable

from dateutil.parser import parse
from dateutil.parser import ParserError


def ap_ranged_type(
    value_type: Any, min_value: Any, max_value: Any
) -> Callable[[str], Any]:
    """A custom type (a range-checker) for use with argparse."""

    def range_checker(arg: str) -> Any:
        try:
            value = value_type(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Must be a valid {value_type}")
        if value < min_value or value > max_value:
            raise argparse.ArgumentTypeError(f"Must be {min_value} .. {max_value}")
        return value

    return range_checker


def ap_date_type() -> Callable[[str], date]:
    """A custom type for use with argparse."""

    def date_checker(arg: str) -> date:
        try:
            value = str(arg)
        except ValueError:
            raise argparse.ArgumentTypeError("Must be a valid str")
        try:
            parse(value)
        except ParserError:
            raise argparse.ArgumentTypeError(f"Not a valid date [{arg}]")
        return parse(value).date()

    return date_checker
