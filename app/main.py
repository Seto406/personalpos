from fastapi import FastAPI, HTTPException

from app.db import get_conn, init_db
from app.receipt_ai import analyze_receipt_text
from app.schemas import (
    ProductCreate,
    ProductOut,
    PurchaseCreate,
    SaleCreate,
    ReceiptAnalyzeIn,
    ReceiptAnalyzeOut,
)

app = FastAPI(title="Personal POS MVP", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/products", response_model=ProductOut)
def create_product(payload: ProductCreate):
    with get_conn() as conn:
        try:
            cur = conn.execute(
                """
                INSERT INTO products(name, sku, cost_price, sell_price, stock_qty)
                VALUES (?, ?, ?, ?, ?)
                """,
                (payload.name, payload.sku, payload.cost_price, payload.sell_price, payload.stock_qty),
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not create product: {exc}")

        product_id = cur.lastrowid
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row)


@app.get("/products", response_model=list[ProductOut])
def list_products():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@app.post("/purchases")
def create_purchase(payload: PurchaseCreate):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Purchase requires at least one item")

    with get_conn() as conn:
        purchase_cur = conn.execute(
            "INSERT INTO purchases(supplier_name) VALUES (?)", (payload.supplier_name,)
        )
        purchase_id = purchase_cur.lastrowid

        total_cost = 0.0
        for item in payload.items:
            row = conn.execute("SELECT * FROM products WHERE id = ?", (item.product_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

            conn.execute(
                """
                INSERT INTO purchase_items(purchase_id, product_id, quantity, unit_cost)
                VALUES (?, ?, ?, ?)
                """,
                (purchase_id, item.product_id, item.quantity, item.unit_cost),
            )
            conn.execute(
                "UPDATE products SET stock_qty = stock_qty + ? WHERE id = ?",
                (item.quantity, item.product_id),
            )
            total_cost += item.quantity * item.unit_cost

        return {
            "purchase_id": purchase_id,
            "supplier_name": payload.supplier_name,
            "total_cost": round(total_cost, 2),
            "items_count": len(payload.items),
        }


@app.post("/sales")
def create_sale(payload: SaleCreate):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Sale requires at least one item")

    with get_conn() as conn:
        sale_cur = conn.execute("INSERT INTO sales DEFAULT VALUES")
        sale_id = sale_cur.lastrowid

        total_revenue = 0.0
        for item in payload.items:
            row = conn.execute("SELECT * FROM products WHERE id = ?", (item.product_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            if row["stock_qty"] < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product {item.product_id}. Available: {row['stock_qty']}",
                )

            conn.execute(
                """
                INSERT INTO sale_items(sale_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                (sale_id, item.product_id, item.quantity, item.unit_price),
            )
            conn.execute(
                "UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?",
                (item.quantity, item.product_id),
            )
            total_revenue += item.quantity * item.unit_price

        return {
            "sale_id": sale_id,
            "total_revenue": round(total_revenue, 2),
            "items_count": len(payload.items),
        }


@app.get("/inventory/report")
def inventory_report():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, name, sku, cost_price, sell_price, stock_qty,
                   ROUND(stock_qty * cost_price, 2) AS inventory_value
            FROM products
            ORDER BY name
            """
        ).fetchall()

    items = [dict(r) for r in rows]
    total_value = round(sum(i["inventory_value"] for i in items), 2)
    return {"items": items, "total_inventory_value": total_value}


@app.post("/receipts/analyze", response_model=ReceiptAnalyzeOut)
def analyze_receipt(payload: ReceiptAnalyzeIn):
    return analyze_receipt_text(payload.ocr_text)
