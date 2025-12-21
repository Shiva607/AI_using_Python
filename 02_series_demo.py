# pandas_series_usecases.py
import pandas as pd

#! video Reference: https://www.youtube.com/watch?v=vtgDGrUiUKk
#! Documentation: https://medium.com/@sathishkumar.babu89/pandas-series-the-one-dimensional-workhorse-youll-use-every-day-4628e8a1f6e2

def financial_returns_and_moving_averages():
    print("\n=== Financial Returns & Moving Averages ===")
    # Create a daily date index
    dates = pd.date_range('2025-12-01', periods=10, freq='D')

    # Close prices Series
    close = pd.Series([100, 101, 99, 102, 105, 103, 106, 108, 107, 110],
                      index=dates, name='close')

    # Daily percentage returns (vectorized)
    returns = close.pct_change().round(4)

    # 5-day moving average
    ma5 = close.rolling(5).mean()

    print("Close prices:\n", close)
    print("\nReturns (%):\n", returns)
    print("\n5-day moving average:\n", ma5)


def text_cleaning():
    print("\n=== Text Cleaning with .str ===")
    product = pd.Series(['  Pro MAX   ', 'basic', 'SUPER-deluxe'], name='product')

    clean = (
        product.astype('string')      # use pandas' string dtype
               .str.strip()           # trim spaces
               .str.lower()           # lowercase
               .str.replace(r'[^a-z]+', '-', regex=True)  # non-letters -> hyphen
               .str.strip('-')        # remove leading/trailing hyphens
    )

    print("Original:\n", product)
    print("\nCleaned:\n", clean)


def category_mapping():
    print("\n=== Category Mapping with .map ===")
    country = pd.Series(['US', 'IN', 'FR', 'BR', 'US'], name='country')

    region_map = {
        'US': 'Americas', 'CA': 'Americas', 'BR': 'Americas',
        'FR': 'EMEA', 'DE': 'EMEA', 'IN': 'APAC'
    }

    region = country.map(region_map).fillna('Other')

    print("Country codes:\n", country)
    print("\nRegion mapping:\n", region)

    # Memory tip: convert repeated labels to categorical
    country_cat = country.astype('category')
    print("\nCategorical dtype (memory-friendly):\n", country_cat)
    print("Categories:", country_cat.cat.categories.tolist())


def missing_data_and_alignment():
    print("\n=== Missing Data & Alignment ===")
    old = pd.Series({'apples': 100, 'oranges': 50}, name='qty_old')
    new = pd.Series({'apples': 120, 'bananas': 60}, name='qty_new')

    # Default arithmetic aligns by index; missing labels produce NaN
    delta_default = new - old

    # Safe arithmetic: treat missing as 0 using fill_value
    delta_safe = new.sub(old, fill_value=0)

    print("Old quantities:\n", old)
    print("\nNew quantities:\n", new)
    print("\nDelta (default alignment → NaN where missing):\n", delta_default)
    print("\nDelta (safe, missing treated as 0):\n", delta_safe)


if __name__ == "__main__":
    financial_returns_and_moving_averages()
    text_cleaning()
    category_mapping()