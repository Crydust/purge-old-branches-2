from pathlib import Path

from purge_old_branches_2 import cli


def test_parse_arguments():
    args = cli._parse_arguments([
        "--csv-file", "foo1",
        "--csv-ticket-col", "foo2",
        "--csv-status-col", "foo3",
        "--csv-done-status", "foo4",
        "--repo", "foo5a", "foo5b",
        "--prefix", "foo6",
        "--target", "foo7",
        "--days", "8",
        "--remote",
        "--dry-run",
    ])
    assert args.csv_file == Path("foo1")
    assert args.csv_ticket_col == "foo2"
    assert args.csv_status_col == "foo3"
    assert args.csv_done_status == "foo4"
    assert args.repo == [Path("foo5a"), Path("foo5b")]
    assert args.prefix == "foo6"
    assert args.target == "foo7"
    assert args.days == 8
    assert args.remote is True
    assert args.dry_run is True
