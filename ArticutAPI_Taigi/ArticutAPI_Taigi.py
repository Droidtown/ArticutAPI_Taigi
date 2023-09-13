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
            self.userDefinedDICT["ENTITY_person"] = personLIST
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
    #台語漢字 CWS/POS TEST
    inputSTR = "你ē-sái請ta̍k-ke提供字句hō͘你做這個試驗。"
    inputSTR = "跋倒, 佮意"
    inputLIST = [
    "這支茶罐看著烏鉎烏鉎，泡出來的茶煞真好啉",
    "阮囝逐擺食飯攏愛硬押，伊才欲好好仔食",
    "伊頭先講好，尾手閣講無愛",
    "好人予你做，我來做臭人",
    "七分酒對三分水上拄好",
    "工頭工尾攏愛顧好",
    "囡仔墜腸，有的家己會好去，大部份攏愛去開刀治療",
    "物件揀好去揣店員結數",
    "你若無坐好，等一下就會吭跤翹",
    "經濟變好了後，誠濟平階攏拆掉換起樓仔厝",
    "你毋通為著人有好的物件就赤目",
    "一下仔久就好矣",
    "逐家共椅仔小促較倚咧，較好夾菜",
    "咱來去踅街，看有啥物通好買",
    "我拄欲出去揣你，你拄好轉來",
    "你愛加減食一寡，病才會較快好",
    "時機䆀，厝賣無好價",
    "飯疕搵糖是較早的囡仔放學轉來上好的點心",
    "禮拜時仔，朋友相招出去食好料",
    "兜是好額人，逐頓食的攏是山珍海味",
    "代先籌備好勢，代誌才好做",
    "厝起好，內面著成格",
    "一屑仔代誌都辦袂好勢，真下痟！",
    "好歹攏是家己的囝，你就看較開咧",
    "伊確實是一个好人",
    "先規劃予好，才來執行",
    "提出較好的條件對方就會投降",
    "喂，你好，麻煩請阿珠聽電話",
    "路口彼間藥局生理真好",
    "我昨昏去揣伊，真拄好，伊人無佇咧",
    "較早的人講，查某人月內若無做好，後擺身體會較䆀",
    "你三點鐘才做會好，伊半點鐘就做好矣",
    "新正年頭見面攏會講好話",
    "等一下麻煩你出喙共我鬥講寡好話好無？",
    "這个接喙黏無好勢，強欲裂開矣",
    "若按呢愈好",
    "你先去添飯，連鞭湯捀出去就聽好食飯矣",
    "好酒沉甕底",
    "我功課若寫好就會使去看電影矣",
    "聲聲句句講欲做好囝，串做攏予人受氣的歹代誌",
    "伊對我真好",
    "冇粟收入好米籮",
    "醫生講伊這个病會好也袂斷根",

    "糋好的芋仔糋欲食進前愛閣乍一下",
    "你看我穿按呢敢好？",
    "欲買的衫揀好矣未？我欲來去納錢矣喔！",
    "衫紩好，線頭愛拍結",
    "阮查某囝若嫁予你，你就愛好好仔共伊疼痛",
    "伊數學的底蒂真好",
    "鹽一撮仔就好矣",
    "番薯礤簽煮糜真好食",
    "親情條直好唯是，聘金濟少由在伊",
    "阿公那挨二絃那唸歌，足好聽的",
    "歹船拄著好港路",
    "伊上班時間走出去摸飛，好死毋死去予頭家㨑著",
    "伊拄仔交落身，著愛好好仔侹身體",
    "若欲參選，伊的背景真好",
    "閣來就是寒人矣，寒衫愛先準備予好",
    "伊一定是頂世人燒好香，才會娶著遮爾好的某",
    "閒閒無代誌，罔行嘛好",
    "病好離離",
    "以前的人對屎礐仔舀屎尿起來，囥予伊發酵過，變做大肥，就聽好沃菜",
    "你著愛紮雨傘去，毋拄好落雨就用會著",
    "這鼎肉我滷規下晡，保證好食",
    "舊鞋較好穿",
    "手去洗洗咧，聽好食飯",
    "這个庄頭的人攏真好客",
    "醬瓜仔配糜真好食，毋過毋好食傷濟",
    "今年頭水的柚仔真好食",
    "過年時仔，人攏會講幾句仔好話",
    "你有啥物好的計謀？",
    "今仔日天氣無好，你出門的時愛會記得紮雨幔",
    "伊昨昏都有較好矣，是按怎今仔日閣反症？",
    "感冒猶未好，毋通出去剾風",
    "景氣無好，失業的人誠濟",
    "共你辦好勢矣",
    "咱七月半普渡彼工，菜碗著攢較腥臊咧，來拜好兄弟仔",
    "這部份是我管的，問我就好",
    "我才搬來，猶未安搭好勢",
    "衫攏洗好矣",
    "面前咱所拄著的問題攏無法度解決，是欲按怎才好？",
    "你去摺衫好無？",
    "雖然我佮恁阿爸平歲，毋過論輩無論歲，咱算仝沿的，叫我阿兄就好",
    "足饞的，咱來食四秀仔好無？",
    "你直接提去予伊毋就好矣，哪著閣用寄的？",
    "囡仔人無規矩真正毋是款，無好好仔管教袂使得",
    "印彩色的加真傷本，印烏白的就好",
    "今仔日誠好日，幾若口灶咧嫁娶",
    "病若欲緊好，無噤喙是袂用得",
    "番薯𠢕湠根，真好種",
    "以前遐衛生無好，有真濟人著寒熱仔",
    "伊定定講人的好話",
    "你誠好運！",
    "好得無去，無，煞加走一逝",
    "錢絞錢，才好趁",
    "這條提案逐家已經討論好勢，紲落來咱就來表決",
    "代誌欲對佗位落手才好？",
    "這是我親手做的，做了毋是真好，請你毋通棄嫌",
    "咱已經品好矣，希望你毋通反僥",
    "伊舊年考無牢，今年閣考，考了真好",
    "欲過年矣，你聽好去清數矣",
    "你寒著才好爾爾，毋通出去外口剾風",
    "阿英，好來食晝矣",
    "做人若會曉看破世情，會較好過日",
    "這上緊嘛著愛到後日才會好",
    "伊上愛膨風，你毋好予伊騙去",
    "阿英佮我是一粒一的好朋友",
    "一百五十二箍，算齊頭，收你百五就好！",
    "伊的漢草真好",
    "你毋好一日到暗拋拋走",
    "見擺你都按呢講，見擺攏做袂好勢",
    "伊對我遮爾好，我煞無法度共伊鬥相共，心內感覺真虧欠",
    "好禮仔坐，無，會倒摔向",
    "摒掃的工課予倩的去做就好矣！",
    "你做的發粿發了真好",
    "這擔的肉餅真好食",
    "看伊滿面春風，一定有啥物好代誌",
    "門愛圈予好",
    "你免咧假好衰啦",
    "咱人著愛存天良、做好代",
    "無愛插伊，伊煞愈好款",
    "設使會當自由行徙，毋知有偌好咧！",
    "好心煞予雷唚，想著誠厭氣",
    "咱出外較無方便，若會當凊彩揣一个所在倚蹛就好矣",
    "講正經的啦，你嘛愛揣一个好的頭路",
    "拄著歹人客來咧花，咱雖然氣暢忍，嘛著好禮仔共伊安搭",
    "沓沓仔粒積，年久月深，伊已經變做好額人矣",
    "藥頭兩碗水煎做八分就好",
    "這種漆的色水真好看",
    "前某對人誠好，予人誠感心",
    "緊行無好步",
    "跤步踏差啥人無？只要改過就好矣",
    "物件愛收予好，欲用的時才袂揣無",
    "伊相信人的命運早就註好好矣",
    "人來就好，毋免紮啥物等路啦！",
    "煙腸用烘的較好食",
    "外才䆀，內才好",
    "物件囥蹛桌頂就好",
    "幼秀跤好命底",
    "阿英仔真好笑神",
    ]
    articutTaigi = ArticutTG(username=accountDICT["username"], apikey=accountDICT["apikey"])
    for inputSTR in inputLIST:
        #inputSTR = "你莫一直掠人金金看！".replace("。", "")
        resultDICT = articutTaigi.parse(inputSTR, level="lv2")
        pprint(resultDICT)
    #<ENTITY_pronoun>[^<]+</ENTITY_pronoun>(<FUNC_inner>[^<]+</FUNC_inner>)?<ENTITY_noun>[^<]+</ENTITY_noun><DegreeP>[^<]+</DegreeP>