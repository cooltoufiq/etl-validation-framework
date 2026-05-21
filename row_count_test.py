# row_count_test.py

import random

def test_row_count():
    expected = random.randint(1, 100)
    actual = random.randint(1, 90)
    assert expected == actual, f"Expected {expected}, got {actual}"

if __name__ == "__main__":
    try:
        test_row_count()
        print("Test passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
