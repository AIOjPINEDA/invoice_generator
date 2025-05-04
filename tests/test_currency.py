import database as db

def test_currency_function():
    print("=== TESTING CURRENCY FUNCTION ===")

    # Test the exact value from the database
    country = "EEUU"
    result = db.get_currency_for_country(country)
    print(f"Country: '{country}'")
    print(f"Currency result: {result}")
    print(f"Symbol: {result['symbol']}")
    print()

    # Test with a different format just to be sure
    country2 = "USA"
    result2 = db.get_currency_for_country(country2)
    print(f"Country: '{country2}'")
    print(f"Currency result: {result2}")
    print(f"Symbol: {result2['symbol']}")
    print()

    # Test with a non-US country
    country3 = "España"
    result3 = db.get_currency_for_country(country3)
    print(f"Country: '{country3}'")
    print(f"Currency result: {result3}")
    print(f"Symbol: {result3['symbol']}")

if __name__ == "__main__":
    test_currency_function()
