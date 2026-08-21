# E-commerce Project — Planning

## 1. Scope (what the project must do)

Sell products, organized by categories, with orders placed by authenticated users.
Each order can contain multiple products, with quantity and price locked at purchase time.

Language: entire project (code, naming, comments) in English.
Data: fake/manual data for development and testing (no external e-commerce API).

---

## 2. Big — Core Entities (nothing exists without these)

- [ ] `User` — who buys (and logs in)
- [ ] `Product` — what is sold
- [ ] `Category` — how products are grouped
- [ ] `Order` — a purchase made by a user

## 3. Big — Relationships between entities

- [ ] `User` → `Order` (1:N) — a user can have many orders
- [ ] `Product` ↔ `Category` (N:N) — via `ProductCategory`
- [ ] `Order` ↔ `Product` (N:N, enriched) — via `OrderItem`, carrying `quantity` and `price_at_purchase`

## 4. Big — Associative (intermediate) tables

- [ ] `ProductCategory` — simple link (product_id, category_id)
- [ ] `OrderItem` — enriched link (order_id, product_id, quantity, price_at_purchase)

---

## 5. Priority 1 — Must exist first (the skeleton)

- [ ] `User`: register, login (reuse JWT pattern from tarefas project)
- [ ] `Product`: create, list, update, delete
- [ ] `Category` + `ProductCategory`: assign product(s) to category(ies)
- [ ] `Order` + `OrderItem`: create an order with items

## 6. Priority 2 — Depends on Priority 1 existing

- [ ] Stock/business rule on purchase (what happens to stock when an order is created — needs a real DB-level solution for concurrent purchases, not just `async`)
- [ ] `role` field on `User` (customer / admin)
- [ ] Simple admin routes (e.g. list all orders) — no dashboard UI

## 7. Priority 3 — Polish (after the core works)

- [ ] Automated tests (planned per feature this time, not left for the end)
- [ ] README with setup instructions and structure
- [ ] Folder/module structure finalized and documented

---

## 8. Medium — Modules (to be filled in once Priority 1 entities are modeled)

- [ ] `models/` — one class per entity
- [ ] `routers/` — one file per resource (users, products, categories, orders)
- [ ] `schemas/` — request/response validation per resource
- [ ] `database/` — db connection, crud functions
- [ ] `core/` — security, JWT (reused pattern)

## 9. Small — To break down later, per module

- [ ] (to fill in once each medium module is started — mirrors the level of detail already used in the tarefas project's functions)

---

## 10. Open questions (capture as they come up — don't stop to resolve immediately)

-