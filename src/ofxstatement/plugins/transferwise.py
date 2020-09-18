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
        default_ccy = self.settings.get("currency")
        account_id = self.settings.get("account")
        return TransferwiseParser(open(filename, "rt"), default_ccy, account_id)


class TransferwiseParser(CsvStatementParser):
    date_format: str = "%d-%m-%Y"
    mappings = {
        "amount": 2,
        "date": 1,
        "memo": 4,
        "refnum": 0,
    }

    def __init__(
        self, fin: TextIO, currency: str = None, account_id: str = None
    ) -> None:
        super().__init__(fin)
        self.currency = currency
        self.account_id = account_id
        self._unique: Set[str] = set()

    def parse(self) -> Statement:
        stmt = super().parse()
        stmt.currency = self.currency
        stmt.account_id = self.account_id
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

        ccy = line[3]
        if ccy != self.currency:
            # Skip lines in some other currencies
            return None

        sl.memo = self._make_memo(line)

        sl.id = generate_unique_transaction_id(sl, self._unique)
        payee_acc_no = line[12]
        if payee_acc_no:
            sl.bank_account_to = BankAccount("", payee_acc_no)

        assert sl.amount is not None
        sl.trntype = "DEBIT" if sl.amount > Decimal(0) else "CREDIT"
        return sl

    def _make_memo(self, line: List[str]) -> str:
        descr = line[4]
        payref = line[5]
        exc_from = line[7]
        exc_to = line[8]
        exc_rate = line[9]

        memo = descr
        if payref:
            memo += f" ({payref})"
        if exc_from and exc_to and exc_rate:
            memo += f", {exc_rate} {exc_from}/{exc_to}"
        return memo
