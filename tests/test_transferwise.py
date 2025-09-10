import os

from ofxstatement.ui import UI

from ofxstatement_wise.wise import TransferwisePlugin


def test_transferwise() -> None:
    config = {"currency": "USD", "account": "TW1"}
    plugin = TransferwisePlugin(UI(), config)
    here = os.path.dirname(__file__)
    sample_filename = os.path.join(here, "sample-statement.csv")

    parser = plugin.get_parser(sample_filename)
    statement = parser.parse()

    assert statement is not None

    assert len(statement.lines) == 5
    # all ids are unique
    assert len(set(ln.id for ln in statement.lines)) == 5
    assert all(ln.amount for ln in statement.lines)
