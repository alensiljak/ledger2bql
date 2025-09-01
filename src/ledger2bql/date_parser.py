def parse_date(date_str: str) -> str:
    """
    Parses a date string and returns a full date string, assuming the beginning of the period.
    Handles YYYY, YYYY-MM, and YYYY-MM-DD formats.
    """
    parts = date_str.split('-')
    if len(parts) == 1:  # YYYY
        year = int(parts[0])
        return f"{year}-01-01"
    elif len(parts) == 2:  # YYYY-MM
        year = int(parts[0])
        month = int(parts[1])
        return f"{year:04d}-{month:02d}-01"
    elif len(parts) == 3:  # YYYY-MM-DD
        return date_str
    else:
        raise ValueError(f"Invalid date format: {date_str}")