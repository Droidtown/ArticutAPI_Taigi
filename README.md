# ArticutAPI_Taigi

# This Project is Still Under Development!

基於 Articut，ArticutAPI_Taigi 是專供台語文使用的斷詞/詞性標記/命名實體辨識 NLP 工具。

Taigi CWS/POS/NER natural language processing tool with Articut as kernel.

## 操作

```python
from ArticutAPI_Taigi import ArticutTG
from pprint import pprint
username = "" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
articutTG = ArticutTG(username, apikey)
inputSTR = "歡迎ta̍k-ke做伙來做台灣語言"
resultDICT = articutTG.parse(inputSTR)
pprint(resultDICT)
```

### 回傳結果
```python
{'exec_time': 0.04989504814147949,
 'level': 'lv1',
 'msg': 'Success!',
 'result_obj': [[{'pos': 'ACTION_verb', 'text': '歡迎'},
                 {'pos': 'ENTITY_pronoun', 'text': 'ta̍k-ke'},
                 {'pos': 'MODIFIER', 'text': '做伙'},
                 {'pos': 'ACTION_verb', 'text': '來'},
                 {'pos': 'ACTION_verb', 'text': '做'},
                 {'pos': 'LOCATION', 'text': '台灣'},
                 {'pos': 'ENTITY_noun', 'text': '語言'}]],
 'result_pos': ['<ACTION_verb>歡迎</ACTION_verb><ENTITY_pronoun>ta̍k-ke</ENTITY_pronoun><MODIFIER>做伙</MODIFIER><ACTION_verb>來</ACTION_verb><ACTION_verb>做</ACTION_verb><LOCATION>台灣</LOCATION><ENTITY_noun>語言</ENTITY_noun>'],
 'result_segmentation': '歡迎/ta̍k-ke/做伙/來/做/台灣/語言',
 'status': True,
 'version': 'v254',
 'word_count_balance': 1943}
```
