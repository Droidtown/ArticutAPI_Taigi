# ArticutAPI_Taigi

# This Project is Still Under Development!

基於卓騰語言科技研發的 Articut 中文 NLP 系統，ArticutAPI_Taigi 是專供台語文使用的斷詞/詞性標記/命名實體辨識 NLP 工具。

Taigi CWS/POS/NER natural language processing tool with Articut as kernel.

### 主要功能：
- 全白話字斷詞暨詞性/NER 標記  (e.g., "歡迎逐家做伙來做台灣語言")
- 全台羅拼音斷詞暨詞性/NER 標記 (e.g., "huan-gîng ta̍k-ke tsò-hué lâi tsò tâi-uan gí-giân")
- 白話字台羅拼音混打斷詞暨詞性/NER 標記 (e.g., 歡迎ta̍k-ke做伙來做 tâi-uan 語言")

### 進階功能：
- 白話字轉譯台羅拼音
- 台羅拼音轉譯白話字 (施作工…)

### 網頁操作介面：
[國立清華大學語言學研究所:: 本土語言斷詞系統](https://taiwan-lingu.ist/segmentation/)


## I. 基本操作：斷詞(WS)/詞性標記(POS)/命名實體辨識(NER)

```python
from ArticutAPI_Taigi import ArticutTG
from pprint import pprint
username = "" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
articutTG = ArticutTG(username, apikey)
inputSTR = "歡迎逐家做伙來做台灣語言"
resultDICT = articutTG.parse(inputSTR, level="lv2") #lv2 為預設值
pprint(resultDICT)
```

### 回傳結果
```python
{'exec_time': 0.17456531524658203,
 'level': 'lv2',
 'msg': 'Success!',
 'result_obj': [[{'pos': 'ACTION_verb', 'text': '歡迎'},
                 {'pos': 'ENTITY_pronoun', 'text': '逐家'},
                 {'pos': 'MODIFIER', 'text': '做伙'},
                 {'pos': 'ACTION_verb', 'text': '來'},
                 {'pos': 'ACTION_verb', 'text': '做'},
                 {'pos': 'LOCATION', 'text': '台灣'},
                 {'pos': 'ENTITY_noun', 'text': '語言'}]],
 'result_pos': ['<ACTION_verb>歡迎</ACTION_verb><ENTITY_pronoun>逐家</ENTITY_pronoun><MODIFIER>做伙</MODIFIER><ACTION_verb>來</ACTION_verb><ACTION_verb>做</ACTION_verb><LOCATION>台灣</LOCATION><ENTITY_noun>語言</ENTITY_noun>'],
 'result_segmentation': '歡迎/逐家/做伙/來/做/台灣/語言',
 'status': True,
 'version': 'v261',
 'word_count_balance': 1965}

```
---
## II. 進階操作：白話字轉台羅拼音
```python
from ArticutAPI_Taigi import ArticutTG
from pprint import pprint
username = "" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
articutTG = ArticutTG(username, apikey)
inputSTR = "歡迎逐家做伙來做台灣語言"
resultDICT = articutTG.parse(inputSTR, level="lv3") #將 lv2 的預設值改為 lv3
pprint(resultDICT)
```
### 回傳結果
```python
{'entity': [[(179, 181, '語言')]],
 'exec_time': 0.1532421112060547,
 'level': 'lv3',
 'msg': 'Success!',
 'person': [[(45, 47, '逐家')]],
 'site': [[(153, 155, '台灣')]],
 'status': True,
 'time': [[]],
 'utterance': 'huan-gîng╱ta̍k-ke╱(tsò-hué/tsuè-hé)╱lâi╱(tsò/tsuè)╱tâi-(uan/uân)╱(gí-giân/gú-giân)',
 'version': 'v261',
 'word_count_balance': 1965}
```
