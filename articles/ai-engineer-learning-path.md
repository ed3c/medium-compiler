# 從軟體工程師到 AI Engineer：用一個文件助理串起 LLM、RAG、Evals、Agent 與 AI Infra

中文優先的學習路徑：從教材章節走到可執行的程式、可定位的失敗，以及能解釋的設計取捨。

假設你正在做一個工程文件助理。使用者問：「billing 服務的 v2，在回復上一版之前要檢查什麼？」系統找到一份 v1 文件，模型讀完後產生了一段流暢、格式正確、附有引用的回答。

這個回答能直接交付嗎？

只看 JSON 是否合法，會漏掉文件版本錯誤；只確認引用存在，會漏掉引用是否支持回答；只換一個更大的模型，則沒有修正資料選擇的條件。這個教學案例把一個 AI 應用拆成幾個可以分別檢查的問題：輸入是什麼、證據從哪裡來、模型能決定什麼，以及錯誤在哪一層被發現。

本文以已具備程式設計、Git、HTTP API 與基本測試經驗的軟體工程師為起點。目標是使用現成大型語言模型（Large Language Model，LLM）建構、評估與維運應用，再依需求深入模型實作與基礎設施。這裡不把「從零訓練大型基礎模型」當成完成第一個應用的先決條件。

以下路徑與文件助理是本文設計的教學方案，並非各教材共同指定的課綱。資源入口與公開目錄核對於 **2026 年 9 月 26 日**。文中的 Python 範例已執行；它使用可控制的模型替身，不代表已測試真實 LLM 的回答品質。

## 1. 先把「成為 AI Engineer」寫成可驗收的工作

[AI Engineering from Scratch 的 Learning Paths](https://aiengineeringfromscratch.com/learning-paths.html)把 LLM Product Engineering、Agent Systems Engineering、AI Evaluation and Reliability 等方向分開，依工作責任安排教材。本文先選應用工程主線：交付一個有資料依據、能診斷失敗、具有工具邊界的功能。

對文件助理而言，第一版只接收服務名稱、版本與問題，回傳附來源的候選回答。找不到指定版本的文件，就明確回報證據不足；模型呼叫失敗，就回報系統錯誤。它不操作真實部署、不執行 rollback，也不把文件中的文字當成額外授權。rollback 在此指將服務回復到先前版本。

這個範圍決定了學習順序。先把輸入、輸出與失敗行為做穩，才能比較檢索方式；先知道答案錯在哪裡，才有理由改 prompt、換模型或微調。之後加入工具與效能量測，仍使用同一批任務觀察變化。

最後應留下的能力是：另一位工程師能重現專案，而你能根據一筆失敗紀錄，指出應修改資料、模型介面、檢索、工具控制或部署中的哪一層。

## 2. 讓教材分工，不要讓每本書都成為前置條件

學習主線使用 [AI Engineering from Scratch](https://aiengineeringfromscratch.com/) 的 **Building and Deploying AI Applications** 路線。把它當成練習入口；需要哪種能力，就前往對應單元，不以首頁課程數量衡量進度。

應用設計的主教材選 Chip Huyen 的繁中版[《AI工程｜從基礎模型建構應用》](https://www.gotop.com.tw/book/BookDetails.aspx?bn=A806)。第 1、5 章幫助建立任務與模型介面；第 3–4 章處理評估；第 6 章進入 RAG 與代理；第 9–10 章連到推論與系統交付。第 7–8 章的微調與數據集工程，留到有適配需求時再讀。

理解模型內部時，使用 Sebastian Raschka 的 [Build a Large Language Model (From Scratch)](https://sebastianraschka.com/llms-from-scratch/)。需要中文補充，就查 [Happy-LLM](https://github.com/datawhalechina/happy-llm) 的 Transformer 與模型實作章節。兩者服務同一個理解缺口，不必每章重複通讀。

工具、上下文與 Agent 評估，使用[《深入理解 AI Agent》](https://github.com/bojieli/ai-agent-book)；資源需求與推論效能，使用[《深入理解 AI Infra》繁中版](https://bojieli.github.io/ai-infra-book/zh-tw/)。這兩套開源書都有持續修訂與社群翻譯，閱讀時應同時記錄章名與版本，不能只記章號。

主線與平行學習的依賴如下。箭頭表示前一步提供下一步需要的產物，不表示所有內容都必須按頁數讀完。

```text
可重現的 Python 程式與測試
  |
  v
模型輸入／輸出契約 + 最小評估
  |
  v
版本正確的證據檢索
  |
  v
有權限與停止條件的工具使用
  |
  v
量測、部署與失敗回復

平行深化：
文字資料 → attention → 小型模型實作

條件式分支：
行為適配需求 → Fine-tuning
容量／延遲瓶頸 → 更深入的 AI Infra
```

## 3. 第一個決策：用明確資料表示問題，而不是只保存一段 prompt

在本文的範例中，請求包含三個欄位：`service` 指定服務，`version` 指定文件適用版本，`question` 保存自然語言問題。文件片段則有自己的 `chunk_id`、服務、版本與本文。

```json
{
  "service": "billing",
  "version": "v2",
  "question": "回復上一版之前要檢查什麼？"
}
```

這個表示方式讓版本篩選有明確依據。如果把服務與版本藏在一長段對話中，每個元件都得重新猜測它們的意思；拆成欄位後，程式可以先排除不符合條件的文件。

本文的資料契約有一個可直接檢查的性質：**候選回答使用的每個引用 ID，都必須屬於這次提供給模型的文件集合。**這只能證明引用綁定，不能證明引用內容足以支持回答。

`chunk_id` 也不是授權證明。在這個離線範例裡，文件都是合成資料；真正加入內部文件前，還需要使用者身分、資料存取控制，以及能重現內容的來源版本或快照。服務名稱相同，不代表使用者有權閱讀該服務的所有文件。

學習這一段，可先讀《AI工程》第 1、5 章，再做課程的 [Structured Outputs](https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/03-structured-outputs&learningPath=building-and-deploying-ai-applications)。這一階段的產物是請求與回應契約、錯誤處理及測試；前進條件是能把無效輸入、證據不足和模型錯誤分開，而不是只展示一次成功回答。

## 4. 跟著一筆請求，走完資料與狀態的變化

先準備兩筆測試資料：`billing-v1-01` 屬於 v1，`billing-v2-01` 屬於 v2。v2 文件的內容是：「v2 的測試文件要求先檢查 migration 相容性。」migration 在這個例子裡指資料庫結構或資料的遷移；這句話只是測試素材，不是實際部署操作指引。

下面的資料流對應下一節程式。模型位置先放入 test double，也就是可控制回應的替代實作；它直接複製收到的第一筆文件，不理解問題。

```text
Request(service="billing", version="v2")
  |
  | 檢查必要欄位
  v
掃描 corpus，精確比對 service 與 version
  |
  | 排除 billing-v1-01
  v
evidence = (billing-v2-01,)
  |
  | 呼叫 fixture_model(question, evidence)
  v
JSON 文字：text + citations
  |
  | 解析結構、檢查欄位與引用集合
  v
status = "candidate"
```

`candidate` 表示結構與引用檢查通過，還不能被命名成「語意已驗證」。這個名稱讓後續評估保留明確位置。

把版本改成 v3，流程會在取得文件後分岔：集合為空，直接回傳 `insufficient_evidence`，不呼叫模型。這是一個由目前資料就能決定的步驟，不需要再讓模型判斷是否「應該試著回答」。

目前只做 metadata filtering，也就是依欄位篩選；它還沒有根據問題找出最相關的段落。先保留這個限制，下一個里程碑才有可以觀察的缺口。

## 5. 第一個可執行里程碑：讓模型替身接受相同的介面檢查

以下程式只需要 Python 3.10 以上的標準庫，不使用 API key，也不連網。存成 `doc_assistant.py`，執行 `python3 doc_assistant.py` 即可看到 v2 與 v3 的不同結果。

先使用替身，是為了讓相同輸入得到可控制的回應，單獨測試模型以外的程式。這一步不衡量 LLM 的能力；之後替換成真實 adapter 時，仍可保留同一組介面測試。

```python
"""Offline teaching example. No network calls and no real LLM inference."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Request:
    service: str
    version: str
    question: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    service: str
    version: str
    text: str


Model = Callable[[str, tuple[Chunk, ...]], str]


def run(req: Request, corpus: tuple[Chunk, ...], model: Model) -> dict:
    def error(reason: str) -> dict:
        return {"status": "error", "reason": reason}

    if any(not isinstance(v, str) or not v.strip()
           for v in (req.service, req.version, req.question)):
        return error("invalid_request")

    # Metadata filtering only; relevance retrieval is a later milestone.
    evidence = tuple(c for c in corpus
                     if c.service == req.service and c.version == req.version)
    if not evidence:
        return {"status": "insufficient_evidence", "citations": []}
    if any(not isinstance(c.chunk_id, str) or not c.chunk_id.strip()
           or not isinstance(c.text, str) or not c.text.strip()
           for c in evidence):
        return error("invalid_evidence")
    allowed = {c.chunk_id for c in evidence}
    if len(allowed) != len(evidence):
        return error("duplicate_chunk_id")

    try:
        raw = model(req.question, evidence)
    except TimeoutError:
        return error("model_timeout")
    except Exception:
        return error("model_call_failed")

    if not isinstance(raw, str):
        return error("invalid_response_type")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return error("invalid_json")
    if not isinstance(obj, dict) or set(obj) != {"text", "citations"}:
        return error("invalid_schema")
    text, ids = obj["text"], obj["citations"]
    if not isinstance(text, str) or not text.strip():
        return error("invalid_text")
    if (not isinstance(ids, list) or not ids
            or any(not isinstance(x, str) or not x.strip() for x in ids)):
        return error("invalid_citations")
    if len(set(ids)) != len(ids) or not set(ids) <= allowed:
        return error("unbound_citation")
    # This establishes structure and citation membership, NOT semantic truth.
    return {"status": "candidate", "text": text, "citations": ids}


def fixture_model(question: str, evidence: tuple[Chunk, ...]) -> str:
    """A test double: copy one fixture, without interpreting the question."""
    return json.dumps({"text": evidence[0].text,
                       "citations": [evidence[0].chunk_id]}, ensure_ascii=False)


CORPUS = (
    Chunk("billing-v1-01", "billing", "v1", "v1 的測試文件。"),
    Chunk("billing-v2-01", "billing", "v2",
          "v2 的測試文件要求先檢查 migration 相容性。"),
)


if __name__ == "__main__":
    for version in ("v2", "v3"):
        req = Request("billing", version, "回復上一版之前要檢查什麼？")
        print(json.dumps(run(req, CORPUS, fixture_model), ensure_ascii=False))
```

這段程式實際執行時，兩筆輸出依序如下：

```text
{"status": "candidate", "text": "v2 的測試文件要求先檢查 migration 相容性。", "citations": ["billing-v2-01"]}
{"status": "insufficient_evidence", "citations": []}
```

範例附帶的 16 個契約測試涵蓋版本篩選、空證據、重複文件 ID、無效 JSON、錯誤引用、模型例外與 CLI 輸出。其中一個測試刻意讓模型說「完全不必檢查 migration 相容性」，卻引用 `billing-v2-01`。程式仍回傳 `candidate`。這個結果暴露了檢查邊界：**引用存在，不足以證明回答忠於引用。**

引用綁定的理由可以直接從程式重建：`evidence` 只收錄服務與版本都相符的片段，`allowed` 只取自這些片段，而回傳前又檢查所有引用都屬於 `allowed`。因此，在輸入 corpus 已是合法 `Chunk` 資料的前提下，通過這些檢查的引用不會指向本次證據集合之外。這個推導沒有包含回答文字的意義，語意評估仍是另一個問題。

這裡沒有實作真正的 deadline。`except TimeoutError` 只處理 adapter 已經回報的逾時；真實 adapter 仍須設定逾時、回應大小限制與有界重試，也要保留供診斷使用的錯誤紀錄。範例同樣沒有實作語意拒答：找到文件但內容無關時，後續模型契約需要能明確表達證據不足。

這一階段的驗收是：在乾淨環境重現正常與拒絕路徑，並能指出程式尚未驗證什麼。若 Python 環境、JSON 或測試隔離仍不熟，先回到課程的 [Software Engineering Fundamentals](https://aiengineeringfromscratch.com/learning-paths.html)；不必同時補完整個深度學習課程。

## 6. 成本從執行的操作推導，不把模型呼叫當成常數

這個小程式也能練習複雜度分析。令 `M` 是 corpus 中的片段數，`K` 是篩選後的片段數，`R` 是模型回傳 JSON 的字元數，`C` 是引用數。先假設服務、版本與引用 ID 的長度有固定上限，並採用 hash set 查找的平均成本模型。

篩選掃描 `M` 筆資料；驗證 evidence 並建立允許集合處理 `K` 筆；JSON 解析讀取 `R` 個字元；引用驗證處理 `C` 個 ID。還有一項容易漏掉：[Python 的 `strip()`](https://docs.python.org/3/library/stdtypes.html#str.strip) 用來檢查請求與文件本文是否只有空白，最壞情況會掃描文字。令 `V` 是這些待驗證輸入字串的總字元數，本機工作量的上界可寫成 `O(M + K + V + R + C)`。模型生成與傳輸需要另外量測，不能因為它在程式裡只有一行，就當作 `O(1)`。

新增的 evidence tuple 保存 `K` 個文件參照，沒有持久複製所有文件本文；但 `strip()` 可能建立暫存字串。令 `V_max` 是待驗證輸入字串的最大長度，連同允許集合、回應解析與引用集合，本機額外空間的上界是 `O(K + R + C + V_max)`。回傳文字與引用有一部分會成為輸出保留資料，文件驗證的暫存則可釋放。這裡不包含原有 corpus，也不包含外部模型的記憶體。

若 ID 長度不再受限，字串比較與 hashing 的字元成本也要計入。這些條件說明估算何時成立，以及改了資料表示後要重新檢查哪裡。

## 7. 接上真實 LLM：先讓一次請求可觀察，再談 prompt 優化

把 `fixture_model` 換成真實 provider adapter 時，保留 `question + evidence → JSON text` 的介面。adapter 負責將資料組裝成模型請求，依供應商介面處理回應、拒絕、截斷、逾時與用量資訊。不要把 API key 寫進程式或測試資料。

這一階段先讓一筆請求留下可查證紀錄：使用哪個模型、哪個 prompt 版本、哪些文件、得到什麼原始回應，以及最後通過或失敗的原因。提供給模型的資料與執行時設定應能重現；敏感內容則須按資料政策遮罩與控制保存範圍。

閱讀《AI工程》第 3–4 章，搭配 [Evaluation & Testing LLM Applications](https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/10-evaluation&learningPath=building-and-deploying-ai-applications)。練習不只包含正常問題，也應包含無關文件、文件矛盾與模型拒絕。這些是本專案選定的診斷案例，不代表真實使用分布已完整覆蓋。

前進條件是能辨認失敗位置。JSON 壞掉就先看輸出契約；文件版本錯誤就看資料選擇；引用正確但說反了，就檢查回答與證據的語意。每次先固定一個問題，再修改相應部分。

## 8. RAG：從「文件有沒有找到」走到「回答有沒有使用」

Retrieval-Augmented Generation（RAG，檢索增強生成）把外部檢索結果接入生成流程。原始 [RAG 論文](https://arxiv.org/abs/2005.11401)將模型參數中的知識與可檢索的非參數記憶結合；本文借用檢索後生成的應用設計，不要求重現原論文的聯合訓練方法。

範例目前會把同服務、同版本的所有片段交給模型。當其中只有部分段落與問題有關時，就需要相關性檢索：先確定可用文件的範圍，再選出與問題相關的內容，保留 ID 與版本資訊，最後組裝進上下文。

```text
獲授權的文件快照
  |
  v
切分片段 + 保存來源與版本
  |
  v
建立可搜尋的資料表示
  |
  v
權限／版本條件 + 問題
  |
  v
檢索相關片段
  |
  v
帶證據的模型請求
  |
  v
回答 + 引用 + 分層評估
```

第一個替代方案其實是先不做檢索。若文件集合很小，可以直接提供全部適用文件，建立比較基線；當內容增加、用量不可接受，或無關內容影響回答時，再用相同案例比較檢索方案。不要把「一定要向量資料庫」放在需求之前。

檢索也有選擇。先用簡單文字搜尋建立可解釋的基線；若觀察到同義詞或不同表達造成漏找，再評估 embedding，也就是把文字表示成可比較的向量。若候選集合有正確段落卻排序不好，再評估 reranking，即對候選重新排序。這些都是本專案的實驗順序，不保證某種方法一定勝出。

閱讀《AI工程》第 6 章，接上課程的 [RAG 單元](https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/06-rag&learningPath=building-and-deploying-ai-applications)；中文補充使用 [Happy-LLM 第 7 章「大模型應用」](https://github.com/datawhalechina/happy-llm)。

這一段的產物包括文件處理流程、檢索結果與失敗標註。驗收時，分開回答：正確文件有沒有進入候選？送進模型的證據是否充分？回答是否忠於證據？若只保存最後答案，三種失敗很容易被混在一起。

## 9. 用 Evals 改善行為：每一輪只追一個真實失敗

Evals 在這裡指保存案例、判斷結果、比較變更並診斷失敗的工作。[Hamel 與 Shreya 的 AI Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)建議從真實輸出與錯誤分析形成評估，而不是一開始就套用通用 rubric。rubric 是判分準則；主觀判斷需要對照可信的人工標註檢查，不能因為有另一個模型打分，就視為正確。

本文已執行的控制案例，只證明引用檢查無法辨認語意顛倒。它不是「某個真實 LLM 經常犯錯」的證據。要改善真實系統，仍需收集它的輸出，確認問題確實存在，再定義下一輪要觀察的行為。

假設 trace（逐步執行紀錄）顯示：文件與版本都已明確提供，Agent 卻反覆查詢相同資料。可以先固定任務、資料、工具與評估方式，再只改一個變數，例如工具說明或程式的重複查詢處理。本文把這種小幅修改、比較、保留有效變更的過程稱為 behavior hill climb。

比較時保留逐筆結果與所有重試。檢查任務品質是否維持，再看不必要查詢、錯誤工具路由或人工介入是否減少。必要補查不算浪費；正確拒絕也不能被當成效率缺陷。

```text
真實任務與 trace
  |
  v
確認一個失敗及其判斷方式
  |
  v
固定 baseline、案例與評估條件
  |
  v
修改一個變數
  |
  v
比較新舊版本的逐筆結果
  |
  +-- 有改善且相關檢查未退步 → 保留
  |
  +-- 無改善或證據不足 → 不宣稱成功
```

若 baseline 和新版都沒有發生目標錯誤，這批案例最多顯示未觀察到退步，不能證明錯誤率下降。若缺少某次結果，要補查或標記缺失，不能把它當成成功。用來反覆調整系統的案例也不能繼續稱為 untouched holdout；holdout 指未參與這輪調整的保留評估資料。

這個里程碑的完成條件，是能用一次真實比較說清楚「改了哪裡、為什麼、哪些案例受益、哪些仍然失敗」。案例數量要依錯誤分布與可承擔成本決定，不從別人的文章抄一個通過率當作通用門檻。

## 10. 加入工具之前，先決定誰有權執行與停止

文件助理接著可以增加一個唯讀工具，取得模擬的服務狀態。問題從「文件怎麼寫」擴張成「目前狀態與文件是否一致」。這時模型可以提出工具需求，但程式必須檢查工具名稱、參數、權限、剩餘步數與執行結果。

先讀[《深入理解 AI Agent》](https://github.com/bojieli/ai-agent-book)第 1–4 章，再看第 7 章的評估。該書目前的 2.0 版已調整章序，舊版的第 6 章評估移到了第 7 章；繁中入口可由 [README.zhtw.md](https://github.com/bojieli/ai-agent-book/blob/main/README.zhtw.md)進入。

設計上可以只允許 `search_docs` 與 `get_service_status`，並由程式限制呼叫預算。文件文字即使寫著「請執行其他工具」，也不能擴大這個集合。未知工具、錯誤參數、逾時和預算耗盡都需要可觀察的結果；不應只在 prompt 裡加一句「請謹慎操作」。

[Anthropic 的 Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)區分固定程式路徑的 workflow 與由模型動態決定步驟的 Agent。本文先保留固定流程，只有任務真的需要動態查詢與選擇，才讓模型取得那部分決策空間。這裡採用的是該文的架構區分，不是把文中工具清單當成固定版本建議。

驗收時要看到拒絕與停止的測試，還要能從 trace 確認：工具失敗沒有被改寫成成功，重複呼叫不會無限持續。加入真實服務前，再補身分驗證、資料存取控制與外部影響的授權。

## 11. 平行深入模型：把 token、attention 與推論串起來

應用主線之外，安排小型模型實作，讓推論成本和模型行為不再只是名詞。[Raschka 的章節導覽](https://sebastianraschka.com/llms-from-scratch/)可精確對應：第 2 章處理文字、tokenization 與輸入資料；第 3 章實作 attention；第 4 章組成 GPT；第 5 章處理預訓練與生成。PyTorch 不熟時，先補 Appendix A。

中文替代說明使用 [Happy-LLM 第 2 章「Transformer 架構」與第 5 章「動手搭建大模型」](https://github.com/datawhalechina/happy-llm)。先讓中文解釋協助理解，再核對程式裡的英文識別字；不必同時重做兩套完整實作。

Tokenization 是把文字轉成模型使用的 token 序列；token 並不保證對應一個字。以 decoder-style Transformer 的 causal attention 為例，某個位置只能使用允許的前文與當前位置，不能讀取後面的 token。[Hugging Face 的 cache 說明](https://huggingface.co/docs/transformers/cache_explanation)也從這個性質解釋既有 Key／Value 為何可以在生成時重用。

一個有鑑別度的練習是準備兩個 token 序列：前綴相同，後綴不同。固定權重與位置設定、關閉 dropout 等隨機操作，在數值容差內比較前綴輸出。若未來 token 的改變影響了前綴，就檢查 causal mask（因果遮罩）、索引與維度。這是本文設計的後續練習，沒有包含在前面的 16 個已執行測試中。

完成這段時，應能追蹤張量如何經過 embedding、attention 和輸出層，並定位一個 mask 或維度錯誤。小資料上的 loss 下降只能說明那個訓練設定下的目標值下降，還需要另外評估模型是否能完成新的任務。

## 12. AI Infra：從一筆請求的等待與記憶體開始

文件助理變慢時，先拆開資料取得、模型請求、生成與後處理的時間。[《深入理解 AI Infra》](https://github.com/bojieli/ai-infra-book)建議先讀第 1–3 章理解模型與負載；應用與推論服務讀者再看第 8–9、11–12 章。算子、硬體或通信問題出現時，再回到第 4–7 章。

模型端可以先分辨 prefill 與 decode：前者處理輸入上下文，後者逐步生成輸出。KV cache 保存已計算的 Key 與 Value，讓後續生成重用它們；代價是需要額外的記憶體。[Hugging Face 的說明](https://huggingface.co/docs/transformers/cache_explanation)列出了逐層快取及其張量形狀。

為了把概念變成可估算的量，考慮每層都保存完整歷史、沒有壓縮的標準 KV cache。若各序列長度相同，可以由張量元素數推導：

```text
KV bytes = 2 × L × B × S × H_kv × D_h × b

2     : Key 與 Value 各一份
L     : 快取層數
B     : batch 中的序列數
S     : 每條序列保存的 token 數
H_kv  : 每層的 KV head 數
D_h   : 每個 head 的維度
b     : 每個元素占用的 bytes
```

假設 `L=32`、`B=1`、`S=16384`、`H_kv=8`、`D_h=128`、`b=2`，則需要 `2,147,483,648 bytes`，也就是 **2 GiB**。這是本文假設參數的計算結果，不對應某個已量測模型，也不包含權重、運算工作區、allocator 或其他服務開銷。滑動視窗、量化、壓縮與跨層共享快取等設計，不能不加調整就套用這個公式。

接著做固定工作負載的量測。TTFT（Time to First Token）是從定義好的請求起點到第一個輸出 token 的時間；TPOT（Time per Output Token）則描述後續 token 的平均時間。要說明量測在客戶端還是伺服器端，以及是否包含排隊。不同工具的操作定義也可能不同，例如 [NVIDIA 的指標說明](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html#metrics)以收到第一個 response 定義 TTFT；使用時須核對 response 與 token 的對應。若只能取得串流區塊的時間戳，就報告 chunk timing，不把它冒稱逐 token 時間。

同時記錄整體完成時間、失敗請求、重試、輸入與輸出用量。本文建議另外計算「全部可歸因成本 ÷ 成功任務數」，並列清楚計價日期、成本範圍與成功定義；零成功時比值沒有定義，不能顯示成零成本。

閱讀《AI工程》第 9–10 章，搭配 [Building a Production LLM Application](https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/13-production-app&learningPath=building-and-deploying-ai-applications)。[AI Infra 的計算工具](https://github.com/bojieli/ai-infra-book)也能協助估算資源，靜態計算不要求 GPU；工具算出的量不是硬體實測速度。

這一階段的產物是原始量測、固定設定、部署說明及降級／回復方式。前進條件是能重現一項比較，並解釋品質、成本與延遲的取捨；只在本機跑通，不等於已承擔 production 流量與 on-call 責任。

## 13. Fine-tuning 是有條件的分支，不用拿來修正所有錯誤

若問題是 v2 文件未被檢索到，先修資料與檢索；若是工具可以越權，先修程式邊界。只有當任務行為仍不符合需求、現有 prompt 與資料處理的限制已被具體觀察，而且手上有可合法使用的訓練資料，才比較 Fine-tuning（微調）是否值得投入。

這時讀《AI工程》第 7–8 章，接 [Raschka 第 6–7 章與 Appendix E](https://sebastianraschka.com/llms-from-scratch/)。第 6 章是分類微調，第 7 章是指令微調，Appendix E 是 LoRA；中文實作補 [Happy-LLM 第 6 章](https://github.com/datawhalechina/happy-llm)。

先固定比較任務，分開訓練資料、用於調整的資料與保留評估資料，再檢查新舊模型的逐筆結果。成功完成訓練，不能直接改寫成「產品品質已提升」。模型適配、資料更新與 runtime 權限是不同的問題，學習分支應跟著實際缺口走。

## 14. 每個里程碑留下什麼，才算真的前進？

第一個里程碑是可重現的介面：另一個乾淨環境能執行程式，錯誤輸入不會被當成成功。接著是帶證據的回答：你能分開定位資料選擇、生成與引用失敗。第三個里程碑是有界工具使用：允許、拒絕、逾時與停止都能回讀。最後是可交付的服務：測試、評估、量測和回復方式都有明確入口。

模型內部與 Fine-tuning 的練習各自保存，不必塞進應用 production runtime。作品集可以按照下面的概念目錄組織；這是後續擴充建議，不代表前面範例已經完成所有檔案。

```text
learning-project/
├── README.md          # 任務、範圍、重現方式
├── app/               # 模型介面、檢索、工具邊界
├── tests/             # 可確定的程式行為
├── evals/             # 案例、判斷方式、逐筆結果
├── experiments/       # 模型內部、效能與適配練習
└── reports/           # 比較、失敗分析與未解限制
```

每週可先以 12 小時安排：3 小時閱讀、6 小時實作、2 小時測試與失敗分析、1 小時解釋設計。這是起步的時間假設，不是最佳比例或取得工作的期限。有基礎缺口時就調整，不必為了維持表定進度跳過失敗。

一週的目標可以是「指定版本不存在時，不再呼叫模型」，下一週是「引用存在但內容顛倒時，評估能指出錯誤」。這些目標有輸入、行為和觀察方法，比「學完 RAG」更容易知道自己是否完成。

## 15. 用英文說清楚實際做過的取捨

面試解釋可以從本文程式真正具備的行為出發，不用把尚未做過的 production 經驗放進答案。

**Why use a model test double first?**

> It makes the model boundary repeatable, so I can test filtering, parsing, and citation checks separately from model quality.

**What does a valid citation prove in this prototype?**

> It proves that the cited ID belongs to the supplied evidence. It does not prove that the evidence supports the answer.

**Why is the result called a candidate?**

> The program has checked its structure and citation membership. Semantic correctness still needs a separate evaluation.

最短的記憶版本是：*Filter the evidence. Validate the response. Evaluate the meaning.* 每一句都對應一段程式或一項尚須補上的評估，而不是一串與專案無關的名詞。

## 16. Master Map：從失敗決定下一段學習

完整路徑可以回到最初的文件助理。下面的箭頭表示工程依賴；支線說明遇到某種問題時，應回去哪個能力。

```text
指定服務、版本與問題
  |
  v
明確的資料契約
  |  欄位／格式錯誤 → 模型介面與程式測試
  v
有來源、版本與權限的證據
  |  文件找不到 → 資料處理與 RAG
  v
模型產生候選回答
  |  內容不忠於證據 → 語意評估與任務設計
  v
需要時使用有界工具
  |  越權／無法停止 → runtime 控制
  v
逐筆結果與執行紀錄
  |  品質變化說不清 → Evals
  |  延遲／容量不可接受 → AI Infra
  v
可重現、可診斷、可交付的應用

平行理解：token → attention → 模型實作
條件式深化：有資料與比較方法後，再做 Fine-tuning
```

這條路徑保留三個判斷：用工作結果選教材，用具體失敗安排下一個實作，用可重現的行為與解釋判斷是否前進。讀到哪一頁是閱讀紀錄；能否讓另一位工程師重現、檢查並理解你的系統，才是作品集要回答的問題。

---

**資源與實作說明**：本文的課程連結、出版社目錄、作者導覽與開源書入口已核對；動態課程頁面並非逐課程式驗證。GitHub `main` 與網站內容會更新，重現時請記錄 commit、依賴、模型與資料版本。文內 Python 程式及 16 個離線契約測試已執行；真實 LLM、語意 judge、模型訓練、效能負載與完整 production 部署不在本次執行範圍。本文不是就業保證。
