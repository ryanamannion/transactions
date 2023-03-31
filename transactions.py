import re
import csv
from typing import List, Dict, Any, Tuple, Union
from datetime import datetime
from collections import defaultdict
from pprint import pprint

Transaction = Dict[str, Any]
TransactionList = List[Transaction]

DATE_FMT = "%m/%d/%Y"


# Some pre-defined configurations #

AMEX = {
    'amount': 'amount',
    'date': 'date',
    'category': 'category',
    'description': 'description',
    'ignore_negatives': True
}

configs = {
    'amex': AMEX
}


def load_csv(path):
    with open(path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)


def transform_data(
        transactions: TransactionList,
        ignore_negatives: bool = True
) -> TransactionList:
    transformed = []
    for t in transactions:
        new_t = {k.lower(): v for k, v in t.items()}
        if not isinstance(new_t['date'], datetime):
            new_t['date'] = datetime.strptime(new_t['date'], DATE_FMT)
        new_t['amount'] = float(new_t['amount'])
        if ignore_negatives and new_t['amount'] < 0:
            continue
        transformed.append(new_t)

    return transformed


class Transactions:

    def __init__(
            self,
            **config
    ) -> None:
        self.transactions = []
        self.amount_key = config['amount']
        self.date_key = config['date']
        self.category_key = config['category']
        self.description_key = config['description']
        self.ignore_negatives = config['ignore_negatives']

        self.config = config

        self._by_category = None

    def __repr__(self):
        vals = (self.date_range(), len(self), f"{self.sum():0.02f}")
        return "<Transactions {}; n={}, sum=${}>".format(*vals)

    def __len__(self):
        return len(self.transactions)

    def __contains__(self, item):
        return item in self.transactions

    def __sub__(self, other):
        diff = [t for t in self.transactions if t not in other]
        return Transactions(**self.config).from_ft(diff)

    def __add__(self, other):
        return Transactions(**self.config).from_ft(
            [*self.transactions, *other.transactions]
        )

    def from_csv(self, file_path):
        self.transactions = transform_data(
            load_csv(file_path), ignore_negatives=self.ignore_negatives
        )
        return self

    def from_ft(self, free_table: List[dict]):
        self.transactions = transform_data(
            free_table, ignore_negatives=self.ignore_negatives
        )
        return self

    def index_by(self, key):
        indexed = defaultdict(list)
        [indexed[t[key]].append(t) for t in self.transactions]
        return {
            k: Transactions(**self.config).from_ft(V)
            for k, V in indexed.items()
        }

    def by_category(self):
        if self._by_category is not None:
            return self._by_category
        return self.index_by(self.category_key)

    def by_description(self, re_str, case_sensitive: bool = False, *flags):
        flags = [*flags, re.I]
        if re.I in flags and case_sensitive:
            flags = [f for f in flags if f != re.I]
        regex = re.compile(re_str, *flags)
        matches = []
        for t in self.transactions:
            if regex.search(t[self.description_key]):
                matches.append(t)
        return Transactions(**self.config).from_ft(matches)

    def by_month(self):
        months = defaultdict(list)
        for t in self.transactions:
            month = t['date'].strftime("%h")
            months[month].append(t)
        return {
            k: Transactions(**self.config).from_ft(V)
            for k, V in months.items()
        }

    def print_transactions(self):
        pprint(self.transactions)

    def sum(self) -> float:
        _sum = 0.0
        for t in self.transactions:
            amnt = float(t[self.amount_key])
            _sum += amnt
        return _sum

    def get_date_range(self) -> Union[Tuple[datetime, datetime], None]:
        dates = [t[self.date_key] for t in self.transactions]
        if len(dates) == 0:
            return None
        min_date = min(dates)
        max_date = max(dates)
        return min_date, max_date

    def date_range(self) -> str:
        d_range = self.get_date_range()
        if d_range:
            return " - ".join([t.strftime("%D") for t in d_range])
        else:
            return "N/A - N/A"


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    activity = Transactions(**AMEX).from_csv(path)
    print(activity)
