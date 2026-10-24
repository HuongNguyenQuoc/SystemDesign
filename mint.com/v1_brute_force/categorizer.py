from models import Category

DEFAULT_SELLER_CATEGORY: dict[str, Category] = {
    "Exxon": Category.GAS,
    "Target": Category.SHOPPING,
    "BAAMF": Category.HOUSING,
    "Starbucks": Category.FOOD,
    "Amazon": Category.SHOPPING,
}

class Categorizer:
    def __init__(self, seller_category_mapping: dict[str, Category]):
        self._map = dict(seller_category_mapping)

    def categorize(self, seller: str) -> Category:
        return self._map.get(seller, Category.OTHER)

if __name__ == "__main__":
    c = Categorizer(DEFAULT_SELLER_CATEGORY)

    assert c.categorize("Exxon") == Category.GAS
    assert c.categorize("Target") == Category.SHOPPING
    assert c.categorize("BAAMF") == Category.HOUSING
    assert c.categorize("Unknown Seller") == Category.OTHER

    # Todo 3: in ra categorize("exxon") (chữ thường) và categorize(" Exxon "), xem ra gì
    print (c.categorize("exxon"))
    print (c.categorize(" Exxon "))

    print("categorizer OK")
