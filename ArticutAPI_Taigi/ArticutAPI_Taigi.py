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

        "阮先行，恁押後",

        "張總的頂擺出張，去巡視海外的工場，佇遐蹛個外月",

        "這張圖真媠，我欲描一張起來",
        "喙共弓開才會當灌藥仔",
        "伊人誠䆀猴",
        "一日到暗喈無錢",
        "這領衫我看袂過目",
        "這領衫有三鈕鈕仔",
        "拄著好時運",
        "廟仔有童乩咧跳童",
        "辭典是真重要的工具冊",
        "做人的囝兒毋通予爸母操心",
        "兩錢金仔",
        "伊咧讀冊",
        "伊這款做法手路傷粗啦",
        "做予好勢",
        "做散工的人趁的錢袂齊勻",
        "這種餅哪會做這形的",
        "共囡仔唔予伊睏",
        "一門大炮",
        "伊上要緊彼隻狗",
        "伊佇咧睏",
        "請你評看啥人較有理",
        "伊的人真笑詼",
        "來者是客",
        "食美國仙丹的副作用是面會圓圓",
        "我的目尾開始有皺痕矣",
        "意氣投合",
        "這片山坪種足濟茶欉",
        "氣力有夠",
        "這逐家嘛看過",
        "拑牆壁",
        "你無證據哪會當誣賴人",
        "興風作浪",
        "魚肉鄉民",
        "伊頂日仔才無去的",
        "這个牌子的產品真有信用",
        "市場外口有人咧拚俗貨",
        "代誌按呢一直吊佇半空中嘛毋是辦法",
        "枵雞無畏箠",
        "你明仔載去揣看有師傅會當來掠漏無？",
        "鐘聲真響亮",
        "往西爿行去",
        "攑椅頭仔去外口坐較秋凊",
        "門關無密",
        "大自然實在真奇妙",
        "你這個月的開銷有較濟",
        "這領衫皺去矣",
        "你毋通放蕩過一生",
        "你哪會使攑牛捽仔咧捽囡仔？",
        "這款索仔較粗勇",
        "激一个氣",
        "我已經想無閣較好的計策矣！",
        "喙焦喉渴",

        "現流仔上鮮",
        "七分酒對三分水上拄好",
        "兄弟攏分散了了矣",

        "斟酌觀察",
        "你的面看起來一點仔血色都無",
        "拹鐵釘仔",
        "原來這層代誌是你咧變鬼",
        "較加嘛會駐水",
        "搦著證據",
        "一橛甘蔗",
        "想袂到伊會為著利益來反背眾人",
        "頭毛鬖鬖",
        "伊的身體有夠勇",
        "倩一陣弄龍的來鬧熱",
        "我致這个症頭已經幾若年矣",
        "電影看煞才來去食飯",
        "伊退休了後就無插代誌矣",
        "囡仔出癖的時陣毋通共伊𤆬出去",
        "總統委任伊做大使派往聯合國",
        "伊堅持無欲做人的接跤的",
        "伊早頓攏嘛烏白食",
        "謼！閣來矣！",
        "偷食野味",
        "欲做伙來去踩街無？",
        "出好囝孫",
        "孤鳥插人群",
        "伊走無去矣",
        "啥物人佇遐咧唱歌？",
        "我欲食糜",
        "這粒錶仔定去矣",
        "攏是伊佇遐咧挲圓捏扁",
        "伊的行為引起人的注目",
        "水蝕落去矣",
        "君子務本",
        "你實在足挐的！",
        "伊的名聲真響",
        "屎瞪袂出來",
        "伊獸醫系畢業了後就開始做獸醫",
        "料想袂到",
        "這个囡仔號名未？",
        "覺悟著過去做了毋著",
        "伊透底毋捌出國",
        "伊共代誌凊彩戽戽咧就準拄好矣",
        "這盤芥藍仔菜有夠柯",
        "伊是阮細的",
        "你穿的衫是羊毛的",
        "到今你才知！",
        "伊看著蛇會掣",
        "草蓬蓬生",
        "阮的厝邊攏誠好鬥陣",
        "這是在地的果子",
        "伊看起來加較少年",
        "三年仔有十班",
        "錢予賊仔偷提去矣！",
        "家家戶戶",
        "才號有好名",
        "伊的目睭真尖",
        "你睏了有飽眠無？",
        "你是趖去佗位？",
        "對遮拋近路較緊",
        "伊佇公所食頭路",
        "伊是教會的老姑娘",
        "硞著頭額",
        "較成物的留咧",
        "西醫的效果比中醫較緊",
        "看鬧熱的人相挨相𤲍",
        "物件揀好去揣店員結數",
        "兩个好朋友哪會相拍？",
        "我已經泡一杯厚茶欲予你解酒",
        "伊做人真澀",
        "日本話我普普仔聽有",
        "二品碗公",
        "害矣啦！代誌煏空矣啦！",
        "疔仔的膿泏出來矣",
        "毋通忤逆序大人",
        "粒仔咧流湯",
        "回心轉意",
        "這款花草較清較好看",
        "股市崩盤",
        "作田人放伴作穡",
        "這擺公司虧損真嚴重",
        "電線相拍電",
        "我心肝內感覺對伊真袂得過",
        "伊有敲電話來請假",
        "我的代誌免你插",
        "褲袋仔袋磅子",
        "這个囡仔做代誌誠規矩",
        "期待再相會",
        "我有一雙大跤胴",
        "頭毛真旺",
        "下早仔水氣真重",
        "糝一寡糖",
        "伊閣咧假痟矣",
        "這領膨紗衫是阿媽共你刺的",
        "毒品害伊行上絕路",
        "臺北車頭內面五路的人攏有",
        "咱毋通濫糝共人批評",
        "馬耳東風",
        "阮某轉去外家矣",
        "剝筍仔殼",
        "這个人看著戇直戇直",
        "我共你當做是上好的朋友",
        "阮老母咧替人騙囡仔",
        "求神明扶持",
        "豬母帶膭",
        "伊的物件交代我保管",
        "這港水泉的水誠甘",
        "細粒子的較𠢕囥歲",
        "掖草仔子",
        "應喙應舌",
        "鬼頭鬼腦",
        "一欉成人懸的樹仔",
        "伊去做工矣",
        "你袂曉寫的題目就先勾起來",
        "索仔若拍死結就真僫敨開",
        "有其父必有其子",
        "你順路送伊轉去",
        "起跤動手",
        "伊的目睭誠利",
        "生活真穩定",
        "往過的人晏報戶口是誠四常的代誌",
        "論輩無論歲",
        "你𣁳一碗湯予我",
        "吊橋行著會㽎",
        "請你有閒來阮遐𨑨迌",
        "伊收跤洗手誠濟年矣",
        "伊猶原佇遐咧等你",
        "佇社會上走跳",
        "你哪會遐狼毒？",
        "彼个人的心肝誠惡毒",
        "空喙咧吐肉箭矣",
        "海水漲起來矣",
        "伊的作為予人誠欣賞",
        "大港無崁蓋",
        "赦你無罪",
        "這間冊店有賣印色",
        "伊共索仔翸斷去矣",
        "阿姊攑花仔傘共彼个阿婆遮日",
        "伊的鼻真利",
        "無證據毋通佇遐吐憐涎",
        "巷仔內有一間板仔店",
        "結婚進前",
        "臭柑排店面",
        "趕緊共你跤底的塗沙刮刮咧！",
        "大量生產才算會和",
        "共草仔耙倚來",
        "演員的替身",
        "鬚聳目降",
        "遮的物件緊送去工場予",
        "是按怎這件代誌到這馬猶未條直？",
        "我今仔日是專工欲來佮你相辭的",
        "伊的心情誠䆀",
        "人若大到在矣就免食轉骨的補藥矣",
        "瘦田歹種作",
        "慶祝生日",
        "你去共茶盤洗清氣",
        "抉紅毛塗",
        "伊若無錢就變無魍矣！",
        "這塊肉真肥",
        "跂較懸咧",
        "妖魔鬼怪",
        "將來會發生啥代誌無人知",
        "伊扞一間礦業公司",
        "有人駐死佇水底",
        "你毋通為著人有好的物件就赤目",
        "伊生做足大漢",
        "金光閃閃",
        "款厝內毋是干焦查某人才會當做的工課",
        "伊閣咧想伊的未婚妻矣",
        "伊會當躘真懸",
        "伊毋是簡單的人物",
        "恁兩人的結合是我上大的願望",
        "伊的車門予人挵一㧌",
        "你共遮的物件囥入去觳仔內底",
        "有家有後",
        "漚柑鋪籠面",
        "臺灣囡仔歌算是唸謠",
        "彼个人按怎叫都叫袂振動",
        "時間無早矣",
        "本來就是按呢嘛！",
        "你參伊去",
        "一目甘蔗",
        "這塊布較結較袂破",
        "伊用草做一隻狗",
        "桌頂全坱埃",
        "哈哈大笑",
        "佇基隆有一間服侍老大公的廟",
        "逐家攏看現現",
        "有人咧揤電鈴",
        "你啥物時陣欲倒去？",
        "伊堅持欲繼續拍拚落去",
        "兩个相接跤來",
        "啥人叫你大主大意做這件代誌？",
        "一項代誌",
        "彼間麵店仔欲褪人",
        "看人的目色過日子",
        "這隻船食水偌深？",
        "塗跤陷入去",
        "我無佮意伊做代誌的方式",
        "你予我考慮一下",
        "一子弓蕉",
        "共錢筒仔破開",
        "這擺的代誌我嘛無步矣",
        "我最近較閒",
        "電影已經收場矣",
        "跩來跩去",
        "閃爍的天星",
        "一下仔久就好矣",
        "伊真𠢕吮食",
        "正月初二查某囝轉外家做客",
        "伊予警察掜留佇警察局",
        "你按呢做毋驚會夭壽！",
        "棉被先捲起來才收入去袋仔內",
        "毋是每一个人攏適合食素食",
        "世間上有真濟代誌是袂按算的",
        "伊對你有情意",
        "雞髻大塊看起來真威風",
        "兩个人的感情真好",
        "這兩種有啥物精差？",
        "孤𣮈絕種",
        "外口較涼",
        "今攏害了了矣！",
        "今年的王梨失收",
        "提去外口予日頭爁一下",
        "拜託你放手",
        "心存善念",
        "這塊肉真韌",
        "這條錢是伊過手的",
        "飼伊成人",
        "阿英明仔載欲轉後頭",
        "心涼脾土開",
        "用鏨仔雕刻一身佛像",
        "坐予好勢",
        "節省時間",
        "這句話是伊提頭的",
        "壁落漆",
        "伊寫字、食飯攏用倒手",
        "做序細的無應該佮序大人應喙應舌",
        "排做三排",
        "這件代誌是你該做的",
        "閹過的雞公飼較會大",
        "兩爿佇咧對削",
        "沿路抾客",
        "牽牛去食草",
        "扯一个結",
        "糜煮了傷漖",
        "伊真五仁",
        "修剪樹枝",
        "涵空無敨",
        "一爿西瓜",
        "我彼本冊你敢有看見？",
        "伊的手頭真重",
        "這是阮阿母的手路菜",
        "大不了予人罵罵咧爾爾",
        "天光矣",
        "伊放聲欲予你好看",
        "專制政府刑罰政治犯的手段真粗殘",
        "你緊來共我鬥跤手",
        "一大捾的荔枝",
        "伊佇法院共人通譯",
        "死都死囉！毋通閣來交纏",
        "我借伊一本冊",
        "伊拄才對外口轉來",
        "打探消息",
        "昨暝狗母毋知按怎一直吹狗螺",
        "這幅圖我感覺無啥物特別",
        "來來來！逐家上桌食飯",
        "西藥食了較散",
        "你千萬毋通誤會",
        "注大筒的",
        "伊一个癖性佮人無仝款",
        "物件囥佇桌頂",
        "伊對逐項代誌攏無興頭",
        "斷了批信",
        "阮囝已經會曉家己扒飯矣",
        "你毋通起歹心共伊計算",
        "這堵壁缺兩隙",
        "好歇工矣",
        "彼个所在誠遠",
        "你欲坐碌硞馬無？",
        "用鐵枝拄門",
        "伊踏著黃金矣",
        "單槍匹馬",
        "伊毋願做人的細姨",
        "予海湧𩛩去",
        "伊的人較土",
        "雞僆仔肉較幼",
        "你臆了真準",
        "伊生做較細漢",
        "恁毋通起跤動手",
        "兩个人𢯾做伙",
        "飯食了才食果子",
        "我下晡會共錢匯入去你的戶頭",
        "天篷陷落來",
        "伊真厚話屎",
        "逐个囡仔攏是爸母的心肝仔寶貝",
        "伊的消息誠靈通",
        "火舌爁一下",
        "伊去予警察召去問口供",
        "伊的思想誠保守",
        "這間公司的財務需要整頓一下",
        "咱共灶跤清清咧",
        "花是你送的乎？免歹勢啦！",
        "會䠡袂爬",
        "王侯將相",
        "鹹水魚若是現流仔加足貴的",
        "三穗番麥",
        "爸仔囝拆開欲十年矣",
        "彼个人的心腸真䆀",
        "囡仔身軀洗好糝一屑仔痱仔粉較焦鬆",
        "人情世事",
        "伊真有喙水",
        "定定用話共我洗",
        "去山頂隱居",
        "伊彼支鼻真媠",
        "伊共甘蔗遏做兩節",
        "陳的佮王的咧加話",
        "稻仔抽長結穗矣",
        "一矸米酒",
        "伊做生理真殺",
        "這齣戲做透矣",
        "伊閣佇遐佯痟矣",
        "伊一直揣機會欲報鳥鼠仔冤",
        "拳頭拇對胸坎貫落去",
        "有的跤踏車倒踏就會停",
        "啥物人接你的缺？",
        "伊的勢力誠大",
        "魚仔瀳倚來",
        "阮阿母較早專門咧共人抾囡仔",
        "伊將我放袂記得矣",
        "開光點眼",
        "我的工課足濟的",
        "這馬的野球攏真注重戰術",
        "蓋世奇才",
        "謝天謝地",
        "共糞埽吸起來",
        "用話叉人",
        "昨暗伊無轉來睏",
        "一條新聞",
        "伊連鞭就會出師矣！",
        "伊是阮的親生老爸",
        "伊規工攏佇外口拜訪客戶",
        "在你去啦！",
        "你毋通予人當做盼仔",
        "三鉼鐵鉼",
        "做人毋通遐歹心",
        "伊是阮兄哥",
        "伊是駐水死的",
        "拋魚著趁流水",
        "這本冊你共我接過去",
        "這款冤枉錢你曷開會落去！",
        "無暝無日",
        "伊的人範袂䆀",
        "伊志願來的",
        "我猶未食飯",
        "你毋通空喙哺舌誣賴別人",
        "物件予人勍去矣！",
        "伊是佇昨昏頂半暝過身去的",
        "老母破病了後到今攏無較好",
        "哪未轉來？",
        "到底你的意願是按怎？",
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
        "伊徛對面共我擛手",
        "好天的時阮欲來去山",
        "我來拍頭陣",
        "大貨車敢會當入去巷仔底落貨？",
        "貓仔上佮意臭臊的",
        "風流人物",
        "歇睏日伊常在𤆬一家伙仔去郊外𨑨迌",
        "哭爸！我袂記得紮錢！",
        "頂禮拜阮一陣人上山去看風景",
        "明仔載欲報數",
        "厝內真驚人",
        "徛佇籠床邊熁燒",
        "伊做代誌攏會留一寡屎尾予別人替伊處理",
        "插春仔花",
        "這隻膨椅已經窞肚矣",
        "伊無因為我生做較歹看面就棄嫌我",
        "提出較好的條件對方就會投降",
        "等戲煞鼓咱來去食宵夜",
        "鰇魚烘無偌久就會蔫",
        "伊無細膩去挵著電火柱",
        "我看著伊就刺疫",
        "萬項代誌攏有前因後果",
        "伊徛佇外口颺風",
        "這個月無來洗",
        "風流才子",
        "路口彼間藥局生理真好",
        "伊生做真好看",
        "提起告訴",
        "一鈕仔囝",
        "向望你會當好好仔做人",
        "火化去矣",
        "稻仔佈了傷櫳",
        "加官晉祿",
        "警方咧調查死者敢有佮人結怨",
        "我對籃球無興趣",
        "細條巷仔",
        "我生理失敗的時佳哉有伊共我打扎",
        "我都無錢矣你……",
        "囡仔的𨑨迌物百百款",
        "收疕矣",
        "火咧湠真緊",
        "煞著頂腹蓋",
        "這件代誌交予你來摠",
        "規日神神",
        "你毋通遐八珍",
        "伊跍佇門口看過路人",
        "遮的柳丁會使提去散賣",
        "爸母飼囝真辛苦",
        "伊失蹤成月日矣",
        "你電話幾番？",
        "死鴨仔硬喙桮",
        "過面矣",
        "工課放咧走去踅街",
        "阿祖較早做過藝旦",
        "三身娘仔",
        "伊佇戰爭的時著銃",
        "兜的家伙攏予伊敗了了矣",
        "我佮伊定定相扴",
        "今年聯考英文的題目真簡單",
        "伊佇公家機關服務",
        "伊攏交結一寡做官的",
        "你去叫彼个走桌的閣捾兩罐麥仔酒來！",
        "大牛惜力",
        "你是偏偏欲佮我做對是無？",
        "酸的物件我較無銷",
        "食老耳空重",
        "臺灣的本土語言毋知閣會當保存偌久？",
        "伊做人真現實",
        "甜粿炊無透",
        "央人寫批",
        "無把握的代誌毋通做",
        "老師咧改簿仔",
        "哭枵！無紮雨傘煞咧落雨",
        "這塊眠床枋足𠕇的",
        "伊真𠢕經絲",
        "沙龍巴斯貼久嘛會起藥蛆",
        "戲棚跤徛久就是你的",
        "彼幅圖真歹看",
        "你哪毋去食飯？",
        "伊不時嘛咧讀冊",
        "這件代誌請你共我運動一下",
        "目空真深",
        "我無欲去啦！",
        "共藥丸磨做藥粉",
        "伊予頭家冰起來",
        "咱做序細毋通予序大人操煩",
        "我來卜一下仔卦咧",
        "伊是阮牽的",
        "邀請伊來參加",
        "一支鎖匙",
        "真實的感覺",
        "違約交割",
        "兩人伨頭搬戲",
        "阮店賣的攏是高級貨",
        "用攄仔剃頭真方便",
        "佇塗跤畫格仔",
        "我共你保證伊開的支票袂跳票",
        "胡蠅颺颺飛",
        "伊牽抾我趁足濟錢",
        "坐倚來",
        "看起來伊猶毋知",
        "天貓霧仔光伊就起來矣",
        "伊足得人惜的",
        "予錢鼠咬破布袋",
        "順風捒倒牆",
        "這件代誌我願意做",
        "彼件代誌我干焦略仔知爾爾",
        "今仔日天氣真翕",
        "彼个少年家真好差教",
        "烏仔魚搢水",
        "現挽現食",
        "一屑仔無夠通楔喙齒縫啦！",
        "這馬足少人咧翕烏白的相片矣",
        "伊搭胸坎保證無問題",
        "頭殼尖尖做錢貫",
        "梅仔蜜了有透",
        "你腹內火氣傷大",
        "有一个查某囡仔按對面行過來",
        "遠親不如近鄰",
        "差無偌濟",
        "你是家己開業抑是予人倩？",
        "伊規工攏佇厝裡無出去",
        "嘉南大圳",
        "這聲苦矣！",
        "按呢敢會祭孤得？",
        "咱雙頭攏來去揣看覓",
        "予人屧手縫都無夠",
        "被囊剝起來洗",
        "你傷倖囡仔",
        "我恁祖公",
        "春夏之交",
        "伊昨昏三更半暝才轉來",
        "手足擽的",
        "伊共兩本簿仔敆做伙",
        "你下的願敢有應效？",
        "倚樣做衫",
        "了錢生理無人做",
        "伊咧唱歌會走音",
        "一牢雞牢",
        "你這過的成績有淡薄仔退步",
        "衫仔擢擢咧",
        "意氣用事",
        "塗豆仁粩",
        "阿玉已經做人矣",
        "伊食錢的代誌煏空矣",
        "奅姼仔伊有一套",
        "這个囡仔真用功",
        "捀一盤菜",
        "今仔日推了有夠飽的",
        "一篋仔餅",
        "伊生做真䆀",
        "狂風大作",
        "恁是咧起痟呢？遐爾仔寒閣欲去泅水",
        "我欲去北港媽進香",
        "阿爸睏醒矣",
        "伊最近捷捷來",
        "物件毋通落勾",
        "伊佮老爸生做誠成",
        "一戶人家",
        "伊有六尺懸",
        "伊為著家己的利益出賣朋友",
        "若按呢愈好",
        "伊共這塊肥豬肉提去炸豬油",
        "量其約仔",
        "光復失土",
        "手予蠓仔叮一模",
        "絲番薯葉",
        "向逐家謝罪",
        "新正年頭",
        "自我介紹",
        "伊對人真誠懇",
        "這塊布布目較疏",
        "我看著有人佇水底沐沐泅",
        "閘佇半路拍人",
        "請你名簽蹛遮",
        "大孫捀斗",
        "你千萬毋通閣行歹路",
        "以早的人攏提豆餅咧飼豬",
        "你毋通閣來膏膏纏",
        "伊今仔日會做這款代誌攏是予人煽動的",
        "壁有一位噗起來矣",
        "這本課本有十二課",
        "樹尾無風袂搖",
        "伊哪會遐才情",
        "伊駛車去軋著人",
        "伊病一下真食力",
        "這條代誌我聽了誠憤慨",
        "你哪會遮爾跤梢？連這曷袂曉",
        "今仔日下晡的天氣真秋凊",
        "年節的民俗",
        "我共你撫撫咧！",
        "目睭噗噗",
        "這味藥仔是推會行抑推袂行？",
        "將心比心",
        "夭壽！阮這條巷仔昨昏又閣著賊偷矣",
        "伊攏總生六个後生",
        "明仔早起我欲佮阮阿公去運動",
        "伊真𠢕軁",
        "我看阿忠輸面較大",
        "好酒沉甕底",
        "你對這件代誌有啥物感想？",
        "你喊啥物名？",
        "兩捻龍眼",
        "垂肩的人穿衫較無好看",
        "到位矣",
        "食老面皺皺",
        "合掌參拜",
        "伊退休了後生活誠逍遙",
        "硬骨的囡仔攏較毋認輸",
        "興衰有時",
        "阮的工頭看起來猶閣真少年",
        "這馬我才知影伊是騙我的",
        "女扮男裝",
        "頭毛染色",
        "伊閣鬧代誌矣",
        "警察指揮交通",
        "你有看著我的數單無？",
        "共屜仔挩開",
        "現此時的人攏較會曉享受",
        "阮翁仔某頂下歲",
        "伊去予滾水燙著",
        "想袂到會變做這个局面！",
        "一年半載",
        "野生動物",
        "伊供出真濟人",
        "有代誌才呼我",
        "阮先生娘生做真媠",
        "定定食菜較袂高血壓",
        "予風尾掃著",
        "用別人的拳頭拇舂石獅",
        "你欲揣的人就是我",
        "錶仔定去袂行矣",
        "濺蠓仔水",
        "伊是阮祧仔內的",
        "逐家做伙來做功德",
        "路邊擔仔的物件較俗",
        "阮序大人攏是誠理解的人",
        "用手比較緊",
        "桌布澹澹𩛩咧會臭臭",
        "伊食重鹹",
        "伊的頭去挵著桌角",
        "伊毋是刁意故的",
        "彼隻狗仔咧𪁎矣",
        "火車閣十分鐘就會到位矣",
        "人民捙倒獨裁者的銅像",
        "咱下昏來去踅夜市",
        "我感覺伊真顧人怨",
        "人𤲍人",
        "你這个卑鄙的小人",
        "我毋捌出國過",
        "唉！真可惜",
        "兩隻牛咧相觸",
        "這水的塗豆真飽仁",
        "明仔載我會坐客運轉去",
        "一葩電火",
        "我功課若寫好就會使去看電影矣",
        "讀國中彼當陣伊就帶痚呴",
        "哈！予我掠著矣",
        "食一頓飯",
        "伊做的彼件歹代誌早慢會破空",
        "心肝內感覺酸酸",
        "伊彼个人誠重錢",
        "軟塗深掘",
        "少年人往往攏較衝碰",
        "番薑仔醬",
        "用橐仔共葡萄套起來",
        "稻仔穗頕落去",
        "財產放予囝孫",
        "猛虎難敵猴群",
        "毋著啦！",
        "你就當做無伊的存在",
        "你誠敢呢！這款代誌你竟然做會出來！",
        "販貨去賣",
        "春天後母面",
        "我欲予伊歹看",
        "本錢真粗",
        "下暗欲來阮兜予阮請無？",
        "彼个物件限你明仔載中晝以前予我",
        "士農工商",
        "暝尾的時足寒的",
        "闊喙的食四方",
        "你緊共伊擋咧！",
        "此情此景",
        "中產階級",
        "小旦上𠢕共人使目尾",
        "伊走了真緊",
        "這个木匠做的木工袂䆀",
        "伊的一句話予我規个心頭挐絞絞",
        "草蓆仔頂的塗粉拭拭咧才去睏",
        "多謝你！",
        "頂日仔規家伙仔有來我遮",
        "欸，哪會按呢？",
        "以德報怨",
        "豬仔相經",
        "十全十美",
        "這有啥物路用？",
        "經營事業",
        "出頭損角",
        "這領衫較暗色",
        "用好紙褙",
        "布邊繐去矣",
        "青天白日",
        "山頂彼陣猴定定落山來損蕩人的果子園",
        "我佇臺灣出世的",
        "封頭壁會洩水",
        "家伙跋了了",
        "何方神聖",
        "伊相罵攏毋免掀戲文",
        "伊對我真好",
        "我做的敢有算額？",
        "彼个查某囡仔敢猶活會？",
        "頭家共伊漲懸價",
        "手不動三寶",
        "予人呸瀾",
        "昨昏佇會場遇著老朋友",
        "伊佇番薯園咧掘番薯",
        "盡人事順天意",
        "伊猶細漢",
        "尾溜翹起來",
        "我共你捋頭毛",
        "冇粟收入好米籮",
        "陰陽兩極",
        "頭毛菜誠輕秤",
        "金仔折現金",
        "我佮你差有一輪",
        "這間金仔店是阮遮上大間的",
        "食厚薰真傷肺管",
        "某偷咬雞仔伊敢毋知？",
        "伊的心肝足硬",
        "度看有發燒無？",
        "你真正有夠悾歁",
        "逐个人的興趣攏無款",
        "伊做人真虯",
        "新的公路欲開磅空對這粒山下跤迵過",
        "西北雨落袂過田岸",
        "這是啥人的主意？",
        "毋知伊的新頂司個性啥款？",
        "會曉煮雜菜麵的麵擔仔愈來愈少矣",
        "我會當幫助你的所在真有限",
        "藥膏抹落去粒仔就收喙矣",
        "閒閒罔出來行跤花",
        "一片枋仔",
        "成雙成對",
        "規嚾規黨",
        "你看我穿按呢敢好？",
        "動拳頭拇",
        "一𥐵醬菜",
        "我頂伊的缺",
        "規公司的代誌攏是伊咧摠頭",
        "工課僫做",
        "這是啥物物件？",
        "欱予伊倒",
        "這種漚色的衫無適合少年人穿",
        "定期存款",
        "阮兜的巷仔口有一間金紙店",
        "綴我來",
        "一串珠仔",
        "去共人客斟茶",
        "有教無類",
        "敢是欲落雨矣",
        "一棟樓仔厝",
        "我從到今毋捌看過遮爾仔㾀勢的查某",
        "花花世界",
        "合股做生理",
        "軍師獻計",
        "伊哪會蝹落去？緊共伊插起來",
        "對手誠弱",
        "天上聖母",
        "你今仔日欲出去𨑨迌乎？",
        "的生活真困難",
        "加減趁一寡仔外路仔來相添所費",
        "啉酒我無趣味",
        "恁新婦當時順月？",
        "花枝先剺花才落去炒",
        "清官難斷家務事",
        "伊面貓貓",
        "公親變事主",
        "錢算了花去",
        "我的代誌毋免你家婆",
        "伊生做吐目吐目",
        "修整路面",
        "你車駛這向敢著頭？",
        "石頭𠕇硞硞",
        "阮阿公較早佇人兜做長工",
        "伊跤手真緊",
        "用手出力共伊黜",
        "你去提凊飯來炒",
        "伊近來定定去拄著麻煩",
        "慈善事業",
        "心頭悶悶",
        "是啥物代誌予伊起毛䆀？",
        "大目新娘揣無灶",
        "開口借錢",
        "共烏枋的字擦擦咧",
        "腹腸狹的人較會排斥別人",
        "拆單欲去坐火車",
        "這款衫連鞭就退流行矣",
        "白頭偕老",
        "今仔日有一个和尚來遮化緣",
        "這粒楊桃有六捻",
    ]
    #inputLIST = ["地動發生到今(4/10)是第八工，砂卡礑步道猶是走揣的重點。今仔早重機具佇步道繼續挖，有揣著兩名死者，可能是姓游的爸爸和查某囝，佇這兩位死者的下跤閣挖著兩个死者，是相攬的姿勢。第三位可能是媽媽，而且佇身軀頂有揣著伊和三个囡仔的健保卡，另外佇咧暗頭仔也閣挖著一位死者，應該是上細漢的查某囝，若無意外，挖出來這五个人就是一家伙仔。",]
    #inputLIST = ["信義區",]
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