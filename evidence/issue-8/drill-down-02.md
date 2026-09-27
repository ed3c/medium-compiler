### 有重複資料時，為什麼不能先算 2.00？

reconcile 不是看到同一個 key，就立刻把左右第一筆金額相減。它走訪左右 ID 的聯集，排序後依固定優先序分類。下面的符號目錄對應 app/main.py 的實際函式；目錄表示責任歸屬，箭頭才表示資料怎麼流動。

```text
app/main.py
├─ normalize(source, mapping)
│  ├─ 檢查欄位與資料
│  └─ transaction_id -> list of normalized rows
└─ reconcile(left, right)
   ├─ 走訪 sorted(set(left) | set(right))
   ├─ 依序分類
   └─ findings：保留左右 row 與差額
```

```text
同一個 ID 的左右 lists
  |
  +-- 任一側超過一筆？
  |     yes -> duplicate_key，delta = null
  |     no
  v
任一側沒有資料？
  |     yes -> missing_left 或 missing_right，delta = null
  |     no
  v
幣別不同？
  |     yes -> currency_mismatch，delta = null
  |     no
  v
金額不同？
  |     yes -> amount_mismatch，delta = left - right
  |     no
  v
不產生 finding
```

所以剛才的重複 T100 會得到 duplicate_key，左右的 row 仍保留在 finding 中，但 delta 是 null。即使兩側各取第一筆可以算出 100.00 − 98.00 = 2.00，程式也不會把它當成可信的金額差異。只有兩側都恰好一筆、幣別相同且金額不同，才產生 amount_mismatch 並計算 delta。

同樣地，若一側重複、另一側缺列，最先成立的仍是 duplicate_key；幣別不同時，也不會把兩個不同貨幣的數字直接相減。這些保證只涵蓋程式採用的分類規則，不證明來源 CSV 或已提交 mapping 的業務含義正確。完整條件可以回到前面連結的 app/main.py，對照 normalize 與 reconcile 逐行檢查。

