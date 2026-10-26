import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

SELLERS = [
    "Exxon", "Target", "BAAMF", "Starbucks", "Amazon",
    "Shell", "Grab", "Shopee", "Netflix"
]

@dataclass
class BankTransaction:
    external_id: str
    created_at: datetime
    seller: str
    amount: Decimal

class FakeBank:
    def __init__(self):
        self._passwords: dict[str, str] = {} #login -> password
        self._history: dict[str, list[BankTransaction]] = {} #login -> list of transactions

    def open_account(self, login: str, password: str, n_transactions: int = 20) -> None:
        rng = random.Random(login) # Seed fixed following login to data no change between runs
        now = datetime.now()
        history = []
        for i in range(n_transactions):
            tx = BankTransaction(
                external_id = f"txn_{i:04d}",
                created_at = now - timedelta(days=rng.randint(1, 60)),
                seller = rng.choice(SELLERS),
                amount = Decimal(rng.randint(100, 50000)) / 100
            )
            history.append(tx)

        # Sort history by created_at ascending
        history.sort(key=lambda tx: tx.created_at)

        self._passwords[login] = password
        self._history[login] = history

    def simulate_purchase(self, login: str, seller: str, amount: Decimal) -> None:
        """Giả lập user vừa quẹt thẻ: thêm 1 giao dịch mới tại thời điểm hiện tại."""
        if login not in self._history:
            raise ValueError(f"Account with login '{login}' not found. Please open an account first.")
        now = datetime.now()
        ext_id = f"txn_{len(self._history[login]):04d}"
        tx = BankTransaction(
            external_id=ext_id,
            created_at=now,
            seller=seller,
            amount=amount
        )
        self._history[login].append(tx)

    def fetch_transactions(self, login: str, password: str, since: datetime | None = None) -> list[BankTransaction]:
        if password != self._passwords[login]:
            raise PermissionError("Invalid login or password.")

        # 2. Return new list (avoid be modified in place)
        if since is None:
            return list(self._history[login])
        return [tx for tx in self._history[login] if tx.created_at >= since]

if __name__ == "__main__":
    bank = FakeBank()
    bank.open_account("john_vcb", "pw-vcb")
    bank.open_account("john_tcb", "pw-tcb")

    # TODO 1: fetch toàn bộ giao dịch của "john_vcb", in mỗi giao dịch 1 dòng
    txs_vcb = bank.fetch_transactions("john_vcb", "pw-vcb")
    for tx in txs_vcb:
        print(f"{tx.created_at.strftime('%Y-%m-%d %H:%M:%S')} | {tx.seller:10s} | {tx.amount}")

    # TODO 2: assert fetch 2 lần liên tiếp ra cùng 1 list
    assert txs_vcb == bank.fetch_transactions("john_vcb", "pw-vcb")

    # TODO 3: assert có ít nhất 1 seller không nằm trong DEFAULT_SELLER_CATEGORY
    from categorizer import DEFAULT_SELLER_CATEGORY
    assert any(tx.seller not in DEFAULT_SELLER_CATEGORY for tx in txs_vcb)

    # TODO 4: fetch với since = 7 ngày trước, assert mọi tx đều >= since
    since_7d = datetime.now() - timedelta(days=7)
    txs_since_7d = bank.fetch_transactions("john_vcb", "pw-vcb", since=since_7d)
    assert all(tx.created_at >= since_7d for tx in txs_since_7d)

    # TODO 5: simulate_purchase rồi fetch với since = 1 phút trước, phải ra đúng 1 tx
    bank.simulate_purchase("john_vcb", "Grab", Decimal("3.50"))
    since_1m = datetime.now() - timedelta(minutes=1)
    new_txs = bank.fetch_transactions("john_vcb", "pw-vcb", since=since_1m)
    assert len(new_txs) == 1
    assert new_txs[0].seller == "Grab"
    assert new_txs[0].amount == Decimal("3.50")

    # TODO 6: fetch với password sai, bắt PermissionError
    try:
        bank.fetch_transactions("john_vcb", "wrong-password")
        assert False, "Expected ValueError for wrong password"
    except PermissionError:
        print("Caught expected PermissionError for wrong password.")

    # TODO 7: in external_id đầu tiên của 2 ngân hàng khác nhau
    txs_tcb = bank.fetch_transactions("john_tcb", "pw-tcb")
    print(f"First transaction external_id for john_vcb: {txs_vcb[0].external_id}")
    print(f"First transaction external_id for john_tcb: {txs_tcb[0].external_id}")

    print("fake_bank OK")