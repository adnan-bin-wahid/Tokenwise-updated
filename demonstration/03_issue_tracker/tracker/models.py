from dataclasses import dataclass


@dataclass
class Issue:
    identifier: str
    title: str
    owner: str
    status: str = "open"
    closed_by: str | None = None
