#! /usr/bin/env python
"""A utility that's used to record trips to the Schengen area
and then allow a user to calculate when they can arrive in the
area for a given trip duration.
"""
import argparse
from collections import OrderedDict
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from dateutil.parser import parse
import humanize
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy import Column, Date, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.engine import Connection

from ap_types import ap_date_type, ap_ranged_type

_USERNAME_LENGTH: int = 80
_MAX_DURATION_180: int = 90
_ONE_DAY: timedelta = timedelta(days=1)

_METADATA: MetaData = MetaData()

_USER: Table = Table(
    "user",
    _METADATA,
    Column("id", Integer(), primary_key=True),
    Column("username", String(_USERNAME_LENGTH), unique=True, nullable=False),
)

_PRESENCE: Table = Table(
    "presence",
    _METADATA,
    Column("id", Integer(), primary_key=True),
    Column("user_id", ForeignKey("user.id")),
    Column("date", Date(), nullable=False),
)


def presence_count_180(connection: Connection, *, user: _USER, at: date) -> int:
    """Returns the number of days the user's been present in the Schengen
    area during the 180 days prior to the given date.
    """
    most_recent_date_180 = at - timedelta(days=180)
    s = select([func.count(_PRESENCE.c.date)]).where(
        _PRESENCE.c.date > most_recent_date_180, _PRESENCE.c.user_id == user.id
    )
    rp = connection.execute(s)
    return int(rp.first().count_1)


def presence_180(
    connection: Connection, *, user: _USER, at: date
) -> Tuple[date, Dict[date, int]]:
    """Returns the date 180 days ago and the dates, the accumulated days,
    and the age of the date the user's been present in the Schengen area during the
    180 days prior to the given date.

    An OrderedDict is returned where the first entry is the most recent visit date.
    """
    oldest_date_180 = at - timedelta(days=180)
    s = (
        select([_PRESENCE.c.date])
        .where(_PRESENCE.c.date > oldest_date_180, _PRESENCE.c.user_id == user.id)
        .order_by(_PRESENCE.c.date)
    )
    rp = connection.execute(s)
    response: OrderedDict = OrderedDict()
    days: int = 0
    for presence in rp:
        days += 1
        presence_date: date = presence[0]
        response[presence_date] = days
    return oldest_date_180, OrderedDict(reversed(list(response.items())))


def find_start_date(connection: Connection, *, user: _USER, duration: int) -> date:
    """Given a user and trip duration this code returns
    the first date the user can be present in the Schengen region.
    """
    today = date.today()
    # Earliest start-date is today.
    start_date = today
    presence_count_today = presence_count_180(connection, user=user, at=today)
    today_overstay = duration + presence_count_today - _MAX_DURATION_180
    if today_overstay > 0:
        start_date += timedelta(days=today_overstay)
    return start_date


def add_trip(
    connection: Connection, *, user: _USER, arrival: date, departure: date
) -> int:
    """Populates the database with a trip, returning the number of days added."""
    # Create some presence records
    num_days: int = 0
    presence_date = arrival
    while presence_date <= departure:
        # Does a presence date exist for this date?
        s = select([_PRESENCE]).where(
            _PRESENCE.c.date == presence_date, _PRESENCE.c.user_id == user.id
        )
        rp = connection.execute(s)
        if not rp.first():
            ins = insert(_PRESENCE).values(user_id=user.id, date=presence_date)
            _ = connection.execute(ins)
            num_days += 1
        presence_date += timedelta(days=1)
    return num_days


def get_or_add_user(connection: Connection, *, username: str) -> _USER:
    s = select([_USER]).where(_USER.c.username == username)
    rp = connection.execute(s)
    user = rp.first()
    if not user:
        ins = insert(_USER).values(username="alan.christie")
        rp = connection.execute(ins)
        s = select([_USER]).where(_USER.c.username == username)
        rp = connection.execute(s)
        user = rp.first()
    assert user
    return user


def main(arg_list: Optional[List[str]] = None) -> None:
    """The 'main' entrypoint of the code."""

    # Build an argument parser,
    # using the supplied args (or command-line if none supplied)
    parser = argparse.ArgumentParser(prog="schengen", description="Trip calculator")
    parser.add_argument("username", type=str)
    parser.add_argument(
        "-t", "--trip-duration", type=ap_ranged_type(int, 1, _MAX_DURATION_180)
    )
    parser.add_argument("-a", "--arrival", type=ap_date_type())
    parser.add_argument("-d", "--departure", type=ap_date_type())
    parser.add_argument("-s", "--spent", action="store_true")
    args = parser.parse_args(arg_list)

    # Can't specify trip-duration and spent
    if args.trip_duration and args.spent:
        parser.error("Cannot use --spent and --trip-duration")

    # If arrival, departure must be specified (and vice-versa)
    if args.arrival and not args.departure or not args.arrival and args.departure:
        parser.error(
            "Arrival and Departure are mutually inclusive."
            " You cannot use one without the other"
        )
    # ...and arrival cannot be after departure
    if args.arrival and args.arrival > args.departure:
        parser.error("Arrival cannot be after Departure")

    # If no arrival, must provide a trip-duration, or query days spent,
    # otherwise the app does nothing.
    if not args.arrival and not args.trip_duration and not args.spent:
        parser.error("Must provide an Arrival and Departure, Trip Duration or Spent")

    # Username is required
    username: str = args.username

    # Next trip duration is optional
    next_trip_duration: int = args.trip_duration if args.trip_duration else 0

    # Create the DB engine and connect...
    engine = create_engine("sqlite:///schengen.db")
    _METADATA.create_all(engine)
    connection: Connection = engine.connect()

    # Get (or create) the user
    user: _USER = get_or_add_user(connection, username=username)

    # Has a new (prior) trip been provided?
    if args.arrival:
        arrival_date: date = args.arrival
        departure_date: date = args.departure
        num_days_added: int = add_trip(
            connection, user=user, arrival=arrival_date, departure=departure_date
        )
        if num_days_added:
            print(f"{num_days_added}-day trip added")

    today: date = date.today()
    presence_count_today: int = presence_count_180(connection, user=user, at=today)
    suffix = "s" if presence_count_today > 1 else ""
    print(
        "Your tally for the Schengen Area"
        f" today is {presence_count_today} day{suffix}"
    )

    # Display what's spent or calculate the earliest arrival date for a _new_ trip?
    if args.spent:
        date_180, presence = presence_180(connection, user=user, at=today)
        # Dates are in reverse-chronological order (most recent first).
        # Separate visits (i.e. dates separated by more than a day) with a short
        # horizontal line.
        day_date: str = humanize.naturaldate(date_180)
        print("+++")
        print(f"Presence (age-off): {day_date}")
        print("+++")

        last_date: Optional[date] = None
        for key, value in presence.items():
            if last_date:
                if last_date - key > _ONE_DAY:
                    print("---")
            day_date = humanize.naturaldate(key)
            print(f"Date: {day_date} ({value})")
            last_date = key
    elif next_trip_duration:
        next_trip_arrival: date = find_start_date(
            connection, user=user, duration=next_trip_duration
        )
        humanized_next_trip_arrival = humanize.naturalday(
            next_trip_arrival, format="%d %b %Y"
        )
        print(
            f"For a {next_trip_duration}-day trip,"
            f" you can arrive in the Schengen Area {humanized_next_trip_arrival}"
        )


if __name__ == "__main__":
    main()
