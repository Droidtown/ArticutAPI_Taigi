# ArticutAPI_Taigi (文截台語 NLP 工具)

基於 [卓騰語言科技](https://api.droidtown.co) 研發的 <u>Articut 中文 NLP 系統</u>，**ArticutAPI_Taigi** 是專供台語文使用的斷詞/詞性標記/命名實體辨識 NLP 工具。

由於 **Articut_Taigi** 是基於 Articut 開發的台語文 NLP 工具，它的免費字數即直接受益於卓騰語言科技提供 Articut NLP 系統使用者的 2000 字/小時。此外，因 Articut 計算字數時不會將字典詞彙計入，而 **Articut_Taigi** 的台語文功能有很大一部份是依賴台文字典實現的，因此實際上消耗的字數會比較少。

若 2000 字/小時的免費額度不夠您的需求使用的話，可自行採購 Articut 的字數額度，取得其 API key 即可使用。我相信絕大多數的情況下，[300 元(十萬字)] 的方案就已經相當夠使用了。([採購連結](https://api.droidtown.co/product/) )

即便是台灣最多人使用的國語，放在商業現實的「中國普通話」面前都算是沒什麼市場價值的小語種，就更別提台閩語、客語、南島語…等本土語言了。因此這些本土語言的 NLP 工具的開發有賴個人支持。我也只能在工餘的時間盡力貢獻。

若您有意贊助 **Articut_Taigi (文截台語 NLP  工具)** 及其後各種台灣本土語言 NLP 工具 (e.g., Articut_Hakka, Articut_Amis, ... 等) 的開發，歡迎直接贊助開發者本人小弟在下我： [http://paypal.me/donatepeterwolf](http://paypal.me/donatepeterwolf) 。

### 主要功能：
- 全白話字斷詞暨詞性/NER 標記  (e.g., "歡迎逐家做伙來做台灣語言")
- 全台羅拼音斷詞暨詞性/NER 標記 (e.g., "huan-gîng ta̍k-ke tsò-hué lâi tsò tâi-uan gí-giân")
- 白話字台羅拼音混打斷詞暨詞性/NER 標記 (e.g., 歡迎ta̍k-ke做伙來做 tâi-uan 語言")
- 自訂詞典

### 進階功能：
- 白話字轉譯台羅拼音
- 台羅拼音轉譯白話字 (施作中…)

### 網頁操作介面：
[國立清華大學語言學研究所:: 本土語言斷詞系統](https://taiwan-lingu.ist/segment/)


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

## 使用自訂詞典

**ArticutAPI_Taigi** 支援自訂詞典的設定。詞典需存為一 .json 檔，且內容格式如下：

```json
{
    "ACTION_verb"           : [ ], #普通動詞
    "ACTION_lightVerb"      : [ ], #輕動詞 (e.g., 把、使…)
    "ACTION_quantifiedVerb" : [ ], #量化動詞 (e.g., 呷看嘜、聽看看…等表示動作只做了輕微嚐試的動詞)
    "ACTION_eventQuantifier": [ ], #事件量化詞 (e.g., 趟、圈…等表用以計算事件發生次數的詞彙)
    "ASPECT"                : [ ], #時態標記詞 (e.g., 看過、吃過…等詞中的「過」)
    "AUX"                   : [ ], #助動詞 (e.g., 為、是…等)
    "CLAUSE_particle"       : [ ], #語氣詞 (e.g., 啊、嘛…等)
    "CLAUSE_Q"              : [ ], #疑問詞 (e.g., 嗎、是不是…等)
    "ENTITY_classifier"     : [ ], #量詞 (e.g., 一部車的「部」、一頭牛的「頭」)
    "ENTITY_DetPhrase"      : [ ], #冠詞詞組 (e.g., 這個、那位…等)
    "ENTITY_measurement"    : [ ], #量測詞組 (e.g., 兩公斤、30尺…等)
    "ENTITY_noun"           : [ ], #普通名詞
    "ENTITY_num"            : [ ], #數字
    "ENTITY_person"         : [ ], #人名
    "ENTITY_possessive"     : [ ], #所有格代名詞 (e.g., 我的、他們的)
    "ENTITY_pronoun"        : [ ], #代名詞 (e.g., 你、他、哥哥…等)
    "FUNC_conjunction"      : [ ], #連結詞 (e.g., 和、與…等)
    "FUNC_degreeHead"       : [ ], #程度詞中心語 (e.g., 很、非常…等)
    "FUNC_inner"            : [ ], #功能詞，不涉及其它句子存在 (e.g., 的)
    "FUNC_inter"            : [ ], #功能詞，暗示其它句子存在 (e.g., 而且)
    "FUNC_negation"         : [ ], #否定詞 (e.g., 不、沒、嘸…等)
    "IDIOM"                 : [ ], #成語、俚語、俗語
    "LOCATION"              : [ ], #地名
    "MODAL"                 : [ ], #情態動詞 (e.g., 會、能…等)
    "MODIFIER"              : [ ], #形容詞
    "MODIFIER_color"        : [ ], #顏色形容詞
    "QUANTIFIER"            : [ ], #量化詞 (e.g., 八成、一些…等)
    "RANGE_locality"        : [ ], #地點方位詞 (e.g., 附近、旁邊…等)
    "RANGE_period"          : [ ], #時間方位詞 (e.g., 之前、以後…等)
    "TIME_justtime"         : [ ], #短時間詞
    "TIME_season"           : [ ] #季節時間詞
}
```
使用時，只要在 .parse() 中指定字典檔即可：

```python
from ArticutAPI_Taigi import ArticutTG
from pprint import pprint
username = "" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
articutTG = ArticutTG(username, apikey)
inputSTR = "歡迎逐家做伙來做台灣語言"
resultDICT = articutTG.parse(inputSTR, level="lv2", userDefinedDictFILE=""my_dictionary.json") 
pprint(resultDICT)
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
