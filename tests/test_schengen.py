import os

import pytest

from schengen import main

pytestmark = pytest.mark.unit

_SQLITE_FILE: str = "schengen.db"


@pytest.fixture
def initialise():
    """Removes any pre-existing database file.
    Used to ensure tests are repeatable, regardless of the execution order.
    """
    if os.path.exists(_SQLITE_FILE):
        os.remove(_SQLITE_FILE)


@pytest.mark.parametrize("option", (["-h"], ["--help"]))
def test_help(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert "Trip calculator" in output


@pytest.mark.parametrize("option", (["alan.christie"],))
def test_with_only_username(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().err
    assert "Must provide an Arrival and Departure, Trip Duration or Spent" in output


@pytest.mark.parametrize(
    "option",
    (
        ["alan.christie", "-a", "4-nov-22", "-d", "21-nov-22"],
        ["alan.christie", "--arrival", "4-nov-22", "--departure", "21-nov-22"],
    ),
)
def test_adding_trip(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert "18-day trip added" in output


@pytest.mark.parametrize("option", (["alan.christie", "--arrival", "4-nov-22"],))
def test_trip_with_missing_departure(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().err
    assert "Arrival and Departure are mutually inclusive" in output


@pytest.mark.parametrize("option", (["alan.christie", "--departure", "21-nov-22"],))
def test_trip_with_missing_arrival(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().err
    assert "Arrival and Departure are mutually inclusive" in output


@pytest.mark.parametrize("option", (["alan.christie", "--arrival", "--departure"],))
def test_trip_with_missing_dates(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().err
    assert "expected one argument" in output


@pytest.mark.parametrize("option", (["alan.christie", "-t"]))
def test_trip_query_with_missing_period(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().err
    assert "unrecognized arguments" in output


@pytest.mark.parametrize(
    "option",
    (["alan.christie", "-t", "90"], ["alan.christie", "--trip-duration", "90"]),
)
def test_trip_query(initialise, capsys, option):
    try:
        main(option)
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert "For a 90-day trip, you can arrive in the Schengen Area today" in output
