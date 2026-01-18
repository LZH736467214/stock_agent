"""
测试双数据源 (AKShare + Baostock)
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("双数据源测试")
print("=" * 60)

from tools.data_source import fetch_financial_data_dual, RateLimitError

TEST_CODE = "sh.600519"
TEST_YEAR = 2024
TEST_QUARTER = 3

data_types = ["profit", "growth", "balance"]

for data_type in data_types:
    print(f"\n[TEST] Getting {data_type} data...")
    try:
        df = fetch_financial_data_dual(TEST_CODE, TEST_YEAR, TEST_QUARTER, data_type)
        if df is not None and not df.empty:
            print(f"  [OK] Success! {len(df)} rows, {len(df.columns)} columns")
            cols = list(df.columns)[:5]
            print(f"  Columns: {cols}...")
        else:
            print(f"  [WARN] Empty data returned")
    except RateLimitError as e:
        print(f"  [FAIL] Rate limited: {e}")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
