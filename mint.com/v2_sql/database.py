import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from models import User, Account, Transaction, Category, Budget

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

class Database:
    def __init__(self, db_path: str = "mint.db"):
        # Kết nối tới database (nếu truyền ":memory:" thì chạy trên RAM để test)
        self.conn = sqlite3.connect(db_path)
        # Giúp truy cập các cột của row theo tên: row["name"] thay vì row[0]
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def add_user(self, name: str, monthly_income: Decimal) -> User:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, monthly_income) VALUES (?, ?)",
            (name, str(monthly_income))
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve the new user's ID")
        return User(id=cursor.lastrowid, name=name, monthly_income=monthly_income)

    def add_account(self, user_id: int, account_url: str, account_login: str, account_password_encrypted: str) -> Account:
        cursor = self.conn.cursor()
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO accounts (user_id, account_url, account_login, account_password_encrypted, created_at, last_update) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, account_url, account_login, account_password_encrypted, now.isoformat(), None)
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve the new account's ID")
        return Account(
            id=cursor.lastrowid,
            user_id=user_id,
            account_url=account_url,
            account_login=account_login,
            account_password_encrypted=account_password_encrypted,
            created_at=now,
            last_update=None
        )

    def get_account(self, account_id: int) -> Account | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM accounts WHERE id = ?
            """, (account_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Account(
            id=row["id"],
            user_id=row["user_id"],
            account_url=row["account_url"],
            account_login=row["account_login"],
            account_password_encrypted=row["account_password_encrypted"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_update=datetime.fromisoformat(row["last_update"]) if row["last_update"] else None
        )

    def update_account_last_update(self, account_id: int, last_update: datetime) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE accounts SET last_update = ? WHERE id = ?
            """,
            (last_update.isoformat(), account_id)
        )
        self.conn.commit()

    def has_transactions(self, account_id: int, external_id: str) -> bool:
        """
        TODO 1: Kiểm tra xem giao dịch đã tồn tại chưa.
        Gợi ý: Viết SELECT 1 FROM transactions WHERE account_id = ? AND external_id = ?
        Trả về True nếu fetchone() có kết quả, ngược lại False.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM transactions WHERE account_id = ? AND external_id = ?
            """,
            (account_id, external_id)
        )
        return cursor.fetchone() is not None

    def add_transaction(self, account_id: int, user_id: int, external_id: str,
                    created_at: datetime, seller: str, amount: Decimal,
                    category: Category = Category.OTHER) -> Transaction:
        cursor = self.conn.cursor()
        # TODO 2: Thực thi INSERT INTO transactions (...) VALUES (...)
        cursor.execute(
            """
            INSERT INTO transactions (account_id, user_id, external_id, created_at, seller, amount, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (account_id, user_id, external_id, created_at.isoformat(), seller, str(amount), category.value)
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve the new transaction's ID")
        return Transaction(
            id=cursor.lastrowid,
            account_id=account_id,
            user_id=user_id,
            external_id=external_id,
            created_at=created_at,
            seller=seller,
            amount=amount,
            category=category
        )

    def get_transactions_by_user(self, user_id: int) -> list[Transaction]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM transactions WHERE user_id = ?
            """,
            (user_id,)
        )
        return [
            Transaction(
                id=row["id"],
                account_id=row["account_id"],
                user_id=row["user_id"],
                external_id=row["external_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                seller=row["seller"],
                amount=Decimal(row["amount"]),
                category=Category(row["category"])
            )
            for row in cursor.fetchall()
        ]

    def update_transaction_category(self, transaction_id: int, new_category: Category) -> bool:
        cursor = self.conn.cursor()
        # TODO 3: Thực thi UPDATE transactions SET category = ? WHERE id = ?
        cursor.execute(
            """
            UPDATE transactions SET category = ? WHERE id = ?
            """,
            (new_category.value, transaction_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def set_budget(self, user_id: int, category: Category, monthly_limit: Decimal) -> Budget:
        cursor = self.conn.cursor()
        # TODO 4: Thực thi INSERT INTO budgets (...) VALUES (...)
        cursor.execute(
            """
            INSERT INTO budgets (user_id, category, monthly_limit)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """,
            (user_id, category.value, str(monthly_limit))
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve the new budget's ID")
        return Budget(
            id=cursor.lastrowid,
            user_id=user_id,
            category=category,
            monthly_limit=monthly_limit
        )

    def get_budget_by_user(self, user_id: int) -> list[Budget]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM budgets WHERE user_id = ?
            """,
            (user_id,)
        )
        return [
            Budget(
                id=row["id"],
                user_id=row["user_id"],
                category=Category(row["category"]),
                monthly_limit=Decimal(row["monthly_limit"])
            )
            for row in cursor.fetchall()
        ]

if __name__ == "__main__":
    # Test nhanh bằng database trong RAM
    db = Database(db_path=":memory:")
    user = db.add_user(name="Alice", monthly_income=Decimal("5000.00"))
    acc = db.add_account(user_id=user.id, account_url="https://bank.com/alice", account_login="alice123", account_password_encrypted="encrypted_password")

    # Test add transaction
    tx = db.add_transaction(
        account_id=acc.id,
        user_id=user.id,
        external_id="tx123",
        created_at=datetime.now(),
        seller="Coffee Shop",
        amount=Decimal("4.50"),
        category=Category.FOOD
    )

    assert db.has_transactions(account_id=acc.id, external_id="tx123") is True
    assert db.has_transactions(account_id=acc.id, external_id="tx999") is False

    # Test UPSERT Budget
    b1 = db.set_budget(user.id, Category.FOOD, Decimal("200.00"))
    b2 = db.set_budget(user.id, Category.FOOD, Decimal("250.00"))  # Update existing budget
    budgets = db.get_budget_by_user(user.id)

    assert len(budgets) == 1
    assert budgets[0].monthly_limit == Decimal("250.00")

    print("All tests passed.")
