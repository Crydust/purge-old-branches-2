import csv
from pathlib import Path


class CsvParser:
    def __init__(self, file: Path, ticket_col: str, status_col: str, done_status: str, prefix: str):
        self.file = file
        self.ticket_col = ticket_col
        self.status_col = status_col
        self.done_status = done_status
        self.prefix = prefix

    def done_tickets(self) -> list[str]:
        with open(self.file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, dialect=csv.excel)
            if reader.fieldnames is None:
                raise ValueError("CSV file has no headers")
            if self.ticket_col not in reader.fieldnames:
                raise ValueError(f"Column '{self.ticket_col}' not found in CSV.")
            if self.status_col not in reader.fieldnames:
                raise ValueError(f"Column '{self.status_col}' not found in CSV.")
            return [row[self.ticket_col]
                    for row in reader
                    if row[self.ticket_col].startswith(self.prefix)
                    if row[self.status_col] == self.done_status
                    ]
        return []
