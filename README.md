# Personal POS MVP (Beginner Friendly)

This is a **first MVP** for your personal Point-of-Sale app.

It focuses on:
- Product catalog
- Purchase recording (stock goes up)
- Sales recording (stock goes down)
- Inventory report
- AI-ready receipt analysis step (MVP rule-based parser for now)

## 1) What you are building

A POS typically does 4 core things:
1. Store products
2. Record purchases from suppliers
3. Record sales to customers
4. Track current inventory and simple reports

This project includes those core flows with a REST API.

---

## 2) Tech used

- **Python 3.11+**
- **FastAPI** for API
- **SQLite** for local database
- **Uvicorn** for local server

No cloud needed for this MVP.

---

## 3) Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open docs:
- http://127.0.0.1:8000/docs

---

## 4) Learning roadmap (for your first software)

### Step A — Understand the data model
Read `app/db.py` first. You will see:
- `products`
- `purchases` + `purchase_items`
- `sales` + `sale_items`
- inventory is derived from product stock columns

### Step B — Try basic API flow in Swagger
1. `POST /products`
2. `POST /purchases`
3. `POST /sales`
4. `GET /inventory/report`

### Step C — Understand receipt analysis
Use `POST /receipts/analyze` with OCR text. MVP parser extracts line items from simple patterns.

### Step D — Upgrade to real AI later
Replace `analyze_receipt_text` in `app/receipt_ai.py` with:
1. OCR provider (Tesseract/cloud)
2. LLM prompt -> strict JSON schema
3. manual review UI before final inventory update

---

## 5) Example cURL flow

### Create product
```bash
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Coke 330ml","sku":"COKE-330","cost_price":15,"sell_price":22,"stock_qty":0}'
```

### Add purchase (stock increases)
```bash
curl -X POST http://127.0.0.1:8000/purchases \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_name":"Local Supplier",
    "items":[{"product_id":1,"quantity":10,"unit_cost":15}]
  }'
```

### Record sale (stock decreases)
```bash
curl -X POST http://127.0.0.1:8000/sales \
  -H "Content-Type: application/json" \
  -d '{
    "items":[{"product_id":1,"quantity":2,"unit_price":22}]
  }'
```

### Inventory report
```bash
curl http://127.0.0.1:8000/inventory/report
```

---

## 6) Next MVP upgrades

- Add login/auth
- Add simple frontend dashboard (Next.js or React)
- Replace rule parser with OCR + LLM
- Add CSV export of reports
- Add low-stock alerts

You now have a strong base. Build slowly, test each feature, and keep commits small.
