### 同一個交易 ID，為什麼保存成一個 list？

前面的箭頭把 normalize 縮成了一個步驟。實際上，它先檢查 mapping 是否包含 transaction_id、amount、currency，而且三個欄位必須存在、不能重複使用。接著逐列建立索引。transaction_id 是 CSV 裡的交易識別值；一次上傳工作的 run ID 則識別整個工作，兩者不是同一個 key。

normalize 對交易 ID 做 strip，移除首尾空白；幣別另做 strip 和 upper。它沒有把交易 ID 轉成同一種大小寫，因此 T100 與 t100 仍是不同交易 ID。每一筆正規化結果還保留 row：enumerate 從 2 開始，因為第一列是欄名，這個數字讓檢查者能回到 CSV 的原始資料列。

索引的 value 是 list，不是單筆資料。下面刻意讓左側 T100 出現兩次，作為程式的診斷輸入；它不是歷史模型報告裡的一次真實業務操作。

```text
left CSV
  row 2: T100, 100.00, USD
  row 3: T100, 100.00, USD
             |
             | normalize：相同 key 持續 append
             v
left index
  T100 -> [row 2, row 3]

right CSV
  row 2: T100, 98.00, USD
             |
             v
right index
  T100 -> [row 2]
```

若把索引改成 transaction_id 對到單筆 row，後一筆可能覆蓋前一筆，對帳時就看不見重複。保留 list，才有足夠資料區分「同一筆交易金額不同」和「交易 ID 本身就不唯一」。這段表示方式的選擇，直接決定下一步能檢查哪種錯誤。

