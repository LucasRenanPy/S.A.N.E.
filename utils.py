import json
import unicodedata
from datetime import datetime


def normalizar(txt):

    if not txt:
        return ""

    s = unicodedata.normalize('NFD', str(txt))
    s = ''.join(
        ch for ch in s
        if unicodedata.category(ch) != 'Mn'
    )

    s = s.split('-')[0].split()[0]

    return s.lower().strip()


def parse_list_field(val):

    if not val:
        return []

    if isinstance(val, list):
        return val

    if isinstance(val, str):
        try:
            parsed = json.loads(val)

            if isinstance(parsed, list):
                return parsed

        except json.JSONDecodeError:
            return [
                p.strip()
                for p in val.split(',')
                if p.strip()
            ]

    return []


def to_minutes(hhmm):

    try:
        parts = hhmm.split(':')

        if len(parts) != 2:
            raise ValueError("Invalid time format")

        h, m = map(int, parts)

        return h * 60 + m

    except Exception as e:
        raise ValueError(f"Invalid time format: {e}")


def safe_parse_date(v, format="%Y-%m-%d"):

    if not v:
        return None

    try:
        return datetime.strptime(v, format).date()

    except ValueError:
        return None