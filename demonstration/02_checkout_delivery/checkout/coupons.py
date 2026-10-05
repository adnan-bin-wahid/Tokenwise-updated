from checkout.models import Coupon


class CouponService:
    """Coupons expire exactly at their deadline; minimum spend uses subtotal."""

    def __init__(self, coupons: dict[str, Coupon]):
        self.coupons = coupons

    def discount_percent(self, code: str, subtotal_cents: int, now: int) -> int:
        coupon = self.coupons.get(code)
        if coupon is None or now >= coupon.expires_at:
            return 0
        if subtotal_cents < coupon.minimum_cents or not 0 <= coupon.percent <= 100:
            return 0
        return coupon.percent
