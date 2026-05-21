# row_count_test.py

source_count = 1001
target_count = 91


print(f"Source count: {source_count}")
print(f"Target count: {target_count}")
if source_count != target_count:
    raise Exception("Row count mismatch!")
else:    print("Row count matches.")
