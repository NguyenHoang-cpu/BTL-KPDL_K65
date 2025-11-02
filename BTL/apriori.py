import time
import re
from apyori import apriori

# ====== Hàm đọc dữ liệu giống FP-tree ======
def Load_data(filename):
    data = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            line = re.sub(r'[\[\]\{\}\'\";]', '', line.strip())
            items = [item.strip().upper() for item in line.split(',') if item.strip()]
            if items:
                items = list(dict.fromkeys(items))
                data.append(items)
    return data

# ====== Chạy Apriori ======
def run_apriori(filename, min_support):
    transactions = Load_data(filename)

    start = time.time()
    results = list(apriori(transactions, min_support=min_support))  # có thể thêm min_confidence nếu muốn
    end = time.time()

    freq_itemsets = []
    supports = []

    for item in results:
        freq_itemsets.append(frozenset(item.items))
        supports.append(item.support)

    total = len(freq_itemsets)
    for itemset, sup in zip(freq_itemsets, supports):
        print(f"{set(itemset)} : {sup:.4f}")
    
    print("\n===== Kết quả Apriori =====")
    print(f"📌 Tổng số tập phổ biến: {total}")
    print(f"⏱ Thời gian thực thi: {end - start:.4f} giây")
    return end - start, total

# ====== Chạy thử cho người dùng ======
if __name__ == "__main__":
    print("Nhập tên file dữ liệu (giống như dùng cho FP-tree): ")
    filename = input()
    option = input("Nhập 'c' nếu dùng min_support theo số lượng (count) hay '%' nếu dùng theo phần trăm: ")

    transactions = Load_data(filename)

    if option == 'c':
        min_support = int(input("Nhập min_support (số lượng): ")) / len(transactions)
    else:
        min_percent = float(input("Nhập min_support (%): "))
        min_support = min_percent / 100

    run_apriori(filename, min_support)
