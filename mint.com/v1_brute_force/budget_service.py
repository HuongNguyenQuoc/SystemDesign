from decimal import Decimal
from collections import defaultdict
from models import Transaction, Budget, Category
from db import InMemoryDB

class BudgetService:
    def __init__(self, db: InMemoryDB):
        self._db = db

    def calculate_monthly_spending(self, user_id: int, year: int, month: int) -> dict[Category, Decimal]:
        spending: dict[Category, Decimal] = defaultdict(lambda: Decimal("0.00"))
        user_txs = self._db.get_transactions_by_user(user_id=user_id)

        for tx in user_txs:
            if tx.created_at.year == year and tx.created_at.month == month:
                spending[tx.category] += tx.amount

        return dict(spending)

    def check_budget(self, user_id: int, year: int, month: int) -> list[str]:
        spending = self.calculate_monthly_spending(user_id=user_id, year=year, month=month)
        budgets = self._db.get_budget_by_user(user_id=user_id)

        notifications: list[str] = []
        for budget in budgets:
            spent_amount = spending.get(budget.category, Decimal("0.00"))
            if spent_amount > budget.monthly_limit:
                notifications.append(
                    f"Budget exceeded for category {budget.category.value}: spent {spent_amount} exceeds limit {budget.monthly_limit}"
                )
        return notifications

    def override_transaction_category(self, transaction_id: int, new_category: Category) -> Transaction | None:
        """
        User chủ động sửa category cho một giao dịch cụ thể.
        """
        # TODO 4: Gọi hàm update_transaction_category của self._db
        updated_transaction = self._db.update_transaction_category(transaction_id=transaction_id, new_category=new_category)
        return updated_transaction
