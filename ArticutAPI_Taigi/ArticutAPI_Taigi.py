#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import platform
import re
import tempfile
import unicodedata
from pprint import pprint

from ArticutAPI import Articut
try:
    from .defaultDict import Taigi_Lexicon
    from .posShift import shiftRule
except:
    from defaultDict import Taigi_Lexicon
    from posShift import shiftRule

BASEPATH = os.path.dirname(os.path.abspath(__file__))

class ArticutTG:
    def __init__(self, username="", apikey="", usernameENG="", apikeyENG=""):
        #self.articut = Articut(username=username, apikey=apikey, url="http://10.1.1.182:50269")
        self.articut = Articut(username=username, apikey=apikey)
        self.articutENG = Articut(username=usernameENG, apikey=apikeyENG, url="https://nlu.droidtown.co")
        self.posPat = re.compile("<[^<]*>([^<]*)</([^<]*)>")
        self.TLPat = re.compile("\s?[\-a-zA-Záíúéóàìùèòâîûêôǎǐǔěǒāīūēō̋̍]+(-+[a-zA-Záíúéóàìùèòâîûêôǎǐǔěǒāīūēō̋̍]+)*\s?")
        self.userDefinedDICT = {}
        self.cjkPAT = re.compile('[\u4e00-\u9fff]')
        self.moeCSV = [[t.replace("\n", "") for t in l.split(",")] for l  in open("{}/defaultDict/moe_dict/詞目總檔.csv".format(BASEPATH), "r", encoding="utf-8").readlines()]
        self.DT_TL = Taigi_Lexicon.DT_TL
        self.purgePat = re.compile("</\w+(_\w+)?><\w+(_\w+)?>|</?\w+(_\w+)?>")
        self.shiftRule = shiftRule
        self.defaultDICT = Taigi_Lexicon.dictCombiner()
        self.legacyLIST = ["", "𪜶𪹚𫝏𫝘𫝙𫝛𫝞𫝺𫝻𫝾𫞭𫞻𫞼𫟂𫟊𫟧𫠛𫣆"]
        self.personPat = re.compile("(?<=<ENTITY_person>)[^<]+(?=</ENTITY_person>)")
    def _pos2Obj(self, posLIST):
        resultLIST = []
        for pos in posLIST:
            if '</' in pos:
                textPosLIST = [[p.group(1), p.group(2)] for p in self.posPat.finditer(pos)]
                # group(0) <ACTION_verb>結帳</ACTION_verb>
                # group(1) 結帳
                # group(2) ACTION_verb
                objLIST = []
                for txt, p in textPosLIST:
                    objLIST.append({
                        "text": txt,
                        "pos": p,
                    })
                if objLIST:
                    resultLIST.append(objLIST)
                else:
                    resultLIST.append([{
                        "text": pos,
                        "pos": 'PUNCTUATION',
                    }])
            else:
                resultLIST.append([{
                    "text": pos,
                    "pos": 'PUNCTUATION',
                }])
        return resultLIST

    def _2TL(self, posLIST):
        '''
        把 posLIST 裡的每一個詞，一一轉為 TL (台羅拼音)
        '''
        resultLIST = []
        for p in posLIST: #p 是一句
            for word in p:
                if "LATIN" in unicodedata.name(word["text"][0]):
                    resultLIST.append(word["text"])
                elif word["text"] in self.DT_TL:
                    resultLIST.append(self.DT_TL[word["text"]])
                elif word["text"] in [token[2] for token in self.moeCSV]:
                    tokenLIST = []
                    for token in self.moeCSV[1:]:
                        if token[2] == word["text"]:
                            tokenLIST.append(token[3])

                    if len(tokenLIST) > 1:
                        resultLIST.append("({})".format("/".join(tokenLIST)))
                    elif len(tokenLIST) == 1:
                        if "/" in tokenLIST[0]:
                            resultLIST.append("({})".format(tokenLIST[0]))
                        else:
                            resultLIST.append("{}".format(tokenLIST[0]))
                    else:
                        pass
                    tokenLIST = []
                else:
                    wordLIST = []
                    tokenLIST = []
                    for t in word["text"]:
                        for token in self.moeCSV:
                            if len(token[2]) == 1 and t == token[2]:
                                tokenLIST.append("{}".format(token[3]))

                        if len(tokenLIST) > 1:
                            wordLIST.append("({})".format("/".join(tokenLIST)))
                        elif len(tokenLIST) == 1:
                            wordLIST.append("{}".format(tokenLIST[0]))
                        tokenLIST = []
                    resultLIST.append("-".join(wordLIST))
        return resultLIST

#<ToDo>
    #def _2POJ(self, postLIST):
        #'''
        #把 posLIST 裡的每一個詞，一一轉為 POJ (白話字拼音)
        #'''
        #resultLIST = []
        #return resultLIST

    #def _2Word(self, posLIST):
        #'''
        #每次從 posLIST 中取一個詞彙，反查這個詞彙是 TL 或 POS 的拼音，依該拼音把同音詞彙找出來，並把這個詞彙同音的台語漢字加入回傳結果中。
        #'''
        #resultLIST = []
        #return resultLIST

    #def _TL2Word(self, TLLIST):
        #'''
        #把 TLLIST (台羅拼音)裡的每一個詞，一一轉為台語漢字
        #'''
        #resultLIST = []
        #return resultLIST

    #def _POJ2Word(self, POJLIST):
        #'''
        #把 POJLIST (白話字拼音)裡的每一個詞，一一轉為台語漢字
        #'''
        #resultLIST = []
        #return resultLIST
#</ToDo>
    def _mixedInputDetector(self, inputSTR):
        TLLIST = [t.group() for t in self.TLPat.finditer(inputSTR)]
        with open(self.TaigiDictFILE.name) as f:
            userDefinedDICT = json.load(f)

        #<特殊區塊：如果使用者有購買英文版 Articut 的使用額度，將調用英文人名偵測。>
        #<否則本功能會在每小時 2000 字免費額度用盡後失效，待下一個小時的免費額度啟用時才恢復>
        knownLIST = []
        for i in TLLIST:
            resultDICT = self.articutENG.parse(i, level="lv1")
            if resultDICT["status"] == True and resultDICT["msg"] == "Success!":
                if "<ENTITY_person>{}</ENTITY_person>".format(i) in "".join(resultDICT["result_pos"]):
                    knownLIST.append(i)
                    userDefinedDICT["ENTITY_person"].append(i)
                    self.userDefinedDICT["ENTITY_person"].append(i)
            else:
                pass
        TLLIST = list(set(TLLIST)-set(knownLIST))
        #</特殊區塊：如果使用者有購買英文版 Articut 的使用額度，將調用英文人名偵測>
        #</否則本功能會在每小時 2000 字免費額度用盡後失效，待下一個小時的免費額度啟用時才恢復>

        if TLLIST == []:
            pass
        else:
            #with open(self.userDefinedDictFILE.name) as f:
                #userDefinedDICT = json.load(f)
            if "_ArticutTaigiUserDefined" in userDefinedDICT.keys():
                userDefinedDICT["_ArticutTaigiUserDefined"].extend(TLLIST)
            else:
                userDefinedDICT["_ArticutTaigiUserDefined"] = TLLIST
            if platform.system() == "Windows":
                self.userDefinedDictFILE = tempfile.NamedTemporaryFile(mode="w+", delete=False)
            else:
                self.userDefinedDictFILE = tempfile.NamedTemporaryFile(mode="w+")
            json.dump(userDefinedDICT, self.userDefinedDictFILE)
            self.userDefinedDictFILE.flush()
        return None

    def _spaceWalker(self, inputDICT):
        '''
        移除非 CJK 字元前後的空格
        '''
        fposPat = re.compile("<UserDefined>\s")
        pposPat = re.compile("\s</UserDefined>")
        posPat = re.compile("</?\w_?[^>]+?>")
        for i in range(0, len(inputDICT["result_pos"])):
            inputDICT["result_pos"][i] = re.sub(fposPat, " <UserDefined>", inputDICT["result_pos"][i])
            inputDICT["result_pos"][i] = re.sub(pposPat, "</UserDefined> ", inputDICT["result_pos"][i])
            inputDICT["result_pos"][i] = inputDICT["result_pos"][i].strip()
        try:
            inputDICT["result_pos"].remove("")
        except:
            pass

        tmpSTR = ""
        for i in range(0, len(inputDICT["result_pos"])):
            tmpSTR = tmpSTR + re.sub(posPat, "<DROIDTOWN_TKBD>", inputDICT["result_pos"][i])
            tmpSTR = tmpSTR.replace("<DROIDTOWN_TKBD><DROIDTOWN_TKBD>", "/").replace("<DROIDTOWN_TKBD> <DROIDTOWN_TKBD>", "/ /").replace("<DROIDTOWN_TKBD>", "/")
        inputDICT["result_segmentation"] = tmpSTR
        return inputDICT

    def _posShift(self, posLIST):
        for i in range (0, len(posLIST)):
            if len(posLIST[i]) == 1:
                pass
            else:
                for pat in self.shiftRule:
                    shiftLIST = [(g.start(), g.end(), g.group(0)) for g in reversed(list(pat[0].finditer(posLIST[i])))]
                    for s in shiftLIST:
                        adjustedSTR = s[2]
                        for adjust_s in pat[1]:
                            adjustedSTR = adjustedSTR.replace(adjust_s, pat[2][pat[1].index(adjust_s)])
                        posLIST[i] = "{}{}{}".format(posLIST[i][:s[0]], adjustedSTR, posLIST[i][s[1]:])
        return posLIST

    def _pos2Seg(self, posLIST):
        resultSTR = ""
        for s in posLIST:
            resultSTR = resultSTR + re.sub(self.purgePat, "╱", s)
        return resultSTR

    def parse(self, inputSTR, level="lv2", userDefinedDictFILE=None, convert=None):
        for i in self.legacyLIST[0]:
            inputSTR = inputSTR.replace(i, self.legacyLIST[1][self.legacyLIST[0].index(i)])

        if level=="lv3":
            tgLV = "lv3"
            level = "lv2"
            if convert == None:
                convert = "TL"
            else:
                if convert.upper() in ("TL", "POJ", "WORD"):
                    convert = convert.upper()
                else:
                    raise
        else:
            tgLV = level

        if platform.system() == "Windows":
            self.TaigiDictFILE = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        else:
            self.TaigiDictFILE = tempfile.NamedTemporaryFile(mode="w+")

        self.userDefinedDICT = self.defaultDICT
        if userDefinedDictFILE == None:
            pass
        else:
            with open(userDefinedDictFILE, encoding="utf-8") as f:
                userDefinedDICT = json.load(f)
            for k in userDefinedDICT.keys():
                try:
                    tmpLIST = userDefinedDICT[k]
                    for POS in self.defaultDICT.keys():
                        self.defaultDICT[POS] = list(set(self.defaultDICT[POS])-set(tmpLIST))
                    if k in self.userDefinedDICT.keys():
                        tmpLIST.extend(self.userDefinedDICT[k])
                    tmpLIST = list(set(tmpLIST))
                    self.userDefinedDICT[k].extend(tmpLIST)
                except KeyError:
                    self.userDefinedDICT[k] = tmpLIST

        #<利用 Articut 建立人名字典>
        checkingPersonDICT = self.articut.parse(inputSTR, level="lv1")
        personLIST = [p[-1] for p in [e[-1] for e in self.articut.getPersonLIST(checkingPersonDICT,  includePronounBOOL=False) if e != []] if p!=[]]
        if personLIST != []:
            self.userDefinedDICT["ENTITY_person"] = [p for p in personLIST if p[0] not in "伊毋" and p[-1] not in "舅叔嬸嫂婆爺爹娘父公爸母某翁姊姐妹兄弟字門梯鄉塗"]

        #</利用 Articut 建立人名字典>

        json.dump(self.userDefinedDICT, self.TaigiDictFILE)
        self.TaigiDictFILE.flush()

        self._mixedInputDetector(inputSTR)
        articutResultDICT = self.articut.parse(inputSTR, level=level, userDefinedDictFILE=self.TaigiDictFILE.name)
        articutResultDICT = self._spaceWalker(articutResultDICT)
        POScandidateLIST = []
        for tkn in articutResultDICT["result_segmentation"].split("/"):
            for k in self.userDefinedDICT.keys():
                if tkn in self.userDefinedDICT[k]:
                    POScandidateLIST.append(("<UserDefined>{}</UserDefined>".format(tkn), "<{0}>{1}</{0}>".format(k, tkn)))

        for i, s in enumerate(articutResultDICT["result_pos"]):
            for p in POScandidateLIST:
                articutResultDICT["result_pos"][i] = articutResultDICT["result_pos"][i].replace(p[0],p[1])
        print("src", articutResultDICT["result_pos"])
        articutResultDICT["result_pos"] = self._posShift(articutResultDICT["result_pos"])
        articutResultDICT["result_obj"] = self._pos2Obj(articutResultDICT["result_pos"])
        articutResultDICT["result_segmentation"] = self._pos2Seg(articutResultDICT["result_pos"])

        if tgLV in ("lv1", "lv2"):
            return articutResultDICT
        elif tgLV == "lv3":
            resultDICT = {"person": self.articut.getPersonLIST(articutResultDICT),
                          #"event": articutResultDICT["event"],
                          "time": self.articut.getTimeLIST(articutResultDICT),
                          "site": self.articut.getLocationStemLIST(articutResultDICT),
                          "entity":  self.articut.getNounStemLIST(articutResultDICT),
                          #"number": articutResultDICT["number"],
                          #"user_defined": articutResultDICT["user_defined"],
                          "utterance": [],
                          #"input": articutResultDICT["input"],
                          #"unit": articutResultDICT["unit"],
                          "exec_time": articutResultDICT["exec_time"],
                          "level": "lv3",
                          "version": articutResultDICT["version"],
                          "status": articutResultDICT["status"],
                          "msg": articutResultDICT["msg"],
                          "word_count_balance": articutResultDICT["word_count_balance"],
                          }
            # 呼叫一個 converter，把 resultDICT["result_obj"] 裡的詞彙一個一個轉成拼音。
            if convert == "TL":
                resultLIST = self._2TL(articutResultDICT["result_obj"])
            #elif convert == "POJ":
                #resultLIST = self._2POJ(articutResultDICT["result_obj"])
            #else: #convert == "WORD":
                #resultLIST = self._2Word(articutResultDICT["result_obj"])
            resultDICT["utterance"] = "╱".join(resultLIST)
            return resultDICT



if __name__ == "__main__":
    try:
        with open("../account.info", encoding="utf-8") as jF:
            accountDICT = json.load(jF)
    except:
        accountDICT = {"username":"", "apikey":""}

    accountDICT = {"username":accountDICT["username"], "apikey":accountDICT["apikey"]}
    articutTaigi = ArticutTG(username=accountDICT["username"], apikey=accountDICT["apikey"])
    #台語漢字 CWS/POS TEST
    inputSTR = "你ē-sái請ta̍k-ke提供字句hō͘你做這個試驗。"
    inputSTR = "跋倒, 佮意"
    inputSTR = "伊誠𠢕激五仁，激甲逐家笑咍咍".replace("。", "")

    inputLIST = [
        #"你愛有出脫人才會看你有",
        #"李家明仔載欲來捾定，咱著辦腥臊請人",
        #"雖然我佮恁阿爸平歲，毋過論輩無論歲，咱算仝沿的，叫我阿兄就好",
        #"借問一下，文化路佇佗位？",
        #"車斗有張升降尾門，較好起落貨",
        #"一人才分一疕仔，連楔喙齒縫都無夠",
        #"錢大百，人落肉",
        #"時機䆀䆀，我的錢水有較乏",
        #"原來你就是王董的，失敬，失敬！",
        #"伊生做肥軟仔肥軟，看著蓋古錐",

        "張總的頂擺出張，去巡視海外的工場，佇遐蹛個外月",

        "兩錢金仔",

        "出好囝孫",
        "物件揀好去揣店員結數",
        "論輩無論歲",
        "佇社會上走跳",
        "世間上有真濟代誌是袂按算的",
        "專制政府刑罰政治犯的手段真粗殘",
        "一大捾的荔枝",
        "你臆了真準",
        "囡仔身軀洗好糝一屑仔痱仔粉較焦鬆",
        "伊連鞭就會出師矣！",
        "伊是阮的親生老爸",
        "三鉼鐵鉼",
        "伊是阮兄哥",
        "伊是駐水死的",
        "拋魚著趁流水",
        "伊志願來的",

        "敢閣有另外的人欲來？",
        "我的房內全是花的芳味",
        "伊的頭毛軟㽎㽎",
        "你毋通走去遐共人鬧台",
        "囡仔騙袂恬！",
        "昨暗我夢著中大獎",
        "跋落萬丈深坑",
        "三頓攏食外口",
        "恁兜是蹛佇佗位？",
        "相爭做乞食頭",
        "緊去予醫生看",
        "嬈花查某",
        "落雨天無法度曝粟",
        "共棉被舒舒咧",
        "尻川斗翹翹",
        "我會真毋甘",
        "這層代誌你會當請伊代辦",
        "伊按呢做是欲做人情予你",
        "嬰仔尻川𩛩著",
        "佇繡房內刺花繡針黹",
        "水捙倒去矣",
        "頭抽豆油",
        "蛟龍泅魚池",
        "伊定定用暗步欲陷害人",
        "聲音哪會攏恬去矣？",
        "金枝玉葉",
        "伊的面有一疧",
        "我共面巾溼予伊澹",
        "五十外歲",
        "你敢知影伊叫做啥物名？",
        "曲跤撚喙鬚",
        "請朋友看電影",
        "一領破衫㧣一冬",
        "你按呢死坐活食敢是辦法？",
        "烏骨雞的市價比肉雞仔較好",
        "逐家對伊的印象真好",
        "伊又閣咧起狂矣",
        "伊因為帶身命才會攏無咧上班",
        "伊大我一輩",
        "象是陸地上上大隻的動物",
        "趁放假去𨑨迌會當改換心情",
        "大本蕹菜",
        "隱痀的交侗戇",
        "你去攑沙耙共跳遠場地整予平",
        "用紙篋仔貯糖仔餅",
        "的交陪誠深",
        "你對我有誤會",
        "真有體面",
        "你是肯抑毋肯？",
        "伊的跤真臭",
        "囡仔好育飼",
        "伊去予人修理",
        "賣摵仔麵的用麵摵仔摵麵",
        "會計師明仔載欲來阮公司查數",
        "彼个人有夠𡳞蔓",
        "老爸是有錢人",
        "伊閣咧發輦矣！",
        "你毋通拍破人的飯碗",
        "檨仔切片烘予堅乾做檨仔乾",
        "臺灣的溪水攏是汫水",
        "伊是這角勢的角頭",
        "代誌猶未定著",
        "老牌歌星",
        "伊飼的雞仔攏著災死了了",
        "毋知咧無閒啥物",
        "這塊布的色緻真媠",
        "這領衫上適合你來穿",
        "尪架桌發爐",
        "天頂攏無雲",
        "拋磚引玉",
        "甍予你倒",
        "阮少爺對阮這寡下跤手人攏真好",
        "在座的人",
        "隨身行李",
        "鳥仔有翼才會飛",
        "今仔日欲搬啥物戲齣？",
        "汗㴙㴙滴",
        "火化去矣！",
        "禮拜咱才做伙來去看電影",
        "伊是分的",
        "鬥陣來去",
        "提針來紩衫",
        "恁查某囝敢做人矣？",
        "姑表相伨",
        "慢牛厚屎尿",
        "挽瓜揫藤",
        "戲院門口人插插插",
        "彼个人足屎桶",
        "伊會共人食倯",
        "孤鳥插人群",
        "彼隻船仔沕落去水底矣",
        "咱兄弟姊妹就像仝一條水脈流出來的啦",
        "囡仔上驚注射",
        "頭毛熁著火就虯去",
        "提出來予你鼻芳",
        "我的冊借人矣",
        "這塊枋一寸厚",
        "這馬真少人用柴頭咧燃火矣",
        "伊對喙就罵",
        "伊對食這項真甘開",
        "你號做啥物名？",
        "伊自做生理到今一直咧塌本",
        "伊較佮意淺色的衫",
        "今仔日伊閣來矣",
        "身軀洗了隨出去弄風會去寒著",
        "你足巧的呢！",
        "金錢毋是萬能的",
        "目睭澀澀",
        "蝦蛄頭食起來無較輸龍蝦",
        "伊真𠢕佮人捙盤",
        "伊決定欲辭職矣",
        "伊確實是一个好人",
        "伊決心欲拍拚讀冊",
        "我用人格共你保證",
        "是啥物人放臭屁？",
        "伊看別人無上目",
        "伊自來就毋捌破病",
        "提石頭共伊搩落去",
        "藥仔挽會行上要緊",
        "阮囝滿三歲矣",
        "毋通破壞人的感情",
        "兩鬢如霜",
        "熱鼎炒菜",
        "囡仔的成就是爸母的驕傲",
        "隔壁的地界一直楦過來",
        "既然如此",
        "濟牛踏無糞",
        "目睭褫開",
        "爽啦！我著頭獎矣！",
        "伊看著真疲勞",
        "伊生做真大漢",
        "藥仔食了有較差無？",
        "塗跤先苴報紙才開始油漆",
        "提供證明文件",
        "目睭瞪大蕊",
        "今年是一个好年冬",
        "丹田無力",
        "伊無一定會來",
        "無趨袂瀉水",
        "你的人面較熟",
        "三條茄毋值一粒蟯",
        "無大無細",
        "一時的失敗嘛毋通失志",
        "罕罕仔才啉一擺酒",
        "佮伊錚落去",
        "便有錢就開了了",
        "櫻花的樹身真金滑",
        "鴨鵤袂生卵",
        "彼間百年老店到今猶是第三代的老頭家咧徛台扞店",
        "鬱死人的才調",
        "雞屎運咧敨",
        "獻敬神明",
        "飼囝真辛苦",
        "伊去予車挵一下著重傷",
        "共伊放袂記",
        "啉一杯茶",
        "你對這个方向直直行就到矣",
        "股票上市",
        "一肢跤指頭仔",
        "祝你一路順風",
        "食飽桌頂無拭會唌虼蚻來",
        "伊閣咧共我供體矣",
        "一打汽水",
        "寬寬仔是",
        "我袂記得伊號做啥物名",
        "我毋捌跍咧食飯",
        "雞仔生雞𧉟真普遍",
        "伊這擺的表現真落氣",
        "腹肚脹起來",
        "原早的路無蓋大條",
        "我來拍頭陣",
        "大貨車敢會當入去巷仔底落貨？",
        "風流人物",
        "徛佇籠床邊熁燒",

        "風流才子",

        "一鈕仔囝",
        "加官晉祿",

        "警方咧調查死者敢有佮人結怨",

        "囡仔的𨑨迌物百百款",

        "遮的柳丁會使提去散賣",

        "阿祖較早做過藝旦",

        "大牛惜力",
        "食老耳空重",

        "伊做人真現實",

        "沙龍巴斯貼久嘛會起藥蛆",
        "伊不時嘛咧讀冊",

        "這件代誌請你共我運動一下",

        "真實的感覺",

        "違約交割",

        "坐倚來",
        "順風捒倒牆",
        "烏仔魚搢水",

        "遠親不如近鄰",
        "嘉南大圳",
        "予人屧手縫都無夠",
        "你傷倖囡仔",
        "我恁祖公",
        "春夏之交",
        "手足擽的",

        "你下的願敢有應效？",

        "奅姼仔伊有一套",
        "一篋仔餅",
        "伊有六尺懸",
        "向逐家謝罪",

        "阮序大人攏是誠理解的人",
        "猛虎難敵猴群",
        "以德報怨",
    ]
    #inputLIST = ["地動發生到今(4/10)是第八工，砂卡礑步道猶是走揣的重點。今仔早重機具佇步道繼續挖，有揣著兩名死者，可能是姓游的爸爸和查某囝，佇這兩位死者的下跤閣挖著兩个死者，是相攬的姿勢。第三位可能是媽媽，而且佇身軀頂有揣著伊和三个囡仔的健保卡，另外佇咧暗頭仔也閣挖著一位死者，應該是上細漢的查某囝，若無意外，挖出來這五个人就是一家伙仔。",]
    #inputLIST = ["日本", "日月潭"]
    for inputSTR in inputLIST:
        resultDICT = articutTaigi.parse(inputSTR, level="lv2")
        print("\n")
        pprint(resultDICT["result_pos"])
        pprint(resultDICT["result_segmentation"])
        print("=================================")

    #inputSTR = "阿明聽了，煞想著一个問題：「若準風颱嘛算是一種自然的現象，為啥物咱猶原愛驚惶伊？」老大人笑笑仔共伊講：「因為咱攏無了解風颱，所以才會感覺驚惶。」".replace("。", "")
    #resultDICT = articutTaigi.parse(inputSTR, level="lv2")
    #pprint(resultDICT)
    #<ENTITY_pronoun>[^<]+</ENTITY_pronoun>(<FUNC_inner>[^<]+</FUNC_inner>)?<ENTITY_noun>[^<]+</ENTITY_noun><DegreeP>[^<]+</DegreeP>