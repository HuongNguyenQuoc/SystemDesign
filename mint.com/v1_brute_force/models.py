from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum

class Category(Enum):
    HOUSING = "housing"
    FOOD = "food"
    GAS = "gas"
    SHOPPING = "shopping"
    OTHER = "other"

@dataclass
class User:
    id: int
    name: str
    monthly_income: Decimal

@dataclass
class Account:
    id: int
    user_id: int
    account_url: str
    account_login: str
    account_password_encrypted: str
    last_update: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Transaction:
    id: int
    account_id: int
    user_id: int
    external_id: str
    created_at: datetime
    seller: str
    amount: Decimal
    category: Category = Category.OTHER

if __name__ == "__main__":
    user = User(id=1, name="John Doe", monthly_income=Decimal("5000.00"))
    account = Account(
        id=1,
        user_id=user.id,
        account_url="https://example.com/account",
        account_login="johndoe",
        account_password_encrypted="encrypted_password",
    )
    transaction = Transaction(
        id=1,
        account_id=account.id,
        user_id=user.id,
        external_id="txn_123456",
        created_at=datetime.now(),
        seller="Amazon",
        amount=Decimal("99.99"),
        category=Category.SHOPPING
    )
    print(user)
    print(account)
    print(transaction)