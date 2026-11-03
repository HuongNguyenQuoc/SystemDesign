from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from models import Category, User

class CreateUseRequest(BaseModel):
    name: str = Field(..., min_length=1, examples=["Huong"])
    monthly_income: Decimal = Field(..., gt=0, examples=[5000.00])

class UserResponse(BaseModel):
    id: int
    name: str
    monthly_income: Decimal

class ConnectAccountRequest(BaseModel):
    user_id: int
    account_url: str = Field(..., examples=["https://vcb.com"])
    account_login: str = Field(..., examples=["john_vcb"])
    account_password: str = Field(..., examples=["pw-vcb"])

class AccountResponse(BaseModel):
    id: int
    user_id: int
    account_url: str
    account_login: str
    created_at: datetime
    last_update: datetime | None

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    user_id: int
    external_id: str
    created_at: datetime
    seller: str
    amount: Decimal
    category: Category

class OverrideTransactionCategoryRequest(BaseModel):
    new_category: Category

class SetBudgetRequest(BaseModel):
    user_id: int
    category: Category
    monthly_limit: Decimal = Field(..., gt=0, examples=[200.00])

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: Category
    monthly_limit: Decimal

class MonthlySpendingResponse(BaseModel):
    user_id: int
    year: int
    month: int
    spending_by_category: dict[Category, Decimal]
    notifications: list[str]
