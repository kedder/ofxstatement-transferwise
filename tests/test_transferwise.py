import os

from ofxstatement.ui import UI

from ofxstatement_wise.wise import TransferwisePlugin


def test_transferwise(snapshot) -> None:
    config = {"currency": "USD", "account": "TW1"}
    plugin = TransferwisePlugin(UI(), config)
    here = os.path.dirname(__file__)
    sample_filename = os.path.join(here, "sample-statement.csv")

    parser = plugin.get_parser(sample_filename)
    statement = parser.parse()

    assert statement == snapshot
