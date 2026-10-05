from checkout.coupons import CouponService
from checkout.inventory import Inventory
from checkout.models import Coupon, Item
from checkout.orders import OrderService
from delivery import delivery_days


def main() -> None:
    coupons = CouponService({"WELCOME10": Coupon("WELCOME10", 10, 1000)})
    order = OrderService(coupons, Inventory({"BOOK": 5}))
    print("Before coupon expiry:", order.checkout([Item("BOOK", 10000, 1)], "WELCOME10", 999))
    print("At coupon expiry:", order.checkout([Item("BOOK", 10000, 1)], "WELCOME10", 1000))
    print("Regional delivery days:", delivery_days("regional"))


if __name__ == "__main__":
    main()
