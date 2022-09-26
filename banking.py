import math
import random

import database


DB_FILEPATH = 'card.s3db'


class BankingSystem:
    """Represents a simple banking system."""

    MENU = """
    \r1. Create an account
    \r2. Log into account
    \r0. Exit"""

    def __init__(self, db_filepath='database.s3db'):
        """Initialize a banking system by connecting to database."""
        self.connection = database.connect(db_filepath)
        database.create_table(self.connection)

    def menu(self):
        """Show banking system's main menu."""
        while True:
            print(BankingSystem.MENU)

            # Choose an action
            action = input()

            # Execute an action
            if action == '0':
                # Exit the system
                print('\nBye!')
                exit()
            elif action == '1':
                # Create an account
                self.create_account()
            elif action == '2':
                # Log into an account
                self.login()
            else:
                raise NotImplementedError

    def create_account(self):
        """Create a new account and add it to the system's database."""
        # Initialize a new Account object
        account = Account.new()

        # Add the card to database
        database.add_card(
            self.connection, number=account.number, pin=account.pin
        )

    def login(self):
        """Log into an account."""
        print('\nEnter your card number:')
        card_num_inp = input()

        print('Enter your PIN:')
        pin_inp = input()

        row = database.get_card_by_number(self.connection, card_num_inp)

        # Check credentials
        if not row:
            print('\nWrong card number or PIN!')
        else:
            card_num, pin, balance = row[0]
            if pin_inp != pin:
                print('\nWrong card number or PIN!')
            else:
                print('\nYou have successfully logged in!')

                account = Account(card_num, pin, balance, self.connection)
                account.menu()


class Account:
    """Represents user's bank account."""

    MENU = """
    \r1. Balance
    \r2. Add income
    \r3. Do transfer
    \r4. Close account
    \r5. Log out
    \r0. Exit"""

    __issuer_num = '400000'

    def __init__(self, number, pin, balance, connection=None):
        self.number = number
        self.pin = pin
        self.balance = balance
        self.connection = connection

    @classmethod
    def new(cls):
        """Create a new account."""
        account = cls(
            number=cls._get_account_num(),
            pin=cls._get_pin(),
            balance=0
        )

        print('\nYour card has been created')
        print(f'Your card number:\n{account.number}')
        print(f'Your card PIN:\n{account.pin}')

        return account

    @staticmethod
    def _get_account_num():
        """Set account number using Luhn algorithm."""
        # Set account identifier
        account_id = ''.join([str(random.randint(0, 9)) for _ in range(9)])

        # Set Bank Identification Number and Account Identifier
        num = Account.__issuer_num + account_id

        # Find checksum
        new_num = []
        for i, digit in enumerate(num, start=1):
            if i % 2 == 1:
                new_digit = int(digit) * 2
                if new_digit > 9:
                    new_digit -= 9
                new_num.append(str(new_digit))
            else:
                new_num.append(digit)

        sum_new_num = sum(map(int, new_num))

        checksum = math.ceil(sum_new_num / 10)
        checksum = checksum * 10 - sum_new_num

        new_num = num + str(checksum)

        return new_num

    @staticmethod
    def _get_pin():
        """Set 4-digit card PIN."""
        pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return pin

    def menu(self):
        """Show account's menu."""
        while True:
            # Show account menu
            print(Account.MENU)

            # Choose account action
            action = input()

            # Execute account action
            if action == '0':
                # Exit the banking system
                print('\nBye!')
                exit()
            elif action == '1':
                # Show balance
                print(f'\nBalance: {self.balance}')
            elif action == '2':
                # Get income
                income = int(input('\nEnter income:\n'))

                # Add income to the account
                self.add_income(self.connection, income)
                print('Income was added!')
            elif action == '3':
                print('\nTransfer')

                # Get receiver
                receiver = input('Enter card number:\n')

                # Transfer money
                self.transfer_money(receiver)
            elif action == '4':
                # Close the account
                self.delete_account()
            elif action == '5':
                print('\nYou have successfully logged out!')
                break
            else:
                raise NotImplementedError

    def add_income(self, connection, income):
        """Deposit money to the account.

        Arguments:
            connection (obj): database connection handle
            income (int): money to be added to the current balance
        """
        database.add_income(connection, self.number, income)
        self.balance += income

    def transfer_money(self, receiver):
        """Transfer money to another account.

        Operation will be executed unless the following circumstances occur:
            - user tries to transfer more money than they have,
            - user tries to transfer money to the same account,
            - receiver's card number doesn't pass Luhn algorithm,
            - receiver's card number doesn't exist.

        Args:
            receiver (str): receiver's bank account number
        """
        if receiver == self.number:
            print('You can\'t transfer money to the same account!')
        elif not is_card_number_valid(receiver):
            print('Probably you made a mistake in the card number. '
                  'Please try again!')
        elif not do_card_number_exists(self.connection, receiver):
            print('Such a card does not exist.')
        else:
            # Get the amount of money to be transferred
            amount = int(input('\nEnter how much money you want to transfer:\n'))

            # Check if such amount is available
            if amount <= self.balance:
                # Delete amount from user account
                database.add_income(self.connection, self.number, -amount)
                self.balance -= amount

                # Add amount to the receiver account
                database.add_income(self.connection, receiver, amount)

                print('Success!')
            else:
                print('Not enough money!')

    def delete_account(self):
        """Delete the account from the database."""
        database.delete_card(self.connection, self.number)


def is_card_number_valid(number):
    """Check that the card number passes Luhn algorithm."""
    new_number = []
    for i, digit in enumerate(number[:-1], start=1):
        if i % 2 == 1:
            new_digit = int(digit) * 2
            if new_digit > 9:
                new_digit -= 9
            new_number.append(str(new_digit))
        else:
            new_number.append(digit)

    sum_new_number = sum(map(int, new_number))
    total = sum_new_number + int(number[-1])

    return True if total % 10 == 0 else False


def do_card_number_exists(connection, number):
    """Check that the card number exists in a database.

    Args:
        connection (obj): Connection object
        number (str): card number to be checked

    Returns:
        bool: True if card number exists in the database, False otherwise
    """
    result = database.get_card_by_number(connection, number)

    return False if result == [] else True


banking_system = BankingSystem(DB_FILEPATH)
banking_system.menu()