#! /usr/bin/env python

# Copyright 2022 Alan B. Christie
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Types that can be used with argparse.
"""
import argparse
from datetime import date
from typing import Any, Callable

from dateutil.parser import parse
from dateutil.parser import parserinfo
from dateutil.parser import ParserError


# Set the dateutil parser info to 'day-first'
# so 01/05/09 is interpreted as 1st May 2009
_PARSER_INFO = parserinfo(dayfirst=True)


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
            parse(value, parserinfo=_PARSER_INFO)
        except ParserError:
            raise argparse.ArgumentTypeError(f"Not a valid date [{arg}]")
        return parse(value, parserinfo=_PARSER_INFO).date()

    return date_checker
