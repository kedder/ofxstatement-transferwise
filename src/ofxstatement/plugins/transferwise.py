from typing import Set, List, Iterable, TextIO, Optional
import itertools
from decimal import Decimal

from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import (
    Statement,
    StatementLine,
    BankAccount,
    generate_unique_transaction_id,
)


class TransferwisePlugin(Plugin):
    """Transferwise CSV format"""

    def get_parser(self, filename: str) -> "TransferwiseParser":
        return TransferwiseParser(open(filename, "rt"))


class TransferwiseParser(CsvStatementParser):
    date_format: str = "%d-%m-%Y"
    mappings = {
        "amount": 2,
        "date": 1,
        "memo": 4,
        "refnum": 0,
        "payee": 11,
    }

    def __init__(self, fin: TextIO) -> None:
        super().__init__(fin)
        self._unique: Set[str] = set()

    def parse(self) -> Statement:
        stmt = super().parse()
        return stmt

    def split_records(self) -> Iterable[List[str]]:
        items = super().split_records()
        # Skip the header line
        yield from itertools.islice(items, 1, None)

    def parse_record(self, line: List[str]) -> Optional[StatementLine]:
        """Parse given transaction line and return StatementLine object"""
        sl = super().parse_record(line)
        if sl is None:
            return None
        sl.id = generate_unique_transaction_id(sl, self._unique)
        payee_acc_no = line[12]
        if payee_acc_no:
            sl.bank_account_to = BankAccount("", payee_acc_no)

        assert sl.amount is not None
        sl.trntype = "DEBIT" if sl.amount > Decimal(0) else "CREDIT"
        return sl
