from csv import DictReader
from datetime import datetime
from typing import Dict, Iterable, Optional
from decimal import Decimal

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import (
    Statement,
    StatementLine,
    BankAccount,
)


class TransferwisePlugin(Plugin):
    """Transferwise CSV format"""

    def get_parser(self, filename: str) -> "TransferwiseParser":
        default_ccy = self.settings.get("currency")
        account_id = self.settings.get("account")
        return TransferwiseParser(filename, default_ccy, account_id)


class TransferwiseParser(StatementParser[Dict[str, str]]):
    def __init__(
        self, filename: str, currency: str | None = None, account_id: str | None = None
    ) -> None:
        super().__init__()
        self.filename = filename
        self.currency = currency
        self.account_id = account_id

    def parse(self) -> Statement:
        stmt = super().parse()
        stmt.currency = self.currency
        stmt.account_id = self.account_id
        return stmt

    def split_records(self) -> Iterable[Dict[str, str]]:
        with open(self.filename, "rt") as f:
            yield from DictReader(f)

    def parse_record(self, line: Dict[str, str]) -> Optional[StatementLine]:
        """Parse given transaction line and return StatementLine object"""
        sl = StatementLine()

        sl.id = line["TransferWise ID"]
        sl.date = datetime.strptime(line["Date Time"], "%d-%m-%Y %H:%M:%S.%f")
        sl.memo = line["Description"]
        sl.amount = Decimal(line["Amount"])

        currency = line["Currency"]
        if currency != self.currency:
            # Skip lines in some other currencies
            return None

        sl.memo = self._make_memo(line)

        payee_acc_no = line["Payee Account Number"]
        if payee_acc_no:
            sl.bank_account_to = BankAccount("", payee_acc_no)

        assert sl.amount is not None
        sl.trntype = line["Transaction Type"]
        return sl

    def _make_memo(self, line: Dict[str, str]) -> str:
        descr = line["Description"]
        payref = line["Payment Reference"]
        exc_from = line["Exchange From"]
        exc_to = line["Exchange To"]
        exc_rate = line["Exchange Rate"]

        memo = descr
        if payref:
            memo += f" ({payref})"
        if exc_from and exc_to and exc_rate:
            memo += f", {exc_rate} {exc_from}/{exc_to}"
        return memo
