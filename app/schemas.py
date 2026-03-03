from pydantic import BaseModel, Field
from typing import List


class ProductCreate(BaseModel):
    name: str
    sku: str
    cost_price: float = Field(gt=0)
    sell_price: float = Field(gt=0)
    stock_qty: int = Field(ge=0, default=0)


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    cost_price: float
    sell_price: float
    stock_qty: int


class PurchaseItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_cost: float = Field(gt=0)


class PurchaseCreate(BaseModel):
    supplier_name: str
    items: List[PurchaseItemIn]


class SaleItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class SaleCreate(BaseModel):
    items: List[SaleItemIn]


class ReceiptAnalyzeIn(BaseModel):
    ocr_text: str


class ParsedReceiptItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    line_total: float


class ReceiptAnalyzeOut(BaseModel):
    supplier_name: str | None
    items: List[ParsedReceiptItem]
    subtotal: float
    estimated_tax: float
    grand_total: float
    confidence: float
    warnings: List[str]
