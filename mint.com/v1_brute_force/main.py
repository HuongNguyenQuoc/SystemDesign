from decimal import Decimal

from db import InMemoryDB
from fake_bank import FakeBank
from models import Category
from security import Encryptor, load_key
from categorizer import Categorizer, DEFAULT_SELLER_CATEGORY
from account_service import AccountService
from datetime import datetime
from budget_service import BudgetService

def main() -> None:
    db = InMemoryDB()
    bank = FakeBank()
    budget_service = BudgetService(db=db)

    service = AccountService(
        db=db,
        encryptor=Encryptor(load_key()),
        categorizer=Categorizer(DEFAULT_SELLER_CATEGORY),
        bank=bank
    )

    user = db.add_user(name="John Doe", monthly_income=Decimal("5000.00"))

    # Create two accounts at the fake bank.
    bank.open_account("john_vcb", "pw-vcb")
    bank.open_account("john_tcb", "pw-tcb")

    # Connecting imports each account's transactions immediately.
    vcb = service.connect_account(
        user_id=user.id,
        account_url="https://vcb.com",
        account_login="john_vcb",
        account_password="pw-vcb"
    )
    tcb = service.connect_account(
        user_id=user.id,
        account_url="https://tcb.com",
        account_login="john_tcb",
        account_password="pw-tcb"
    )

    transactions = db.get_transactions_by_user(user.id)

    assert len(transactions) == 40
    assert {tx.account_id for tx in transactions} == {vcb.id, tcb.id}
    assert any(tx.category == Category.OTHER for tx in transactions)

    for tx in sorted(transactions, key=lambda tx: tx.created_at):
        print(f"{tx.created_at.strftime('%Y-%m-%d %H:%M:%S')} | account={tx.account_id} | {tx.seller:10s} | {tx.amount:8.2f} | {tx.category.value}")

    # Sync again: existing transactions must not be duplicated.
    assert service.extract_transactions(vcb.id) == []
    assert service.extract_transactions(tcb.id) == []
    assert len(db.transactions) == 40

    # Simulate a new purchase, then sync.
    bank.simulate_purchase("john_vcb", "Grab", Decimal("3.50"))
    added = service.extract_transactions(vcb.id)

    assert len(added) == 1
    assert added[0].seller == "Grab"
    assert added[0].amount == Decimal("3.50")

    #Another sync must not important that purchase again.
    assert service.extract_transactions(vcb.id) == []
    assert len(db.transactions) == 41

    print(
        "\nOK: 40 initial transactions; repeated sync adds 0; "
        "new purchase adds 1."
    )

    # 1. Đặt ngân sách cho User
    # TODO: Đặt budget cho FOOD là 100.00 và SHOPPING là 200.00 bằng db.set_budget(...)
    db.set_budget(user_id=user.id, category=Category.FOOD, monthly_limit=Decimal("100.00"))
    db.set_budget(user_id=user.id, category=Category.SHOPPING, monthly_limit=Decimal("200.00"))

    # 2. Tính chi tiêu tháng hiện tại
    now = datetime.now()
    spending = budget_service.calculate_monthly_spending(user_id=user.id, year=now.year, month=now.month)
    print("\nMonthly spending by category:", spending)

    # 3. Kiểm tra cảnh báo ngân sách
    notifications = budget_service.check_budget(user_id=user.id, year=now.year, month=now.month)
    print("Budget notifications:", notifications)

    # 4. Demo User override category của 1 giao dịch
    # Lấy giao dịch đầu tiên và đổi sang Category khác
    tx_to_change = db.transactions[0]
    old_category = tx_to_change.category
    new_category = Category.OTHER if old_category != Category.OTHER else Category.FOOD

    budget_service.override_transaction_category(transaction_id=tx_to_change.id, new_category=new_category)
    assert tx_to_change.category == new_category
    print(f"\nOverride transaction category: {tx_to_change.id} from {old_category.value} to {new_category.value}")

    print("\nv1_brute_force demo completed successfully.")

if __name__ == "__main__":
    main()
