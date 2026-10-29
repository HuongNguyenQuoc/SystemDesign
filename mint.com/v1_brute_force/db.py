from datetime import datetime
from decimal import Decimal

from models import User, Account, Transaction, Category, Budget

class InMemoryDB:

    def __init__(self):
        self.users: list[User] = []
        self.accounts: list[Account] = []
        self.transactions: list[Transaction] = []
        self.budgets: list[Budget] = []
        self._next_id = 1

    def _new_id(self) -> int:
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def add_user(self, name: str, monthly_income: Decimal) -> User:
        user = User(id=self._new_id(), name=name, monthly_income=monthly_income)
        self.users.append(user)
        return user

    def add_account(self, user_id: int, account_url: str, account_login: str, account_password_encrypted: str) -> Account:
        account = Account(
            id=self._new_id(),
            user_id=user_id,
            account_url=account_url,
            account_login=account_login,
            account_password_encrypted=account_password_encrypted
        )
        self.accounts.append(account)
        return account

    def get_account(self, account_id: int) -> Account | None:
        for account in self.accounts:
            if account.id == account_id:
                return account
        return None

    def add_transaction(self, account_id: int, user_id: int,
                        external_id: str, created_at: datetime, seller: str,
                        amount: Decimal, category: Category = Category.OTHER) -> Transaction:
        transactions = Transaction(
            id=self._new_id(),
            account_id=account_id,
            user_id=user_id,
            external_id=external_id,
            created_at=created_at,
            seller=seller,
            amount=amount,
            category=category
        )
        self.transactions.append(transactions)
        return transactions

    def has_transaction(self, account_id: int, external_id: str) -> bool:
        for transaction in self.transactions:
            if transaction.account_id == account_id and transaction.external_id == external_id:
                return True
        return False

    def get_transactions_by_user(self, user_id: int) -> list[Transaction]:
        return [t for t in self.transactions if t.user_id == user_id]

    def get_user(self, user_id: int) -> User | None:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def update_transaction_category(self, transaction_id: int, new_category: Category) -> Transaction | None:
        for transaction in self.transactions:
            if transaction.id == transaction_id:
                transaction.category = new_category
                return transaction
        return None

    def set_budget(self, user_id: int, category: Category, monthly_limit: Decimal) -> Budget:
        # Nếu user đã có budget cho category này rồi thì cập nhật lại monthly_limit (override)
        for budget in self.budgets:
            if budget.user_id == user_id and budget.category == category:
                budget.monthly_limit = monthly_limit
                return budget
        # Nếu chưa có thì tạo mới và thêm vào self.budgets
        budget = Budget(
            id=self._new_id(),
            user_id=user_id,
            category=category,
            monthly_limit=monthly_limit
        )
        self.budgets.append(budget)
        return budget

    def get_budget_by_user(self, user_id: int) -> list[Budget]:
        return [b for b in self.budgets if b.user_id == user_id]

if __name__ == "__main__":
    db = InMemoryDB()

    user = db.add_user(name="John Doe", monthly_income=Decimal("5000.00"))

    account1 = db.add_account(
        user_id=user.id,
        account_url="https://example.com/account1",
        account_login="johndoe1",
        account_password_encrypted="encrypted_password1"
    )

    account2 = db.add_account(
        user_id=user.id,
        account_url="https://example.com/account2",
        account_login="johndoe2",
        account_password_encrypted="encrypted_password2"
    )

    transaction1_1 = db.add_transaction(
        account_id=account1.id,
        user_id=user.id,
        external_id="txn_123456",
        created_at=datetime(2026, 9, 28),
        seller="Amazon",
        amount=Decimal("99.99"),
        category=Category.SHOPPING
    )

    transaction1_2 = db.add_transaction(
        account_id=account1.id,
        user_id=user.id,
        external_id="txn_123457",
        created_at=datetime(2026, 9, 28),
        seller="Starbucks",
        amount=Decimal("5.99"),
        category=Category.FOOD
    )

    transaction2 = db.add_transaction(
        account_id=account2.id,
        user_id=user.id,
        external_id="txn_223456",
        created_at=datetime(2026, 9, 28),
        seller="Shell",
        amount=Decimal("45.00"),
        category=Category.GAS
    )

    print(f"Transactions for user {user.name}: {db.get_transactions_by_user(user.id)}")
    print(f"Does user {user.name} have transaction with external_id 'txn_123456' in account1? {db.has_transaction(account1.id, 'txn_123456')}")
    print(f"Does user {user.name} have transaction with external_id 'txn_999999' in account1? {db.has_transaction(account1.id, 'txn_999999')}")
    print(f"Does have account with id '999'? {db.get_account(999) is not None}")