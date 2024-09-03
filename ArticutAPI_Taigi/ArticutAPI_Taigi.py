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
        #"伊食到七十外矣，猶閣是紅膏赤蠘",
        #'伊嫌\ue701翁頇顢講話,',
        #"除非你加入，伊才肯共阮鬥相共",
        #"伊提錢欲共警察楔空，警察顛倒共罰較濟錢",
        #"李家明仔載欲來捾定，咱著辦腥臊請人",
        #"雖然我佮恁阿爸平歲，毋過論輩無論歲，咱算仝沿的，叫我阿兄就好",
        #"今仔日誠好日，幾若口灶咧嫁娶",
        #"借問一下，文化路佇佗位？",

        "車斗有張升降尾門，較好起落貨",
        "一人才分一疕仔，連楔喙齒縫都無夠",

        "錢大百，人落肉",

        "醫生共聽筒囥佇我的胸坎，聽看我的肺部有各樣無",

        "三噸半的貨車扣除車身重量，會使載大約一千五百公斤的貨",

        "教會佇老母日攏會準備剪絨仔花，予會友結佇胸前",

        "耕者自耕，讀者自讀",

        "伊無細膩甌仔捙倒，煞予燒茶燙著",
        "時機䆀䆀，我的錢水有較乏",

        "是拄搪予我看著，我才知影的",

        "雞屎落塗，也有三寸煙",

        "共袂食得的菜葉仔揀掉，提去漚肥",

        "伊真有才調，律師牌一擺就考過！",

        "伊咧問你，你攏無回答",

        "請你閣予我寬限一個月，時到我一定會共錢還你",

        "佇遠遠的所在，就看會著臺中火力發電廠彼四支煙筒管矣",

        "檢方挽瓜揫藤，將所有的嫌犯攏㨑著，才做一睏總共起訴",

        "大通路的十字路頭，一般攏有電眼咧翕",

        "會得過日就好矣，毋免欣羨別人好額",

        "你若閣背約，伊就毋佮你合作矣",

        "伊無遵照契約，去予人消定矣",

        "古早時代，「玉井」叫做「噍吧哖」",

        "豬跤𤉙爛爛，真好食",

        "伊違反規定，去予主辦單位除名矣",

        "玻璃摔落塗跤，就去了了矣",

        "食藥仔會當止疼，毋過嘛有副作用",

        "我去清田溝，無細膩煞落湳",

        "元宵節的時，南北二路的人攏來看「臺灣燈會」",

        "咱蹛這角圍仔，山勢較低",

        "石頭傷大粒，著用鐵撬才撬會起來",

        "湯拄𣁳起來爾爾，猶燒滾滾，毋好燙著",

        "你做代誌著較撙節咧，毋通傷超過",

        "這个名真生份，我毋捌聽過",

        "為著欲顧三頓，閣較艱苦嘛毋驚",

        "緊去洗身軀，洗好通較早去睏",

        "赤跤逐鹿，穿鞋食肉",

        "原來你就是王董的，失敬，失敬！",

        "伊賣的貨，正範假範相濫，你毋通予伊唬去",

        "鳳尾草雖然臭賤，毋過若是熱著的時，共伊煎來做茶啉嘛誠有效",

        "深坑的豆腐是燃柴煮的，所以較芳",

        "伊改酒了後，人加真有精神",
        "我聽你咧落下頦，錢明明就是你提的，閣諍無",
        "我欲步輦來去公園𨑨迌，你欲鬥陣來去無？",
        "雖然兜真散赤，毋過的囡仔攏真有出脫",
        "你親像管家婆，逐項代誌都欲管",
        "跤手遮緊，隨予你搩幾若塊去",
        "手䘼傷束，我的手軁袂過",
        "你就是貪人的利息，才會予人倒數",
        "若想著這層代誌，我就火大",
        "像這款大寒的天，食一寡燒的上好",
        "積一寡仔錢，以後就用會著",
        "嘿啊，我知啊",
        "蹔跤步，跤步著和齊",
        "人若長志，就有機會出脫",
        "伊是我的心肝寶貝，啥人都袂使共伊欺負",
        "伊實在有夠破格，代誌予伊沐著就失敗",
        "仙人拍鼓有時錯，跤步踏差啥人無？",
        "彼个部長嚴重失職，煞毋肯落台負責，佇遐咧漚戲拖棚",
        "等咧喜酒食煞，彼陣好朋友欲去弄新娘",
        "遮的香油囥傷久，鼻著臭油餲臭油餲",
        "昨暗走一下傷久，害我今仔日跤牚腿",
        "我都允人矣，袂使反悔",
        "伊生做肥軟仔肥軟，看著蓋古錐",
        "我姑情伊規半工矣，伊毋答應就是毋答應",
        "伊的工課真濟，足無閒的",
        "月圍箍，曝草埔",
        "伊咧修行，無插俗事",
        "燈座傷細，徛袂好勢",
        "伊做人真豪爽，袂沙屑",
        "逐遍若叫你讀冊，你就開始盹龜",
        "窗仔有縫，風攏對遐貫入來",
        "提好，毋通摔破",
        "路頭擔燈心，路尾擔鐵槌",
        "伊做代誌足工夫，真可取",
        "戲台小人生，人生大戲台",
        "這塊碗較深，會使貯較濟湯",
        "若無才調閣硬欲賭強，是會傷害著家己呢！",
        "孤兒的命運，親像葉仔佇水面漂",
        "我臆了無毋著，物件果然是伊提去的",
        "你共烘爐提去外口搧風，按呢火才會較炎",
        "阿菊真擔輸贏，翁欠錢走路，伊家己拍拚趁錢替翁還數",
        "伊真𠢕假仙，你毋通予伊騙去",
        "囡仔摸著烘烘，可能欲感冒矣",
        "聽你咧臭彈，我就毋相信你有佮總統做伙食飯過",
        "是你毋著呢，閣敢來嚷！",
        "伊敢若牛螕咧，欲叫伊出錢是無可能的代誌",
        "我逐工共恁煮飯洗衫，就敢若恁倩的老婆仔咧",
        "熱人蠓仔厚，著用蠓仔薰來趕蠓",
        "立冬燖補，共序大人侹身體",
        "彼兩間便利商店相對相，毋過生理差真濟",
        "今仔日隔壁的門口埕停幾若台高級轎車，毋知有啥物大代誌",
        "你叫做啥物名，我雄雄煞袂記得",
        "海湧有時起，有時落",
        "伊傷貪，才會去予諞仙仔諞去",
        "你就是對人傷無客氣，才會不時咧食膨餅",
        "日本點心甜粅粅，食濟會大箍",
        "拋碇了後，咱就會當落船矣",
        "伊鬼鬼祟祟，毋知閣欲變啥魍矣",
        "落雨了後，田岸路醬醬醬",
        "你佗位無爽快，哪會咧流凊汗？",
        "大人咧處理代誌，囡仔人毋通來鬥鬧熱",
        "有燈塔的指引，船仔才會當平安入港",
        "新的總經理真𠢕轉錢空，順利解決公司的財務危機",
        "厝內若有活水來透，錢的用度就會較冗剩",
        "警察懷疑伊有紮毒品，共伊搜身軀",
        "伊有影長尻川，去人兜坐落去就毋知通起來",
        "洘旱的時陣無水通用，真艱苦",
        "伊會拍老爸，真反常",
        "千斤重擔有人擔，辛苦病疼無人擔",
        "兄弟仔定定正面衝突，冤家量債",
        "我共你使目尾，你攏無共我看",
        "冰箱內底的菜已經烏漚去矣，緊提去擲掉！",
        "東部營業處後個月月初起磅，逐家加油！",
        "伊欠人一筆數，這馬才咧四界傱錢",
        "看你按呢氣怫怫，是為著啥物代誌？",
        "這个囡仔誠硬氣，以後一定有出脫",
        "這擺的代誌做了無啥順利，才會去予人碰釘",
        "你真正有夠低路，連這款工課都袂曉做",
        "伊專門拐弄人的囡仔去做賊仔，誠歹心！",
        "人若淺緣，就袂深交",
        "工課若著頭，就會真順序",
        "過年時仔，街仔路人洘秫秫",
        "你遮爾鈍，欲按怎做生理？",
        "今仔日誠好日，幾若口灶咧嫁娶",
        "伊正經工課毋做，規日就佇遐變猴弄",
        "死矣，錢無去矣",
        "看著伊彼个死人面，我就受氣",
        "三工傷趕矣，交袂出來",
        "現代網路方便進步，有足濟人是佇面冊頂懸佮人相捌、盤撋",
        "無，恁兩个相換好矣，伊徛頭前，你徛後壁",
        "阮翁差不多暗頭仔就會轉來，你閣等一下",
        "無錢，做你共我提",
        "落雨矣，緊共雨傘褫開",
        "兄弟若仝心，烏塗變成金",
        "頭家人真好，我一半日仔無去，伊嘛袂按怎",
        "無錢毋通假大範，才袂予人吊猴",
        "鹽酸仔足臭賤的，真𠢕生湠",
        "少年的，你著聽老歲仔苦勸",
        "一陣春風吹來，予人感覺誠清彩",
        "伊有一个大肚胿，做啥物代誌攏真無方便",
        "羅漢跤仔四界流，流到南洋去",
        "我頂禮拜問你的問題，你當時會當回覆我？",
        "正經叫伊來，伊毋來！",
        "你做你大伐行，攏無欲等我！",
        "提親進前，逐家攏會去探對方的門風",
        "新正年頭，規个社會充滿快樂的氣氛",
        "遮四面攏是山，環境真好",
        "逐家先品予伊好，等咧欲耍的時毋通呸面",
        "伊逐工食飽睏，睏飽食，真正是一个閒人",
        "你毋通掛意，我會趕緊轉來",
        "囡仔大漢了後，序大人就較清心",
        "時機䆀䆀，錢愈趁愈少",
        "工課到睏尾，人雖然誠忝，嘛是袂使凊彩做做咧",
        "你遮大漢，欺負細漢的敢有𠢕？",
        "你做按呢就會使矣，毋免閣加工啦！",
        "伊是讓你，毋是驚你，你毋通軟塗深掘喔！",
        "你窗仔門關無好，風攏對空縫吹入來矣！",
        "歲頭遐濟矣，閣遮爾歹性地",
        "兩人相尋，真久攏毋分開",
        "請你手梳攑懸，原諒伊這遍的不是",
        "初見面，請你多多指教",
        "你免聳鬚，連鞭警察就來矣",
        "伊一世人勤儉，食老日子才會遮好過",
        "這塊杯仔有必痕，毋通閣用矣",
        "伊無寫功課，去予老師罰徛",
        "你遮爾驚死，是欲按怎做代誌？",
        "伊干焦一身人爾爾，無長半項",
        "歹瓜厚子，歹人厚言語",
        "毋是雙，就是奇",
        "伊這个人歹積德，後擺無好尾",
        "我毋是本地人，我是外位搬來的",
        "佇代誌猶未查清楚進前，咱逐家攏有嫌疑",
        "千算萬算，毋值天一劃",
        "已經害去矣，閣哭嘛無較縒",
        "疑人，毋成賊",
        "番薯囥咧予伊收水了後，食著較甜",
        "帶念你較早攏真認真做工課，這擺就原諒你",
        "看都好好人，哪會定定咧揣醫生？",
        "開喙就𧮙，有夠無品",
        "車咧欲開矣，你若無較緊咧就袂赴矣",
        "伊真好量，人對伊歹聲嗽，伊嘛袂抾恨",
        "官司來到尾站，較輸面的使倒頭槌，提出新證據，勢面反輾轉，倒贏",
        "咱廟裡做醮的紅龜粿，每一口灶分一个",
        "伊駛車佇臺北佮人相舂，這馬咧等警察去處理",
        "一直向前行，毋免轉斡",
        "天地遐爾仔大，免驚無所在通去",
        "田園若有收，鳥隻食得偌？",
        "我若毋是欠錢，哪著行當店？",
        "了錢無打緊，閣會害著別人",
        "伊順從爸母的意思，出國讀冊",
        "借問一下，文化路佇佗位？",
        "你頭拄仔敲電話來的時，我拄咧洗身軀",
        "伊若閣軟塗深掘，我就欲予伊好看",
        "代誌會成袂成，介在你欲做毋做",
        "生不帶來，死不帶去",
        "伊彼號豬哥性，看著媠查某囡仔就流豬哥瀾",
        "頭家，這敢猶閣有別款的？",
        "彼堆火欲化去矣，你緊去提火夾來挓火",
        "阿國仔足豬哥神的，看著媠查某喙瀾就直直流",
        "欲完成這條高速鐵路，著閣坉錢",
        "這種代誌，你毋通予彼个放送頭知影，若無，規庄仔內的人就隨攏知矣！",
        "欲走矣，緊追！",
        "伊是好意欲共你鬥相共，結果煞予你罵",
        "看人咧蹛洋樓，你敢袂欣羨？",
        "伊欠錢毋還，我提伊的跤踏車來拄",
        "彼个頭家蓋惡質，工廠刁工放予倒，家己走去外國享受",
        "看伊規日憂悶，我心內嘛真艱苦",
        "彼堵壁斜去，強欲倒落去矣",
        "朋友有代誌來央託，伊若做會到的，攏毋捌共人推捒",
        "寫甲遐爾細字，你敢看有？",
        "伊按呢共你訕潲，你敢袂艱苦？",
        "伊做伊走，放我佇遮沐沐泅",
        "老大人腸仔無力，有時會滲屎",
        "伊無張持喝一聲，逐家攏驚一趒",
        "伊送去病院進前，就無氣矣",
        "伊是阮這搭的霸王，無人敢得失伊",
        "落水平平沉，全無重頭輕",
        "警察掠著的是人頭，毋是真正的頭家",
        "你這隻暗光鳥，三更半暝矣猶毋睏",
        "關公攑關刀，過五關，斬六將",
        "閣過一个青紅燈，就會當看著兜",
        "紅尾冬，較贏食赤鯮",
        "袂曉啉酒閣啉並濟的，這馬咧茫矣乎？",
        "代先明呼明唱，才袂後日仔毋認數",
        "有當時仔食一屑仔鹹梅，會幫助消化",
        "這領衫袂當囥洗衫機洗，你去用手浞浞咧",
        "貓的奸臣，鬍的不仁",
        "你這个袂見笑的，竟然敢閣來揣我",
        "阮阿兄娶某的時陣，阮兜是家己開桌請人",
        "伊有今仔日的下場，我早就料算著矣",
        "欠錢毋還，我欲提你的翕相機來拄數",
        "恁彼个同事無，姓張的",
        "伊真有風度，共對頭恭喜",
        "伊逐改送禮，攏是大出手，毋是大鮑魚就是高麗參",
        "看起來是大姊較巧神，小妹較頇顢",
        "知影家己毋著，頭隨頕低落來",
        "平平是人，生活哪會差遐濟？",
        "阮阿公過身，打桶兩禮拜才出山",
        "若無經過這擺的考驗，你永遠袂出脫",
        "伊當咧大，一頓摁著三四碗飯",
        "偷提物件予警察掠著，有夠註死！",
        "伊做著涼勢涼勢，別人來做就無遐熟手！",
        "煞戲了後，我就送你轉去",
        "我叫阮囝共我鬥顧擔，伊煞閬港去佮人撞球",
        "這領是舒被，彼領予你蓋",
        "準做天反地亂，你嘛袂用得烏白來",
        "考了䆀，免佇遐喘大氣，趕緊用功，才有機會補救",
        "做粗工食體力，到食飯的時，腹肚就足枵燥矣",
        "人若有歲，身體就會開始厚毛病",
        "厝內當咧摒掃，恁毋通佇遐傱來傱去",
        "四月芒種雨，六月火燒埔",
        "船到碼頭，逐家攏準備欲落船",
        "我來捀碗共你貯飯，你閣小等一下",
        "伊受著老師的感化了後，就變乖矣",
        "你咧痟，我無欲綴你痟",
        "連鞭寒，連鞭熱，蜂蝦生真少",
        "明仔載免上班，會使穩心仔睏",
        "你照我的話做，保證你萬無一失",
        "人硩番薯拋過溝，咱硩番薯毋落頭",
        "彼堵壁足垃圾，你毋通並佇遐",
        "你按呢一直逃避，嘛毋是辦法",
        "蔗尾拍結做號頭，千萬毋通敨",
        "這間厝傷淺，袂當做生理",
        "伊遐爾仔少歲就來過身，實在予人想袂到",
        "頭家猶未來，咱慢且決定",
        "伊予人看破跤手矣，無人會閣再相信伊",
        "弓蕉無到分，食著末末",
        "你雄雄喝一聲，囡仔煞著驚！",
        "一旦地動，彼間厝就會倒",
        "看命無褒，食水都無",
        "伊最近無笑容，敢若有心事咧",
        "伊大箍把是好看頭，身體其實無通好",
        "我都毋去矣，伊閣較無可能去",
        "我欲食炒飯，你咧？",
        "你順這條路直直去，就會看著車站矣",
        "你拍五筒，我就到矣！",
        "已經變紅燈矣，閣硬衝過",
        "伊便若坐車，就會眩車",
        "伊規年迵天攏佇深山林內燒瓷仔，罕得轉來一逝",
        "車囥佇外口，落雨了後煞卡一沿水鉎",
        "老的老步定，少年的較懂嚇",
        "囡仔若破病，做老母的人總是會慒心",
        "這項代誌誠要緊，你緊呼請南北二路眾兄弟過來。 ",
        "頭殼挲尖尖，專門咧鑽",
        "較早若選舉伊攏共人扛轎，這擺伊欲家己出來選",
        "伊真殘忍，不時拍貓、拍狗",
        "啊都伊毋來，阮才會欠一个人",
        "彼个人規身軀癩爛癆，無人敢倚去伊遐",
        "好代毋通知，歹代直直來交纏",
        "菜市仔內，人密密是",
        "去大賣辦貨是用割價，有較俗",
        "囡仔人顧耍，連飯都毋食",
        "伊駛車進前有啉燒酒閣駛傷緊，才會發生車禍",
        "去外埠頭趁食，著較保重咧",
        "無，你是咧畫符仔是無？",
        "恁查某囝會對你大細聲，攏是你共伊寵倖的！",
        "彼條路傷狹，轎車無法度通過",
        "天然的璇石無濟又閣歹挖，所以真貴氣",
        "有的物件好趁，有的末趁，掠長補短生理猶會做得。 ",
        "阮先行，恁押後",
        "昨暗聽伊痚規暝，我實在真毋甘",
        "對今仔日起，咱就是翁仔某矣",
        "彼个囡仔黃酸黃酸，敢若飼袂啥會大漢",
        "翁佇外口有查某，伊攏無智覺著",
        "伊這站仔當咧落衰，逐項代誌都做袂順",
        "外才䆀，內才好",
        "你閣加疊一寡錢，這項物件就賣你",
        "這个庄頭無偌大，蹛無幾口灶",
        "我這陣拄好無散票，大張的予你找敢好？",
        "伊有孝大家官閣𠢕扞家，真是一个賢慧的查某人",
        "沓沓仔來，免趕緊",
        "伊誠將才，為國家計畫足濟代誌",
        "為著趁一屑仔錢，老命險無去",
        "你小扶挺一下，我來共固定予在",
        "阿母洗碗的時，盤仔煞遛手摔破去",
        "真歹勢，我欲勞煩你替我走一逝",
        "伊拍球傷出力，手骨煞脫輪",
        "伊的性敢若阿斗，予人袂扶得",
        "外地的朋友來相揣，我𤆬伊出去附近四界蹓蹓咧",
        "我共伊使目箭，伊就恬去矣",
        "這遍佳哉有你鬥幫贊，實在真多謝！",
        "你著較拍拚咧，毋通做了尾仔囝",
        "氣溫降低，人的血管會收縮",
        "真久無見面矣，高夫人最近好無？",
        "曷無咧半遂，著閣人扛！",
        "欲答應毋答應是出在你的意思，我袂共你干涉",
        "一日徙栽，三日徛黃",
        "食茶練痟話，消遣拍抐涼",
        "這條路彎來斡去，真歹駛",
        "我是放目，毋是無看見",
        "厝場好不如肚腸好，墳地好不如心地好",
        "洗藕粉，著等藕粉坐底",
        "伊做代誌傷死板，袂曉通變竅",
        "機器有佗位仔走縒，才袂振動",
        "伊是孤囝，煞猶未娶某就過身，兜就按呢無傳",
        "彼攏是謠言，你毋通相信",
        "欲按怎做，我心內有譜",
        "枕頭囊全油垢，剝起來洗洗咧",
        "伊倒手真𠢕畫圖，換手就畫袂媠矣",
        "伊出來選立委的時，有真濟好名聲的人共伊徛台",
        "人若有歲閣孤獨，人會叫伊老孤𣮈",
        "伊真為家己人，所以遐的細的攏足敬重伊",
        "欲拜託伊辦，也著前金，也著後謝",
        "你入來的時，紲手關門",
        "乖孫，過來阿媽遮",
        "日月潭的景色袂䆀，有閒咱來去行行咧",
        "這味產品是純天然成分煉成的，無透濫一寡有的無的",
        "伊毋是娶某，是予某招的",
        "伊食暗頓的時，攏會嗺一下",
        "這件代誌是頂司揤牢咧，若無早就辦矣",
        "醫生理解的掛慮，徛佇同情的立場，答應共提囡仔",
        "簽字進前，著先看予伊清楚",
        "倚海的所在鹽分重，欲種作是有較困難",
        "彼手機仔都已經有打對折矣，伊閣硬拗，叫店員送伊電池佮配件",
        "明明知影代誌真嚴重，伊嘛是蹽落去",
        "頭前地場較闊，你車開去遐大翻頭，按呢較好轉踅",
        "咱做人求平安就好，毋通痟貪",
        "阮蹛佇內山斗底，交通真無利便",
        "伊慣勢早睏，過九點就毋通閣敲電話予伊",
        "伊共花矸排做一列，予人欣賞",
        "伊不時咒讖別人，無欲檢討家己",
        "我的胸坎實實，人真無爽快",
        "想著這件代誌，我就失眠睏袂去",
        "衫洗久，料身會虛去。 ",
        "梨仔誠厚重，無幾粒就三斤矣",
        "較緊睏！無，虎姑婆欲來矣",
        "送彼做禮物傷料小，恐驚無夠看",
        "藥粕無啥物藥效，會使擲掉矣",
        "物件猶閣好好你就毋挃矣，按呢敢袂傷討債？",
        "你欲出門做你去，囡仔交予我管顧就好",
        "生有時，死有日",
        "這馬景氣無好，較歹過日",
        "雨落遮爾大，我看會淹大水",
        "你的文章寫了真好，會使去投稿矣",
        "伊目睭𥍉𥍉看，向望老母會轉來𤆬伊",
        "彼班搝大索搝贏，逐家攏足歡喜的",
        "頂幫毋是已經修理好矣，哪會閣歹去？",
        "為著身體健康，你上好改薰",
        "伊雖然人生做矮肥矮肥，毋過跤手真扭掠",
        "昨日暗，阿公有託夢予我",
        "阿爸的身材中範中範，看起來袂肥嘛無偌瘦",
        "我人已經共你揣來矣，看你是欲按怎發落？",
        "伊食物件有夠討債，定定賰一半就欲挕捒",
        "伊提錢欲共警察楔空，警察顛倒共罰較濟錢",
        "這阮查某孫，頂禮拜才大學出業",
        "我欲揣校長，勞煩你通報一下",
        "高麗菜先豉鹽才落去炒，食著加真脆",
        "小徙跤咧，人咧摒掃",
        "恁翁真體貼你，真𠢕共你照顧",
        "一兼二顧，摸蜊仔兼洗褲",
        "遮的貨賣完嘛干焦夠工爾爾，也無啥趁",
        "伊根本都毋捌字，哪會曉寫批？",
        "阮搬來下港二十年矣，早就釘根矣",
        "虱目魚的幼骨仔誠濟，你著細膩仔食",
        "這遍的旅遊，費用攏由公司負擔",
        "山路真狹，駛較慢咧",
        "錢是伊欠的，佮我無相干",
        "阮欲走矣，你咧？",
        "這粒菝仔傷𠕇，我咬袂落去",
        "熱人到矣，電風好提出來矣",
        "你等一下，我隨來",
        "受訓了後，逐家會分發去無仝的單位",
        "你若閣為非糝做，別日仔你就會無好死",
        "伊受著枉屈，才四界咧哭呻",
        "頭家，賰的我總貿，你算我較俗咧",
        "伊暗崁足濟外路仔做私奇，無予某知",
        "陳三五娘相𤆬走的故事，佇臺灣真受歡迎",
        "財子壽，難得求",
        "這粒西瓜到分矣，真甜真好食",
        "法律之前，人人平等",
        "伊貸款納袂出來，厝就予人拍賣矣",
        "叫某去趁食，家己做烏龜，真正袂見笑",
        "勢面若䆀，你就緊抽退",
        "佇遐變規晡，毋知伊咧變啥物魍？",
        "天氣遮寒，食火鍋正當時",
        "這本諺語集所收的臺灣話，逐句都仁仁仁",
        "世間人攏真自私，干焦知影顧家己的利益",
        "你若無較乖咧，我就共你掠來拍尻川",
        "予老母為著這件代誌佇遐激心煩惱，實在是太不應該",
        "徛佇尾溜彼个，你敢捌伊？",
        "嬰仔滿月，阿媽真歡喜，備辦雞酒來請親情、厝邊",
        "有誠濟較早的代誌，我攏袂記得矣",
        "這个囡仔欲食毋討趁，有夠了然",
        "步頻欲叫我做編輯的工課，我做無路來",
        "伊真荏身，磕袂著就破病",
        "你做人大兄閣一日到暗佮小弟冤家量債，敢袂歹勢？",
        "食雞，會起家；食鰇魚，生囡仔好育飼",
        "伊今年畢業，這馬當咧揣頭路",
        "公司倒去的代誌，予伊真大的打擊",
        "伊若是欲食毋討趁，後擺就會予人看袂起",
        "月暗暝行路，有人陪伴，就較在膽",
        "伊定定用媠查某囡仔做釣餌，來騙人的錢",
        "查某人做月內的時，若無細膩著著月內風，是會交纏一世人喔！",
        "伊足久無頭路矣，規个人看著死殗殗",
        "伊的人真雜插，啥物代誌都欲管",
        "翁仔某一个虎豹母一个雷公性，毋知按怎鬥陣",
        "下昏我有一个食飯會，無欲轉去食暗矣",
        "伊做人欺貧重富，佇庄仔頭名聲誠䆀",
        "頭興興，尾冷冷",
        "彼个烏心肝的人，早慢會有報應",
        "弓蕉去予風颱掃倒了了，咱著較儼硬咧，重來",
        "這罐芳水較低級，毋是高級貨",
        "遮的物件舊漚舊臭，閣毋甘擲㧒捔",
        "遮爾好的機會，你是閣咧躊躇啥物？",
        "伊足急性的，無像我遐𠢕拖沙",
        "頭仔興興，尾仔冷冷",
        "你小忍耐一下，連鞭就好矣",
        "伊的頭挵著壁，腫一癗",
        "你著較大路咧，毋通遐凍霜",
        "只要有你，代誌就會成功",
        "這个辦法有通，咱就按呢試看覓",
        "伊這站仔誠懶屍，啥物代誌攏無欲做",
        "真罕行，你今仔日哪有閒通來？",
        "伊跋落去山溝，跤骨摔斷去",
        "教囡仔行五子直，會當提升的智力",
        "歹勢，我較柴目，袂記得咱是啥人，咱敢有相捌？",
        "扳予牢，毋通放",
        "咱來比賽射鏢，看啥人較準",
        "伊雄雄傱出來，害我掣一趒",
        "你緊共雨傘展開，無，會沃澹去！",
        "筅黗以後，就準備過年",
        "我是一个出外人，我的故鄉佇臺東",
        "小說人物玉卿嫂就是佇外口飼花眉，心甘情願共伊照顧",
        "兩人偷來暗去，通庄頭的人攏嘛知",
        "這只是暫時過渡，逐家較忍耐咧",
        "伊為著離緣的官司，去旅社掠猴",
        "你做代誌著較安份咧，毋通痟貪軁雞籠",
        "我都猶未食半喙咧，你就捽了了矣！",
        "伊生做人懸漢大，氣力飽，夯的貨自然比人較濟",
        "聽你一工到暗咧誦經，實在有夠𤺪的",
        "阮阿公七十歲大壽的時陣，阮兜有辦桌請人",
        "阮兜捌飼過花眉，歡喜的時就一直叫，若咧唱歌咧",
        "伊戇戇坐佇遐，毋知咧想啥",
        "毋免抄啦，提去影印較緊",
        "若是攏無人欲去，咱就抽鬮來決定",
        "頭拄才洗好，膨獅獅",
        "規間厝搜透透，攏揣無",
        "你就是攏無修行，性地才會遮爾仔䆀",
        "伊雖然生做戇頭戇面，毋過心肝真善良",
        "你真正咧老顛倒矣，昨昏的代誌今仔日就袂記得",
        "愈落伍的國家，楔後手的現象愈普遍",
        "這幾日雨澹水滴，路不時攏𣻸塌塌",
        "這陣的股市行情誠好，伊攢兩千萬，存範欲大抐一下",
        "慢慢仔是，免著急",
        "這支刀有夠鈍，切肉若咧鋸肉",
        "伊做代誌真浮冇，我袂放心",
        "較早踮厝內，大囝的責任較重",
        "規欉好好，無錯",
        "有人咧叫門，你去看是啥物人？",
        "伊早起跋倒，去頓著尻川",
        "這領衫皺皺，你共熨較伸咧",
        "伊雄雄發性地，逐家攏予伊驚著",
        "馬四跤，有時也會著觸",
        "自從離開故鄉，每日思念爸母",
        "代誌若有小可撞突，伊就袂食袂睏矣",
        "你佇遐牛聲馬喉，有夠噪人耳，較細聲咧",
        "阿美翁真靠俗，真好鬥陣",
        "叫你加疊一領衫你就毋，這馬去寒著矣乎！",
        "老爸放予伊的財產，伊無幾年就刜了了矣",
        "伊開始咧陣疼，應該欲生矣",
        "就是有人陷害，伊才會來枉死",
        "人共伊歹，伊毋但毋驚，閣敢佮人㧣",
        "伊一个查某人飼兩个囡仔，雖然艱苦，生活猶會得過",
        "我都合袂拄好，袂當參加這遍的同窗會",
        "人咧叫你，你嘛共人應聲一下",
        "你斟酌一下，應該聽會著",
        "伊拄失戀，逐工攏心慒慒",
        "恁查某囝實在真活動，一直走來走去",
        "頭昏昏，腦鈍鈍",
        "無聊的時陣，就來變工藝",
        "真歹勢，無張持共你挨著",
        "這幾年來，社會一直咧轉變",
        "看這个範勢，無走袂使矣！",
        "我細漢的時，序大人有教我用母語暗唸三字經",
        "予伊掠龍了後，規身軀攏誠爽快",
        "親情有禮數相伨，較會親",
        "你實在是儑頭儑面，伊是頭家的姨仔，你曷敢對伊大細聲",
        "無靠戇膽，哪會敢去啊！",
        "有錢就烏白拍翸，較濟嘛無夠開！",
        "阿達仔是一个佬仔，你毋通予伊騙去",
        "寒著蓋被翕汗，較緊好",
        "頂港有名聲，下港上出名",
        "遮痠遐疼，我身軀已經規組害了了矣",
        "人生在世，毋免傷計較",
        "這馬咧烏陰矣，較停仔無的確會落雨",
        "無伊共你點醒，你較想嘛想袂清楚",
        "毋知這个嬰仔是佗位仔咧袂拄好，騙攏袂恬",
        "你去四箍輾轉揣看覓，看彼个囡仔覕佇佗位？",

        "蓮藕粉摻糖煡煡咧，真好食",

        "這桶水圇圇仔，拄仔好會使洗身軀",

        "這个人是火烌性，較會得失人",

        "賣貨頭，卸貨尾",

        "張總的頂擺出張，去巡視海外的工場，佇遐蹛個外月",

        "這張圖真媠，我欲描一張起來",

        "伊古意閣好笑神，真深緣，予人愈看愈中意",

        "這口灶的囝孫仔，逐个都真出擢",
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