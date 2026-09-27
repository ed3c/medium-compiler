# Git 與協作：讓每次練習都能追蹤、隔離與備份

上一篇[開發環境設定](https://medium-compiler.vercel.app/articles/application-engineering-colab/)讓程式可以執行。這一篇依 [Git & Collaboration 原課](https://aiengineeringfromscratch.com/lesson?path=phases/00-setup-and-tooling/02-git-and-collaboration&learningPath=software-engineering-fundamentals)，把練習檔案保存成可追溯的版本，再放到自己的 GitHub fork。它是 Software Engineering Fundamentals 的第二課。

這次已實際建立 fork、clone、建立分支、提交、推送、驗證忽略規則與讀取歷史。文章直接說明每個動作的原因與結果；不另加等待讀者作答的題目，也不把代理操作紀錄登記成學員測驗成績。

## 2026 年 9 月 27 日複驗：原課要求已逐項核對

本次重新讀完原課的學習目標、問題、概念、Build It 四步、Use It、三道 Exercises 與實際五題題庫。課文版本仍是原先的 `968da079`。沿用已建立的 fork 與 my-progress，重新 clone、加入一份解釋操作原因的筆記、提交並推送，再從 GitHub 建立全新副本取回檔案。原課沒有要求 Colab，也沒有獨立的 Ship It 章節；這一課可以直接在本機完成。

下文保留的 `4e5a5abc`、`960f0b5c` 是第一次實作的兩個提交；本次在它們之上新增 [Git 操作筆記](https://github.com/ed3c/ai-engineering-from-scratch/blob/3d9a80386b195fb7156b2aedc126a4e48a39390d/learning-artifacts/git-collaboration/review.md)，提交為 `3d9a80386b195fb7156b2aedc126a4e48a39390d`。舊紀錄描述第一次操作，本節及新增的複驗章節描述這次操作。

三道實作要求都有可核對的成果：自己的 fork／my-progress 已保存並取回新筆記；三種 checkpoint 副檔名仍受忽略，明確 add 被拒絕；再次讀取 log 與課文 diff，確認先 fork 再 clone 的修正原因。這表示原課指定的操作已執行，不表示讀者已通過個人測驗。原課五題的答案與推理也直接列在後面，方便對照觀念。

## 本課行動：保存一次可核對的變更

原課沒有要求開發模型或部署服務。這次用一個只有一行文字的檔案，追蹤它從磁碟、暫存區、commit 到 GitHub 的變化。選擇這麼小的例子，是為了看清楚 Git 保存的究竟是哪一份內容，避免套件或模型錯誤掩蓋版本控制本身。

最後交付的是自己的[課程 fork 與 my-progress 分支](https://github.com/ed3c/ai-engineering-from-scratch/tree/my-progress)、兩個可閱讀的提交，以及三種模型權重格式的忽略規則。原課上游與 fork 的遠端 main 都沒有被這次練習修改。

## 學習目標

第一個目標是分清楚設定提交者身分、建立 commit 與取得遠端推送權限。名字與 email 是提交紀錄的一部分；它們不會替你登入 GitHub。

第二個目標是能在實驗分支工作，確認 main 在合併前不受影響，再理解合併如何把成果接回來。分支是一個會移動的 commit 指標，不是每次都複製整份專案。

第三個目標是只保存需要追蹤的來源。模型 checkpoint 常很大，應由適合的儲存位置管理；程式、設定與取得權重的方法，才應清楚留在版本紀錄。

第四個目標是能從歷史找到「當時為什麼需要這個修正」，而不只看見一串提交代碼。本次會用原課補上 fork 步驟的修改作例子。

## 問題：存檔、提交與備份是三個動作

編輯器的存檔只改變工作目錄中的檔案。建立 commit 才有本地版本；推送成功，且遠端讀回相同 commit，才確認這一版已到 GitHub。若把這三件事混成「已存好了」，就可能以為最新內容已備份，其實只停在磁碟上。

AI 工程還有另一個常見問題：一次產生許多模型檔、資料與實驗輸出，隨手全部加入版本庫，會讓日後下載與追蹤變得笨重。忽略規則要在加入檔案前建立，並用真實檔名檢查它有沒有生效。

## 概念：一份內容經過四個位置

工作目錄是現在正在編輯的檔案；暫存區是準備放進下一次 commit 的內容；本地 repository 保存 commit 與歷史；remote 是另一個 repository 的位置。這一課的 remote 位於 GitHub，但 Git 的本地提交不需要連上 GitHub。

```text
工作檔 snapshot=1
  → git add：暫存區記住1
  → 工作檔改成2：暫存區仍是1
  → git commit：第一個commit保存1
  → 再次git add + git commit：第二個commit保存2
  → git push：更新自己的遠端分支
  → 讀回遠端commit：確認與本地相同
```

這是本次真正執行的案例。第一個 commit `4e5a5abc` 內的檔案是 `snapshot=1`；第二個 `960f0b5c` 才是 `snapshot=2`。[Git add 官方說明](https://git-scm.com/docs/git-add)指出，add 保存的是執行當下選定內容，後續修改需要再次 add。這解釋了為什麼看見已 staged 的檔案，也不能假設最新編輯自動包含在 commit 裡。

在合併前，main 仍指向原課版本 `968da079`，my-progress 已指向兩次練習提交。main 的原位置是後者的祖先，所以這次本機合併可以 fast-forward：把 main 指標往前移到已存在的 commit，不需要製造第三個 merge commit。這是實際驗證的合併情況；兩邊各自修改同一處時，可能需要解決衝突，不能套用這次的無衝突結果。[Git merge 官方說明](https://git-scm.com/docs/git-merge)

```text
合併前：A（main）→ B（第一次練習）→ C（my-progress）
合併後：A → B → C（本機main與my-progress）
GitHub：main仍在A；my-progress在C
```

本機分支與遠端同名分支不是同一個物件；本機 merge 不會自動 push。因此可以驗證合併，同時保留 GitHub main 作為乾淨的上游起點。

## 建立它（Build It）

### 步驟 1：設定提交身分，另外確認連線權限

原課示範用 global 設定姓名與 email，這會成為其他 repository 的預設值。本次改用課程工作副本的 local 設定，避免影響已有專案；使用 GitHub noreply email，讓公開 commit 不必揭露私人信箱。

```bash
git config --local user.name "ed3c"
git config --local user.email "30064024+ed3c@users.noreply.github.com"
```

這是本次帳號的設定，其他讀者應使用自己的名稱與 GitHub 提供的 noreply email。local 與 global 改變的是設定套用範圍；都不會賦予對別人的 repository 的寫入權限。

本次 GitHub CLI 的查詢回傳 HTTP 401，但 Git 的 SSH 連線與後續 push 成功。這表示兩者使用的登入方式不同；不能由 CLI 失敗直接推論 Git 完全不能用，也不能由瀏覽器已登入就推論終端機有權限。本文沿用已可用的 SSH，不另建立 token，也沒有變更帳號權限。

### 步驟 2：照 add、commit、push 保存練習

工作目錄位於 `~/ai-engineering-learning/git-collaboration/my-progress`，分支就是 `my-progress`。先檢查所在位置與要提交的差異，再選定檔案；本次沒有使用會一次加入所有未知輸出的做法。

```bash
cd ~/ai-engineering-learning/git-collaboration/my-progress
git status --short
git branch --show-current
git add learning-artifacts/git-collaboration/practice.txt
git diff --cached
git commit -m "feat(phase-00/02): retain the revised practice snapshot"
git push -u origin my-progress
```

這組命令示範有新修改時的工作流程。現在練習已提交，直接重跑而沒有改檔案，Git 會顯示沒有可提交內容，並不是需要重建 repository。

想知道下一個 commit 包含什麼，讀 `git diff --cached`；想看尚未暫存的修改，讀 `git diff`。本次先暫存1，再把工作檔改成2，分別讀取兩個差異，確認 commit 只保存1；第二次明確 add 後才提交2。這比只背誦命令順序更能解釋實際結果。

### 步驟 3：隔離實驗，再核對合併

原課一般流程是在同一個 checkout 建立並切換分支。本次已有其他開發工作，沿用「不切換共享工作目錄分支」的操作限制，建立兩個獨立課程副本。主副本一直在 main，練習副本從建立時就選定 my-progress。

```bash
# 已clone的主副本中建立分支，但不切換它
git -C course-main branch my-progress
# 新副本從一開始就選定練習分支
git clone --branch my-progress ./course-main ./my-progress
```

兩份 checkout 多占磁碟空間，卻讓這次練習不必改變另一個目錄正在使用的分支。這是本次的替代操作，不是每位初學者都必須建立兩份副本。分支本身仍是 commit 指標；不要把這個隔離安排誤認成 Git 每建分支都會複製專案。

練習提交完成後，先確認主副本仍是原始 commit，才從練習副本 fetch 並執行 `git merge --ff-only FETCH_HEAD`。因為 main 沒有其他新提交，fast-forward 成功；最後兩個本機副本指向同一個 commit。遠端 main 另行讀回，仍保留原課版本。

### 步驟 4：先 fork，再把 origin 指向自己的 repository

fork 是 GitHub 上屬於你的課程副本；clone 是下載到本機。直接 clone 原作者的 repository 可以閱讀與修改本地檔案，卻不表示能 push 回原作者的帳號。

本次在 GitHub 建立 `ed3c/ai-engineering-from-scratch`，確認頁面標示 forked from 原課，再透過 SSH clone。練習副本是從本機主副本建立，初始 origin 因此指向本機路徑；推送前明確把它改為自己的 GitHub fork。

```bash
git remote set-url origin git@github.com:ed3c/ai-engineering-from-scratch.git
git remote get-url origin
git push -u origin my-progress
```

這三步分別是指定目的地、讀回目的地與真正推送。最後本機與 GitHub 都讀回 `960f0b5cc6094163135c2e5fc75cce2079070233`，才確認推送成功。沒有向原課上游送出 PR，也沒有把練習推到遠端 main。

## 用它（Use It）：每次練習都留下可閱讀的差異

下次開始時，進入練習副本，確認所在分支與工作狀態。完成一個小步驟，就檢查差異、選定檔案、以說明原因的訊息提交，再推送 my-progress。不要把「程式能跑」與「最新成果已經備份」當成同一件事。

若要重新開發，先使用 `git status` 確認有沒有尚未保存的修改，再決定如何取得遠端更新；本課不需要為了完成基本備份就引入 rebase、cherry-pick 或 submodule。

本次文件與 Git 操作直接在本機完成，不需要 Colab。GitHub 是保存遠端 repository 的位置；Colab 是執行程式的環境，兩者處理不同問題。把 Git 練習搬到臨時 runtime，反而還得處理檔案持久性與另一份登入。

## 補充實作：推送後，能否從 GitHub 取回同一份成果？

原課練習要求推送到自己的 fork。要把「遠端有這個分支」和「這份成果真的能取回」連起來，可以多做一次全新 clone。本次在 my-progress 新增 `learning-artifacts/git-collaboration/review.md`，只把這個檔案放進暫存區；檢查差異後提交，再推送。

推送前，遠端分支仍是 `960f0b5c`；推送後，本機 HEAD 與 GitHub 分支都變成 `3d9a80386b195fb7156b2aedc126a4e48a39390d`。接著建立新的 recovery 目錄，不借用原工作目錄裡尚未提交的內容：

```bash
git clone --single-branch --branch my-progress \
  git@github.com:ed3c/ai-engineering-from-scratch.git recovery
git -C recovery rev-parse HEAD
git -C recovery show HEAD:learning-artifacts/git-collaboration/review.md
```

這組命令需要新的 recovery 目錄與可用的 GitHub SSH 連線；其他讀者應換成自己的 fork。本次全新副本的 HEAD 相同，筆記內容也逐位元組相同。舊的 `snapshot=1` 與 `snapshot=2` 仍可從各自 commit 讀出。這說明 push 後可取回已提交內容與歷史，卻不表示原目錄裡未追蹤的檔案、忽略的模型、套件環境也跟著備份。

合併也另外重做：新建一個從遠端 main 開始的獨立副本，先確認它仍在 `968da079`，再 fetch 練習副本的 my-progress，執行 `git merge --ff-only FETCH_HEAD`。本機 main 前進到新筆記的 commit；再次讀取 GitHub main，仍是原課版本。fetch 取得物件與引用資訊，merge 才整合到目前分支；兩者都不會替你把 main 推到 GitHub。[Git fetch 官方說明](https://git-scm.com/docs/git-fetch)

這次只驗證原課所需的基本分支與 fast-forward 路徑。沒有兩人同改一行的情境，因此不能把無衝突合併的結果當作衝突處理已驗收。

## 練習（Exercises）：原課三題的操作與答案

### 練習 1：fork、clone、建立 my-progress、提交並推送

這條流程已完整執行。[第一次提交](https://github.com/ed3c/ai-engineering-from-scratch/commit/4e5a5abc0abe9ba857e5be58958c34b20135b345)保存暫存區的1；[第二次提交](https://github.com/ed3c/ai-engineering-from-scratch/commit/960f0b5cc6094163135c2e5fc75cce2079070233)保存再次 add 的2。GitHub 分支與本機最後 commit 相同，原課上游未被修改。

這一道題真正要建立的是「自己的修改有可追溯歷史，並能送到自己有權限的遠端」。fork 解決遠端歸屬，分支隔離練習，commit 保存版本，push 才傳送版本；每個動作都有不同作用。

### 練習 2：排除模型 checkpoint 檔案

原課根目錄其實已包含三種權重副檔名的忽略規則。本次仍在練習目錄寫一份小型 `.gitignore`，讓這一題的規則與驗證可以獨立閱讀，不修改上游的全域規則。

```gitignore
*.pt
*.pth
*.safetensors
```

用三個小型文字占位檔模擬副檔名，不下載任何模型。`git check-ignore -v` 逐一指出練習目錄的規則與行號；再明確嘗試加入其中一個被忽略檔案，Git 以結束碼1拒絕。最後提交只包含 `.gitignore` 與文字練習檔，模型占位檔仍未受追蹤。

有兩個細節會影響日後實作。第一，Git 可以追蹤二進位檔，只是大型模型權重不適合當一般原始碼反覆提交；原課的忽略建議不是「Git 完全不支援二進位」。第二，[gitignore 官方說明](https://git-scm.com/docs/gitignore)指出，忽略規則作用於尚未追蹤的檔案；已經提交的檔案不會因新增規則就自動消失。

所以要在第一次 add 前建立規則。權重另存時，也應保存取得位置與版本，避免只留下檔名，卻無法找回當時使用的模型。這是對忽略規則的實務解釋，不是另加一項需要等待作答的課程題目。

### 練習 3：從歷史讀出課程如何修正

先讀整個 repository 的近期 `git log --oneline`，能看到網站重新建置與課程連結修正。再把範圍縮到這一課，找出課文自己的演變：

```bash
git log --oneline -- phases/00-setup-and-tooling/02-git-and-collaboration
git show d1cb9d19 -- phases/00-setup-and-tooling/02-git-and-collaboration/docs/en.md
```

歷史顯示 `2b62eda3` 最初加入 Git 課，`963b4d8e` 後來補上學習目標與測驗。更有用的是[這次課文修正](https://github.com/rohitg00/ai-engineering-from-scratch/commit/d1cb9d1933f121140694fd55873110ff7602e463)：原範例直接 clone 作者的 repository，後來改成先 fork，再 clone 自己的副本，第一道練習也同步補上 fork。

原因可以從實際 diff 讀出：一般學員沒有上游寫入權限，所以「可以 clone」不能推導成「可以 push」。讀 log 找到變更，再用 show 看修改內容，才把歷史轉成現在可用的判斷。

## 補充實作：為什麼加了忽略規則，檔案仍被 Git 追蹤？

規則寫對，不代表它能回頭取消既有追蹤。本次另建一個只在本機存在的小型 repository：先提交文字占位檔 `already-tracked.pt`，再寫入 `*.pt`，同時建立尚未追蹤的 `untracked.pt`。兩個檔案都很小，不是模型。

結果是：`git ls-files already-tracked.pt` 仍列出已追蹤檔；`git check-ignore -v untracked.pt` 則指出新檔命中了忽略規則。因此看到被追蹤的權重檔時，先查它是否早已進入 index，不要只反覆修改副檔名規則。

如果確定某檔案今後應留在磁碟、退出版本追蹤，可以針對該檔案執行：

```bash
git rm --cached already-tracked.pt
git diff --cached
```

本次實測後，工作檔仍在，index 不再列出它，忽略規則開始生效。`--cached` 的作用是從 index 移除；若要把這個停止追蹤的決定保存成專案歷史，還需要檢查 staged diff 並提交。這次只是本機控制，沒有推送占位檔或修改原課。[Git rm 官方說明](https://git-scm.com/docs/git-rm)

這個操作不會抹去過去 commit 裡的檔案，也不會立即縮小既有歷史。對模型檔，最好在第一次 add 前設定規則，另外保存權重的取得方式與版本；別把忽略規則當成歷史清除工具。

## 原課概念題：直接回答並解釋理由

以下對照這一課實際的[五題題庫](https://github.com/rohitg00/ai-engineering-from-scratch/blob/968da0791b83917c9d8a5ba197ff190fa0b24093/phases/00-setup-and-tooling/02-git-and-collaboration/quiz.json)，提供參考答案，不要求讀者先作答才繼續文章。

**版本控制解決什麼？** 保存可檢查的變更歷史，讓人能比較版本、回到已保存的狀態並協作。它不會自動修好程式，也不會讓程式算得更快。本次能分別取回1與2，就是保存不同版本的具體結果。

**Repository 包含什麼？** 它管理提交的檔案快照、歷史及相關物件；搭配工作目錄供人編輯。不要把課文的概括描述理解成磁碟上所有檔案都已備份：剛建立但未 add 的筆記、被忽略的模型，都不在已提交的快照中。

**保存與備份的順序為何？** 先 add 選定內容，再 commit 保存本機版本，最後 push 到遠端。若 add 之後又改檔案，就要重新核對暫存區；若只 commit 沒 push，另一台機器不能從 GitHub 取到新版本。

**建立並切換實驗分支做了什麼？** 原課的 `git checkout -b experiment/new-optimizer` 在目前 commit 建立新分支並切換到它；main 不會因此自行前進。這次為保留共享工作目錄的分支，從 clone 起就指定工作分支，功能目標相同，但不是實際執行過那條切換命令。

**為何排除 checkpoint 副檔名？** 這些格式常承載大型模型權重，反覆放入一般 Git 歷史會增加保存與傳輸負擔。原課題庫要辨認的是這個儲存選擇，不是「Git 不支援二進位」，也不是每個該副檔名都必然巨大。需要另外保存取得位置與版本，才不會只保住程式，卻無法重現所用模型。

三道原課實作及以上概念說明，都可以回到[本次複驗紀錄](https://github.com/ed3c/medium-compiler/blob/main/articles/evidence/git-collaboration-recheck.json)核對。它記錄代理執行的命令、回傳與限定範圍，沒有替任何人登記測驗分數或學習進度。

## 關鍵術語：用本次操作理解它們

**Repository** 保存版本歷史及相關物件，並可搭配工作目錄讓你編輯。**Commit** 記錄一次專案快照及其父提交；本次兩個 commit 讓1與2都能被查閱。只存 commit 不代表全部外部依賴、資料與模型也一併保存。

**Branch** 是指向 commit 的名稱。my-progress 隨兩次提交往前移，main 在合併前仍停在原處。**Merge** 把另一條歷史整合到目前分支；本次是 fast-forward，不涉及衝突解決。

**Remote** 是另一個 repository 的連線設定；origin 只是常用名稱，實際位置必須讀回確認。它既可能是本機另一個副本，也可能是 GitHub。**Fork** 是 GitHub 維護的上游／個人副本關係；**clone** 則是建立本機 repository 的操作。

## 本次交付與接續課程

可重看的成果包括兩個 GitHub 提交、可重用的忽略規則，以及[本次操作驗證紀錄](https://github.com/ed3c/medium-compiler/blob/main/articles/evidence/git-collaboration.json)。本機目錄在 `~/ai-engineering-learning/git-collaboration/`，保留 main 主副本、my-progress 練習副本與操作結果。這些是代理完成的實作證據，沒有代填原網站的個人測驗。

前面的操作已回答為什麼要分開 add、commit、push，以及何時才算推送成功。接著要處理的是：程式版本保存了，Python 套件版本如何一起重現？依同一條 Software Engineering Fundamentals 路線，[下一課是 Python Environments](https://aiengineeringfromscratch.com/lesson?path=phases/00-setup-and-tooling/06-python-environments&learningPath=software-engineering-fundamentals)。它是路線中的第三課，並非依 Phase 0 目錄數字直接前往 GPU 課。

本篇核對的[課文來源](https://github.com/rohitg00/ai-engineering-from-scratch/blob/968da0791b83917c9d8a5ba197ff190fa0b24093/phases/00-setup-and-tooling/02-git-and-collaboration/docs/en.md)固定在本次 fork 的上游版本。本文保留原課的學習目標、四個建立步驟、Use It、三道 Exercises 與 Key Terms；本次兩份 checkout、SSH 連線與暫存區對照，是為解釋實際操作而補上的內容。
