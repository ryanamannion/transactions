# Transactions

No requirements, pure python baby. Works on 3.7+

Run `transactions.py` with a path to a CSV downloaded from AMEX (make sure to 
select to include extra information in the download dialog)

e.g. `$ python transactions.py /path/to/activity.csv`

This will just print a basic representation of that activity CSV:
`<Transactions 02/21/23 - 03/23/23; n=100, sum=$2000>`

The real fun comes with the interactive bit

## Interacting with `Transactions`

Download the code, `cd` into the directory that contains `transactions.py` 
(e.g. `$ cd transactions/`)

```python
>>> from transactions import Transactions, configs
>>> conf = configs['amex']
>>> path_to_csv = "/home/johndoe/Downloads/activity.csv"
>>> activity = Transactions(**conf).from_csv(path_to_csv)
>>> activity
'<Transactions 02/21/23 - 03/23/23; n=100, sum=$2000>'
```

Now that your transactions are loaded into memory, you can start to play around
with them.

### Group by Month

```python
>>> activity.by_month()
{'Mar': '<Transactions 03/01/23 - 03/23/23; n=50, sum=$1000>',
 'Feb': '<Transactions 02/01/23 - 02/29/23; n=50, sum=$1000>'
 }
```

### Group by Category

```python
>>> activity.by_category()
{'transportation': '<Transactions 03/01/23 - 03/23/23; n=50, sum=$1000>',
 'groceries': '<Transactions 02/01/23 - 03/23/23; n=50, sum=$1000>'
}
```

### Group by Description

Use regular expressions to find matching transaction descriptions. Use `re.I` to
make the search case-insensitive. Uses `re.search` so it should match to 
anywhere in the description, not just at the beginning of the string. 

```python
>>> import re
>>> activity.by_description(r'whole foods', re.I)
'<Transactions 02/01/23 - 03/23/23; n=50, sum=$1000>'
```


### Adding and Subtracting

Adding and subtracting works as you would imagine, subtracting removes items
that are in one list of transactions from another. For example, you group by
uber transactions

```python
>>> uber = activity.by_description("uber", re.I)
>>> uber
'<Transactions 02/27/23 - 03/19/23; n=5, sum=$110.00>'
```

but maybe after looking at `uber.transactions` you realize this groups together
uber trips and uber eats. Separate them like this

```python
>>> eats = uber.by_description("eats", re.I)
>>> eats
'<Transactions 02/27/23 - 03/05/23; n=2, sum=$35.00>'
>>> trips = uber - eats
'<Transactions 03/05/23 - 03/19/23; n=3, sum=$75.00>'
>>> added = trips + eats
>>> uber
'<Transactions 02/27/23 - 03/19/23; n=5, sum=$110.00>'
>>> added
'<Transactions 02/27/23 - 03/19/23; n=5, sum=$110.00>'
```

### Seeing Transactions

At any time, you can use Transactions.print_transactions() to use pretty print
to show you all the details about each individual transaction

```python
>>> eats.print_transactions()
[{'address': '1455 MARKET ST\n-',
  'amount': 10.00,
  'appears on your statement as': 'AplPay UBER EATS    help.uber.com       CA',
  'category': 'Restaurant-Restaurant',
  'city/state': 'SAN FRANCISCO\nCA',
  'country': 'UNITED STATES',
  'date': datetime.datetime(2023, 3, 5, 0, 0),
  'description': 'AplPay UBER EATS    help.uber.com       CA',,
  'reference': "123456789",
  'zip code': '94103'},
 {'address': '1455 MARKET ST\n-',
  'amount': 25.00,
  'appears on your statement as': 'AplPay UBER EATS    help.uber.com       CA',
  'category': 'Restaurant-Restaurant',
  'city/state': 'SAN FRANCISCO\nCA',
  'country': 'UNITED STATES',
  'date': datetime.datetime(2023, 2, 27, 0, 0),
  'description': 'AplPay UBER EATS    help.uber.com       CA',,
  'reference': "987654321",
  'zip code': '94103'}]

```
