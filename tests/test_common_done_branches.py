from purge_old_branches_2.cli import _common_done_branches


def test_common_done_branches():
    branches = _common_done_branches(
        prefix="foo-",
        branch_sets=[
            {"foo-1", "foo-2-bar", "foo-xyz-4", "foo-10"},
            {"foo-1", "foo-2-bar", "foo-3", "foo-10"},
        ],
        done_tickets=["foo-1", "foo-2", "foo-3", "foo-10"],
    )
    assert branches == ["foo-1", "foo-2-bar", "foo-10"]
