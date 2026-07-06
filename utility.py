from datetime import datetime, timedelta, date

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def resolve_expense_date(when: str | None) -> str:
    """
    Convert common natural-language dates into YYYY-MM-DD.

    Supported examples:
        today
        yesterday
        tomorrow
        3 days ago
        last friday
        this monday
        next sunday
        2026-07-04
        July 4 2026
        Jul 4, 2026
    """

    if when is None or when.strip() == "":
        return date.today().strftime("%Y-%m-%d")

    text = when.strip().lower()
    today = datetime.today()

    # today
    if text == "today":
        return today.strftime("%Y-%m-%d")

    # yesterday
    if text == "yesterday":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # tomorrow
    if text == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # X days ago
    if text.endswith("days ago"):
        parts = text.split()
        if len(parts) == 3 and parts[0].isdigit():
            days = int(parts[0])
            return (today - timedelta(days=days)).strftime("%Y-%m-%d")

    # last monday
    if text.startswith("last "):
        weekday_name = text[5:]
        if weekday_name in WEEKDAYS:
            target = WEEKDAYS[weekday_name]
            diff = (today.weekday() - target) % 7
            if diff == 0:
                diff = 7
            return (today - timedelta(days=diff)).strftime("%Y-%m-%d")

    # this monday
    if text.startswith("this "):
        weekday_name = text[5:]
        if weekday_name in WEEKDAYS:
            target = WEEKDAYS[weekday_name]
            diff = target - today.weekday()
            return (today + timedelta(days=diff)).strftime("%Y-%m-%d")

    # next monday
    if text.startswith("next "):
        weekday_name = text[5:]
        if weekday_name in WEEKDAYS:
            target = WEEKDAYS[weekday_name]
            diff = (target - today.weekday()) % 7
            if diff == 0:
                diff = 7
            return (today + timedelta(days=diff)).strftime("%Y-%m-%d")

    # Try common date formats
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%B %d %Y",      # July 4 2026
        "%b %d %Y",      # Jul 4 2026
        "%B %d, %Y",     # July 4, 2026
        "%b %d, %Y",     # Jul 4, 2026
    ]

    for fmt in formats:
        try:
            return datetime.strptime(when.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    raise ValueError(f"Unable to understand date: {when}")


# from datetime import date
# import dateparser
#
#
# def resolve_expense_date(when: str | None) -> str:
#     """
#     Convert a natural language date into YYYY-MM-DD.
#
#     Examples:
#         today
#         yesterday
#         3 days ago
#         last Friday
#         2026-07-04
#         July 4 2026
#         and so on ...
#     """
#
#     if when is None or when.strip() == "":
#         return date.today().strftime("%Y-%m-%d")
#
#     parsed = dateparser.parse(
#         when,
#         settings={
#             "PREFER_DATES_FROM": "past",
#             "DATE_ORDER": "YMD",
#         },
#     )
#
#     if parsed is None:
#         raise ValueError(f"Unable to understand date: {when}")
#
#     return parsed.strftime("%Y-%m-%d")