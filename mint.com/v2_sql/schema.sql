-- Bật kiểm tra khóa ngoại (Foreign Keys) trong SQLite
PRAGMA foreign_keys = ON;

-- 1. Bảng users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    monthly_income TEXT NOT NULL  -- Lưu số tiền dưới dạng TEXT để map chuẩn với Python Decimal
);

-- 2. Bảng accounts
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_url TEXT NOT NULL,
    account_login TEXT NOT NULL,
    account_password_encrypted TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_update TEXT,
    -- TODO 1: Khóa ngoại user_id tham chiếu tới users(id) ON DELETE CASCADE
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Bảng transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    external_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    seller TEXT NOT NULL,
    amount TEXT NOT NULL,       -- Lưu dạng TEXT để giữ độ chính xác Decimal
    category TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- TODO 2: Ràng buộc UNIQUE để chống trùng lặp giao dịch ở cấp độ database.
    -- Một tài khoản không được có 2 giao dịch trùng external_id.
    UNIQUE (account_id, external_id)
);

-- 4. Bảng budgets
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    monthly_limit TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- TODO 3: Mỗi user chỉ có tối đa 1 budget cho mỗi category.
    -- Tạo ràng buộc UNIQUE cho cặp nào?
    UNIQUE (user_id, category)
);

-- ============================================================================
-- INDEXES (CHỈ MỤC) - Trọng tâm của Bước 4
-- ============================================================================

-- Index 1: Tìm account theo user_id
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);

-- TODO 4: Khi tính chi tiêu theo tháng (budget_service), ta thường query:
-- SELECT ... FROM transactions WHERE user_id = ? AND created_at >= ? AND created_at <= ?
-- Hãy tạo một Composite Index (chỉ mục kết hợp) trên bảng transactions gồm 2 cột: user_id và created_at
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, created_at);
