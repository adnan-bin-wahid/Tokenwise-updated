from collections import Counter
import csv
from io import StringIO


def activity_summary(events: list[dict]) -> dict[str, int]:
    """Count operational actions without inspecting passwords or account state."""
    return dict(sorted(Counter(event["action"] for event in events).items()))


def export_activity(events: list[dict]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["actor", "action"])
    writer.writeheader()
    for event in events:
        writer.writerow({key: event[key] for key in writer.fieldnames})
    return stream.getvalue()
