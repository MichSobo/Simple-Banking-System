"""
Code for interacting with a database.
"""
import sqlite3
from sqlite3 import Error


CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS card (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    number TEXT NOT NULL UNIQUE,
    pin TEXT NOT NULL,
    balance INTEGER DEFAULT 0 NOT NULL
);'''

INSERT_CARD = 'INSERT INTO card (number, pin) VALUES (?, ?);'

GET_CARD_BY_NUMBER = 'SELECT number, pin, balance FROM card WHERE number = ?;'
GET_ALL_CARDS = 'SELECT number, pin, balance FROM card;'

ADD_INCOME = 'UPDATE card SET balance = balance + ? WHERE number = ?;'

DELETE_CARD = 'DELETE FROM card WHERE number = ?';


def connect(db_filepath):
    """Set a database connection to the SQLite database.

    Args:
        db_filepath (str): path to database file

    Returns:
        obj: Connection object or None
    """
    try:
        connection = sqlite3.connect(db_filepath)
    except Error as e:
        print(e)
        connection = None

    return connection


def create_table(connection):
    with connection as c:
        c.execute(CREATE_TABLE)


def add_card(connection, number, pin):
    with connection as c:
        c.execute(INSERT_CARD, (number, pin))


def get_card_by_number(connection, number):
    with connection as c:
        return c.execute(GET_CARD_BY_NUMBER, (number,)).fetchall()


def get_all_cards(connection):
    with connection as c:
        return c.execute(GET_ALL_CARDS).fetchall()


def add_income(connection, number, income):
    """Add money to the account's current balance.

    Arguments:
        connection (obj): Connection object
        number (str): account number
        income (int): money to be added to the current account's balance
    """
    with connection as c:
        c.execute(ADD_INCOME, (income, number))


def delete_card(connection, number):
    """Delete card entity from the database."""
    with connection as c:
        c.execute(DELETE_CARD, (number,))
