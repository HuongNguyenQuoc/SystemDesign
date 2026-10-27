import datetime
from decimal import Decimal

from db import InMemoryDB
from fake_bank import FakeBank
from models import Account, Transaction, Category
from security import Encryptor, load_key
from categorizer import Categorizer, DEFAULT_SELLER_CATEGORY

class AccountService:
    def __init__(self, db: InMemoryDB, encryptor: Encryptor,
                    categorizer: Categorizer, bank: FakeBank):
        self._db = db
        self._encryptor = encryptor
        self._categorizer = categorizer
        self._bank = bank

    def connect_account(self, user_id: int, account_url: str,
                        account_login: str, account_password: str) -> Account:
        # TODO 1: mã hoá account_password bằng self._encryptor.encrypt(...)
        #         (TUYỆT ĐỐI không lưu plaintext password vào DB)
        encrypted_password = self._encryptor.encrypt(account_password)

        # TODO 2: lưu account vào self._db bằng add_account(...)
        account = self._db.add_account(user_id, account_url, account_login, account_password_encrypted = encrypted_password)

        # TODO 3: gọi self.extract_transactions(...) ngay lập tức cho account vừa tạo
        #         (Brute force v1: chạy đồng bộ ngay khi user bấm Connect)

        self.extract_transactions(account.id)
        return account

    def extract_transactions(self, account_id: int) -> list[Transaction]:
        # TODO 1: lấy account từ self._db. Nếu là None thì raise ValueError("Account not found")
        account = self._db.get_account(account_id)
        if account is None:
            raise ValueError("Account not found")

        # TODO 2: giải mã account.account_password_encrypted để lấy lại plaintext password
        plaintext_pw = self._encryptor.decrypt(account.account_password_encrypted)

        # TODO 3: gọi self._bank.fetch_transactions(...) với login, password vừa giải mã,
        #         và since=account.last_update
        bank_txs = self._bank.fetch_transactions(account.account_login, plaintext_pw, since=account.last_update)

        added_txs: list[Transaction] = []
        for btx in bank_txs:
            # TODO 4: kiểm tra trùng bằng self._db.has_transaction(account.id, btx.external_id)
            #         Nếu đã có rồi thì bỏ qua (continue)
            if self._db.has_transaction(account_id=account.id, external_id=btx.external_id):
                continue
            # TODO 5: phân loại seller bằng self._categorizer.categorize(btx.seller)
            category = self._categorizer.categorize(btx.seller)

            # TODO 6: lưu vào DB bằng self._db.add_transaction(...) rồi append vào added_txs
            tx = self._db.add_transaction(
                account_id=account.id,
                user_id=account.user_id,
                external_id=btx.external_id,
                created_at=btx.created_at,
                seller=btx.seller,
                amount=btx.amount,
                category=category
            )
            added_txs.append(tx)


        # TODO 7: cập nhật account.last_update thành thời điểm hiện tại (datetime.now())
        account.last_update = datetime.datetime.now()

        return added_txs

            
