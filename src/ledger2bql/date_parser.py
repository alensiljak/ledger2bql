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


def parse_date_range(date_range_str: str) -> tuple:
    """
    Parses a date range string and returns (begin_date, end_date) tuple.
    Supports formats like:
    - "2025" -> ("2025-01-01", "2026-01-01")  # Year (exclusive end)
    - "2025-08" -> ("2025-08-01", "2025-09-01")  # Month (exclusive end)
    - "2025-08-15" -> ("2025-08-15", "2025-08-16")  # Day (exclusive end)
    - "2025..2026" -> ("2025-01-01", "2027-01-01")  # Year range (exclusive end)
    - "2025-08.." -> ("2025-08-01", None)  # From month onwards
    - "..2025-09" -> (None, "2025-09-01")  # Up to September 2025 (exclusive)
    - "2025-08..2025-10" -> ("2025-08-01", "2025-11-01")  # Month range (exclusive end)
    - "2025..2025-02" -> ("2025-01-01", "2025-03-01")  # Year to month range (exclusive end)
    """
    if '..' in date_range_str:
        parts = date_range_str.split('..')
        if len(parts) != 2:
            raise ValueError(f"Invalid date range format: {date_range_str}")
        
        start_part, end_part = parts
        
        # Handle start date
        if start_part:
            start_date = parse_date(start_part)
        else:
            start_date = None
            
        # Handle end date
        if end_part:
            # For end date in range syntax, we parse it directly as the exclusive end date
            end_date = parse_date(end_part)
        else:
            end_date = None
            
        return start_date, end_date
    else:
        # Single date - treat as beginning of period, end is exclusive
        single_date = parse_date(date_range_str)
        
        # Calculate the exclusive end date
        parts = date_range_str.split('-')
        if len(parts) == 1:  # YYYY
            year = int(parts[0]) + 1
            end_date = f"{year}-01-01"
        elif len(parts) == 2:  # YYYY-MM
            year = int(parts[0])
            month = int(parts[1]) + 1
            if month > 12:
                year += 1
                month = 1
            end_date = f"{year:04d}-{month:02d}-01"
        elif len(parts) == 3:  # YYYY-MM-DD
            # For specific date, we add one day
            from datetime import datetime, timedelta
            date_obj = datetime.strptime(date_range_str, "%Y-%m-%d")
            date_obj += timedelta(days=1)
            end_date = date_obj.strftime("%Y-%m-%d")
        else:
            raise ValueError(f"Invalid date format: {date_range_str}")
            
        return single_date, end_date