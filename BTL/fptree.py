import time
from collections import defaultdict
import re

# Hàm chuẩn hóa & chuyển đổi dữ liệu thành list of list cho FP-tree
def Load_data(filename):
    data = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            # Loại bỏ ký tự đặc biệt
            line = re.sub(r'[\[\]\{\}\'\";]', '', line.strip())
            items = [item.strip().upper() for item in line.split(',') if item.strip()]
            if items:
                # Loại mục trùng trong 1 giao dịch
                items = list(dict.fromkeys(items))
                data.append(items)
    return data

def create_initialset(dataset):
    retDict = {}
    for trans in dataset:
        trans_fs = frozenset(trans)
        if trans_fs in retDict:
            retDict[trans_fs] += 1
        else:
            retDict[trans_fs] = 1
    return retDict

class TreeNode:
    def __init__(self, Node_name, counter, parentNode):
        self.name = Node_name
        self.count = counter
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}
    def increment_counter(self, counter):
        self.count += counter

def update_NodeLink(Test_Node, Target_Node):
    #1 Duyệt đến cuối danh sách nodeLink (các node cùng tên trong cây)
    while (Test_Node.nodeLink is not None):
        Test_Node = Test_Node.nodeLink
    #2 Nối thêm node mới vào cuối danh sách
    Test_Node.nodeLink = Target_Node


def updateTree(items, node, headerTable, count):
    #1 Nếu không còn item nào thì dừng đệ quy
    if len(items) == 0:
        return

    first = items[0]  # Item đầu tiên trong danh sách đã sắp xếp

    #2 Nếu item này đã tồn tại trong cây dưới node hiện tại → tăng count
    if first in node.children:
        node.children[first].increment_counter(count)

    #3 Nếu chưa tồn tại → tạo node mới
    else:
        node.children[first] = TreeNode(first, count, node)

        #4 Cập nhật headerTable: nếu lần đầu xuất hiện thì gán luôn
        if headerTable[first][1] is None:
            headerTable[first][1] = node.children[first]
        #5 Nếu đã có, nối node mới vào danh sách nodeLink của item này
        else:
            update_NodeLink(headerTable[first][1], node.children[first])

    #6 Đệ quy xử lý các item còn lại trong danh sách
    updateTree(items[1:], node.children[first], headerTable, count)
    
def create_FPTree(dataset, minSupport):
    # 1. Đếm số lần xuất hiện (support) của từng item trong tất cả giao dịch
    header = {}
    for trans, count in dataset.items():
        for item in trans:
            header[item] = header.get(item, 0) + count

    # 2. Lọc bỏ những item có support < minSupport
    header = {item: [num, None] for item, num in header.items() if num >= minSupport}
    if not header:  # Nếu không còn item nào thỏa điều kiện
        return None, None

    # 3. Khởi tạo nút gốc của cây FP-tree (node "Null")
    root = TreeNode('Null', 1, None)

    # 4. Duyệt từng giao dịch để chèn vào FP-tree
    for trans, count in dataset.items():
        # Giữ lại các item đủ điều kiện trong giao dịch hiện tại
        freqItems = {item: header[item][0] for item in trans if item in header}
        if freqItems:
            # Sắp xếp item theo tần suất support giảm dần, nếu bằng thì theo thứ tự alpha
            ordered = [item for item, _ in sorted(freqItems.items(),key=lambda x: (-x[1], x[0]))]
            # Chèn các item đã sắp xếp vào cây
            updateTree(ordered, root, header, count)

    return root, header

def ascendTree(leafNode, prefixPath):
    # lưu lại tên các node trên đường đi để tạo prefix path
    if leafNode.parent is not None:              
        prefixPath.append(leafNode.name)         
        ascendTree(leafNode.parent, prefixPath)  


def find_prefix_path(basePat, treeNode):
    #1 Tìm tất cả các đường đi (prefix paths) dẫn đến item basePat
    condPats = {}                              
    while treeNode is not None:               
        prefixPath = []                        
        ascendTree(treeNode, prefixPath)       
        if len(prefixPath) > 1:                
            #2 Loại bỏ chính item basePat, chỉ lấy các item phía trước nó
            condPats[frozenset(prefixPath[1:])] = treeNode.count  
        treeNode = treeNode.nodeLink             
    return condPats                              


def mineTree(headerTable, minSupport, prefix, freqItemList, supportList):
    if headerTable is None:                    
        return
    #1 Sắp xếp các item theo support tăng dần để duyệt (đảm bảo khai thác từ item ít gặp trước)
    sorted_items = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0])]
    for basePat in sorted_items:               
        newFreqSet = prefix.copy()               
        newFreqSet.add(basePat)     
                    
        #2 Lưu tập phổ biến mới và support tương ứng
        freqItemList.append(frozenset(newFreqSet))
        supportList.append(headerTable[basePat][0])

        #3 Tìm conditional pattern base (các đường đi dẫn đến basePat)
        conditional_pattern_base = find_prefix_path(basePat, headerTable[basePat][1])

        #4 Tạo FP-tree điều kiện từ conditional pattern base
        myCondTree, myHead = create_FPTree(conditional_pattern_base, minSupport)

        #5 Nếu cây điều kiện vẫn còn item hợp lệ → tiếp tục khai thác đệ quy
        if myHead is not None:
            mineTree(myHead, minSupport, newFreqSet, freqItemList, supportList)


print("Enter the filename:")
filename = input()
option = input("Nhập 'c' nếu muốn nhập số lượng (count), nhập '%' nếu muốn nhập phần trăm: ")
if option == 'c':
    min_Support = int(input("Nhập min_support (số lượng): "))
    transactions = Load_data(filename)
    initSet = create_initialset(transactions)
else:
    min_support_percent = float(input("Nhập min_support (phần trăm): "))
    transactions = Load_data(filename)
    min_Support = int(len(transactions) * min_support_percent / 100)
    initSet = create_initialset(transactions)

start = time.time()
FPtree, HeaderTable = create_FPTree(initSet, min_Support)
freqItemList = []
supportList = []
mineTree(HeaderTable, min_Support, set([]), freqItemList, supportList)
end = time.time()

from collections import defaultdict
size_dict = defaultdict(list)
for fi, sup in zip(freqItemList, supportList):
    size_dict[len(fi)].append((fi, sup))
for size in sorted(size_dict.keys()):
    print(f"\nTập {size} phần tử (có {len(size_dict[size])} tập):")
    for fi, sup in size_dict[size]:
        items = ', '.join(sorted(fi))
        print(f"{{{items}}}: {sup}")
print("\n-------------------------------------------")
print(f"✅ Tổng số tập phổ biến tìm được: {len(freqItemList)}")
print(f"⏱️ Thời gian thực thi: {end - start:.4f} giây")
print("-------------------------------------------")

with open("output.txt", "w", encoding="utf-8") as f:
    for size in sorted(size_dict.keys()):
        f.write(f"\nTập {size} phần tử (có {len(size_dict[size])} tập):\n")
        for fi, sup in size_dict[size]:
            items = ', '.join(sorted(fi))
            f.write(f"{{{items}}}: {sup}\n")
    f.write("\n-------------------------------------------\n")
    f.write(f"Tổng số tập phổ biến tìm được: {len(freqItemList)}\n")
    f.write(f"Thời gian thực thi: {end - start:.4f} giây\n")
    f.write("-------------------------------------------\n")
            
