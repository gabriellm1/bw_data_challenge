import csv
from pathlib import Path
from pprint import pprint
from datetime import datetime, timedelta

transactions1 = list(csv.reader(Path('transactions1.csv').open()))
transactions2 = list(csv.reader(Path('transactions2.csv').open()))

def transaction_map(transactions):
    """
    Maps transactions dates by primary key (dept, value, beneficiary)

    Args:
        transactions (list): List of transactions, 
            must follow pattern [date, departament, value, beneficiary]

    Returns:
        transaction_dict(dict): A dictionary with the primary key as key 
            and a list of respective transactions dates
    """
    transaction_dict = {}
    for transaction in transactions:
        date, dept, value, beneficiary = transaction
        pk = (dept, value, beneficiary)
        if pk not in transaction_dict:
            transaction_dict[pk] = []
        transaction_dict[pk].append(datetime.strptime(date, "%Y-%m-%d"))
    return transaction_dict

def transaction_tag(transactions, transaction_mapped):
    """
    Tags transactions as FOUND or MISSING based on the mapped transactions

    Args:
        transactions (list): List of transactions, 
            must follow pattern [date, departament, value, beneficiary]
        transaction_mapped (dict): A dictionary with the primary key as key 
            and a list of respective transactions dates
    
    Returns:
        transaction_tagged (list): List of transactions, 
            with an additional tag, either FOUND or MISSING
    """
    transactions_tagged =  []
    for transaction in transactions:
        
        date, dept, value, beneficiary = transaction
        date = datetime.strptime(date, "%Y-%m-%d")
        pk = (dept, value, beneficiary)
        if pk in transaction_mapped.keys():
            transaction_mapped[pk].sort()
            for date_aux in transaction_mapped[pk]:
                if date_aux and abs((date - date_aux).days) <= 1:
                    transaction.append("FOUND")
                    transaction_mapped[pk].pop(0)
                    if not transaction_mapped[pk]:
                        transaction_mapped.pop(pk)
                    break
            if transaction[-1] != "FOUND":
                transaction.append("MISSING")
        else:
            transaction.append("MISSING")
        transactions_tagged.append(transaction)
    return transactions_tagged

def reconcile_accounts(transactions1, transactions2):
    """
    Reconciles two transactional lists based on transactions dates by primary key

    Args:
        transactions1 (list): List of transactions, 
            must follow pattern [date, departament, value, beneficiary]
        transactions2 (list): List of transactions, 
            must follow pattern [date, departament, value, beneficiary]
    Returns:
        transaction_tagged1 (list): List of transactions1, 
            with an additional tag, either FOUND or MISSING
        transaction_tagged2 (list): List of transactions2, 
            with an additional tag, either FOUND or MISSING
    """
    transaction_mapped1 = transaction_map(transactions1)
    transaction_mapped2 = transaction_map(transactions2)

    transactions_tagged1 = transaction_tag(transactions1, transaction_mapped2)
    transactions_tagged2 = transaction_tag(transactions2, transaction_mapped1)

    return transactions_tagged1, transactions_tagged2

result = reconcile_accounts(transactions1, transactions2)
pprint(result)