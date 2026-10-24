# 第二輪有界 Reader report

現行凍結內容83項均為PASS_BOUNDED：81項沿用第一次exact unchanged內容判讀，2項完整新判讀。不是新83項全獨立重測。第一次全部audit/report/FAIL保留，未改驗收criteria。

actual delta：Water p22（UI第23段）及Course p7（UI第8段），各在中英兩頁同步更換note與首條premise。其餘81項完整annotation在兩語皆exact unchanged。四份批准Markdown bytes完全不變；四頁正文article HTML完全不變。所有reading markup、source links、短cue、Active sentences/cues/oracles都不變。故不能將變動數寫為「1項修稿／82項沿用」。

Water p22新note說「此實作…不修改 input list；item assignment會寫入item，但這裡沒有這種assignment」，首premise又限定原程式並明說source沒有將它當所有mutation的必要條件。其明鏈#alg-p-22原文為「An assignment targeting an item such as height[left] would write that item; no such assignment occurs here」，且解釋讀取/local binding/integer重綁定的效果。新註解保持充分例示與展示程式範圍，不再倒推唯一機制。原F1 counterexample仍有效：合法起始height=[2,5]可經append修改而沒有item assignment；新註解已不推出其否定。F1在第二份凍結內容RESOLVED，第一輪FAIL永久保留。

Course p7新note說「此comprehension對每門課分別求值[]，會產生獨立inner lists」，新context明示這是source做法的效果，不宣稱只有[]語法可建獨立lists。明鏈#alg-p-7的「Evaluating [] separately for each course makes independent inner lists」只給這個充分方向；相鄰原文分清[[]]*V共享mutable list、[0]*V配integer slot replacement安全。合法V=2的shared-list append反例和完整context一致。另一方面list()逐課建立也能獨立，說明不能加唯一語法必要條件；本反例只檢查推論方向，不替註解補來源前提。

對歷史判讀的限制：原Course p7的「每次求值[]才有獨立inner lists」也有必要方向歧義；第一輪給PASS而未單列。本輪對照actual修稿才明確記錄此歷史風險。沒有回寫原結果，也沒有冒稱第一次已抓到它。新文字已去除此歧義，現行沒有追加FAIL。

兩項新判讀都沒有時間checkpoint要求，故不添加先後順序前提。完整reading、bundle、Active sentence/cue/oracle已重讀，與首次內容相同；其Active只談指定重綁定或shared-list repetition，明鏈source直接支持。短question仍只是閱讀cue，沒有當成獨立theorem驗收。

source losslessness、其餘chunk attachment/cue/Active的既有有界判斷可沿用，理由是完整內容與source exact unchanged，並非本輪又測得新證據。全部83行連同note/context、完整明鏈中英source引文、必要前提與附近反例在audit.json；audit.tsv及audit.md供掃讀。actual-delta.json記逐頁實際變動。

範圍依舊只有指定frozen HTML/source文字與本人第一次原稿/audit。沒有Ownerledger、skill、expected answer、其他讀者trace或repository history。未fetch外部source links，未開瀏覽器、聽音訊、跑runtime、收真人資料或增加發音證據；不宣稱人類速度、學習效果或一般穩定性。same Reader/same thread作修稿後有界複核，不是新獨立Reader session。
