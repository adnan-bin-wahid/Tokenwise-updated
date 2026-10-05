ZONE_DAYS = {"local": 1, "regional": 3, "remote": 7}


def delivery_days(zone: str, express: bool = False) -> int:
    if zone not in ZONE_DAYS:
        raise ValueError("Unknown delivery zone")
    return max(1, ZONE_DAYS[zone] - (2 if express else 0))


def tracking_summary(events: list[str]) -> str:
    known = {"packed", "dispatched", "delivered"}
    if any(event not in known for event in events):
        raise ValueError("Unknown tracking event")
    return events[-1] if events else "pending"
