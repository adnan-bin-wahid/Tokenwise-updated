# Checkout and Delivery

A local teaching application with expiring coupons, integer-cent pricing,
atomic stock reservation, and delivery estimates. No real payment is processed.

```powershell
py -3.12 app.py
py -3.12 -m unittest discover -s tests -v
```

Open this folder itself in Antigravity. Use `checkout/coupons.py` as the manual
baseline. Task: Explain coupon expiry, its effect on checkout totals, and the
tests for expiry and rounding. Do not modify any files.

Coupon validity, rounding, order coordination, and tests are separate modules.
Inventory and delivery provide working, potentially unrelated repository context.
