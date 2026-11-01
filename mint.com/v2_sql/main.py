import time
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from database import Database
from fake_bank import FakeBank
from models import Category
from security import Encryptor, load_key
from categorizer import Categorizer, DEFAULT_SELLER_CATEGORY
from account_service import AccountService
from budget_service import BudgetService

DB_FILE = Path(__file__).resolve().parent / "mint.db"

def run_demo() -> None:
    # Xóa file mint.db cũ (nếu có) để mỗi lần chạy demo là trạng thái sạch
    if DB_FILE.exists():
        DB_FILE.unlink()

    # TODO 1: Khởi tạo Database với đường dẫn str(DB_FILE)
    db = Database(db_path=str(DB_FILE))
    bank = FakeBank()
    budget_service = BudgetService(db=db)

    service = AccountService(
        db=db,
        encryptor=Encryptor(load_key()),
        categorizer=Categorizer(DEFAULT_SELLER_CATEGORY),
        bank=bank,
    )

    user = db.add_user(name="John Doe", monthly_income=Decimal("5000.00"))

    bank.open_account("john_vcb", "pw-vcb")
    bank.open_account("john_tcb", "pw-tcb")

    vcb = service.connect_account(
        user_id=user.id,
        account_url="https://vcb.com",
        account_login="john_vcb",
        account_password="pw-vcb",
    )
    tcb = service.connect_account(
        user_id=user.id,
        account_url="https://tcb.com",
        account_login="john_tcb",
        account_password="pw-tcb",
    )

    transactions = db.get_transactions_by_user(user.id)
    assert len(transactions) == 40

    # Sync lại: không được nhân đôi giao dịch
    assert service.extract_transactions(vcb.id) == []
    assert service.extract_transactions(tcb.id) == []

    # Quẹt thẻ mới 1 giao dịch rồi sync
    bank.simulate_purchase("john_vcb", "Grab", Decimal("3.50"))
    added = service.extract_transactions(vcb.id)
    assert len(added) == 1
    assert len(db.get_transactions_by_user(user.id)) == 41

    # Đặt ngân sách (UPSERT)
    db.set_budget(
        user_id=user.id, category=Category.FOOD, monthly_limit=Decimal("100.00")
    )
    db.set_budget(
        user_id=user.id, category=Category.SHOPPING, monthly_limit=Decimal("200.00")
    )

    now = datetime.now()
    spending = budget_service.calculate_monthly_spending(
        user_id=user.id, year=now.year, month=now.month
    )
    notifications = budget_service.check_budget(
        user_id=user.id, year=now.year, month=now.month
    )

    print("Monthly spending:", spending)
    print("Notifications:", notifications)

    # Override category của giao dịch đầu tiên
    tx_to_change = transactions[0]
    new_cat = (
        Category.OTHER if tx_to_change.category != Category.OTHER else Category.FOOD
    )
    # TODO 2: Gọi budget_service.override_transaction_category(...)
    ok = budget_service.override_transaction_category(transaction_id=tx_to_change.id, new_category=new_cat)
    assert ok is True

    print("Demo v2_sql passed! File mint.db đã được lưu trên đĩa cứng.\n")


def run_benchmark() -> None:
    print("--- BẮT ĐẦU BENCHMARK: FULL SCAN vs COMPOSITE B-TREE INDEX ---")
    db = Database(db_path=":memory:")
    user = db.add_user("BenchUser", Decimal("10000.00"))
    acc = db.add_account(user.id, "https://mb.com", "mb_user", "enc_pw")

    # Sinh 20,000 giao dịch trải đều trong 2 năm (730 ngày)
    now = datetime(2026, 10, 15)
    rows = [
        (
            acc.id,
            user.id,
            f"bench_{i}",
            (now - timedelta(days=i % 730)).isoformat(),
            "Starbucks",
            "10.00",
            "food",
        )
        for i in range(20_000)
    ]
    db.conn.executemany(
        "INSERT INTO transactions (account_id, user_id, external_id, created_at, seller, amount, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    db.conn.commit()

    total_v1 = Decimal("0.00")
    total_v2 = Decimal("0.00")

    # 1. Đo kiểu cũ (Kéo toàn bộ 20,000 giao dịch lên RAM rồi dùng vòng lặp Python lọc tháng 10/2026)
    t0 = time.perf_counter()
    for _ in range(20):
        all_txs = db.get_transactions_by_user(user.id)
        total_v1 = sum(
            tx.amount
            for tx in all_txs
            if tx.created_at.year == 2026 and tx.created_at.month == 10
        )
    time_full_scan_ms = (time.perf_counter() - t0) / 20 * 1000

    # 2. Đo kiểu mới (Lọc trực tiếp qua B-Tree Index idx_transactions_user_date)
    budget_service = BudgetService(db)
    t0 = time.perf_counter()
    for _ in range(20):
        # TODO 3: Gọi budget_service.calculate_monthly_spending cho user.id, năm 2026, tháng 10
        spending_v2 = budget_service.calculate_monthly_spending(user_id=user.id, year=2026, month=10)
        total_v2 = spending_v2.get(Category.FOOD, Decimal("0.00"))
    time_index_ms = (time.perf_counter() - t0) / 20 * 1000

    assert total_v1 == total_v2
    print(f"1. Full Scan (20,000 rows)      : {time_full_scan_ms:6.2f} ms / query")
    print(f"2. B-Tree Index (user_id, date) : {time_index_ms:6.2f} ms / query")
    print(
        f"=> Tốc độ tăng gấp              : {time_full_scan_ms / time_index_ms:.1f}x lần!"
    )


if __name__ == "__main__":
    run_demo()
    run_benchmark()
