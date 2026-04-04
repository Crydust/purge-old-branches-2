from pathlib import Path

from purge_old_branches_2.csv_parser import CsvParser


def test_csv_parser(tmp_path: Path):
    csv = tmp_path / "test.csv"
    with open(csv, "w") as f:
        f.write("\n".join([
            "id,status",
            "TICKET-1,Done",
            "TICKET-2,Todo",
            "TICKET-3,Done",
            "FOOBAR-4,Done",
        ]))
    parser = CsvParser(csv, "id", "status", "Done", "TICKET-")
    done_tickets = parser.done_tickets()
    assert done_tickets == ["TICKET-1", "TICKET-3"]
