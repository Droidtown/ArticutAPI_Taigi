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
    articutTaigi = ArticutTG(username=accountDICT["username"], apikey=accountDICT["apikey"])
    #台語漢字 CWS/POS TEST
    inputSTR = "你ē-sái請ta̍k-ke提供字句hō͘你做這個試驗。"
    inputSTR = "跋倒, 佮意"
    inputSTR = "伊誠𠢕激五仁，激甲逐家笑咍咍".replace("。", "")

    inputLIST = [
        #"閣來就是寒人矣，寒衫愛先準備予好",
        #"拄著歹人客來咧花，咱雖然氣暢忍，嘛著好禮仔共伊安搭",
        #"人講：「驚某大丈夫，拍某豬狗牛。」你著愛好好仔疼惜恁牽手才著",
        #"這个囡仔四個月爾爾就真硬插，足好抱",
        #"曝焦收入來的衫愛摺摺咧",
        #"硬拄硬一工著愛兩千箍倩人顧",
        #"你定定愛家己一个走去無救生員的海邊泅水，緊縒慢會出代誌",
        #"你家己做毋著，愛有自覺",
        #"阿英都無愛你矣，你猶閣綿死綿爛咧求伊，你哪會遮戇啦！",
        #"彼箍若相拍雞仔，無人愛參伊鬥陣",
        #"錢愛共伊掜起來，無，伊會亂開",
        #"錢愛挽咧用，毋通開了了",
        #"錢愛紮較冗咧",
        #"這張字紙頂懸有寫講你愛還偌濟錢",
        #"煮魚仔湯愛用燒酒壓味",
        #"各人的物件愛顧予伊好",
        #"就是你無來，毋才愛請伊來鬥相共！",
        #"行到雙叉路口，毋知愛按怎行",
        #"這筆錢愛報銷",
        #"你愛有出脫人才會看你有",
        #"咱文化的根愛顧予伊牢",
        #'阮明仔載就開始歇寒，免去學校上課矣,',
        #'伊毋去病院予醫生看，甘願買藥草仔烏白食,',
        "衫仔櫥內有一領西裝",
        '伊話講煞，隨越頭做伊去摔大眠,',
        '彼陣人講無三句話就起迸矣,',
        '彼項代誌伊共我講矣,',
        '伊較講都講袂翻捙，有夠聬儱,',
        '伊講的話有夠譀古,',
        '照講我按呢做應該無毋著，哪會失敗咧？,',
        '無，你是佇咧講笑詼是毋？,',
        '連參詳一下都無通，閣欲講東講西，你實在真聬儱,',
        '伊是𠢕講爾爾，正經叫伊做是無半撇,',
        '閣講嘛是無彩工,',
        '阿三仔誠臭煬，不時講家己偌𠢕拄偌𠢕,',
        '干焦共伊講兩句仔，伊就閣開始咧覕喙矣,',
        '伊講遐的話是咧共你剾洗,',
        '伊講伊大後日會倒轉來,',
        '你若無講話，人嘛袂共你當做啞口,',
        '就算講你無中意，阮嘛無法度,',
        '我欲佮伊本人講話,',
        '像你講的,',
        '江湖一點訣，講破毋值三仙錢,',
        '伊講白賊去予阿母搧喙䫌,',
        '無證據毋通烏白講,',
        '我咧佮你講話，你是按怎攏毋應話？,',
        '彼陣人講無兩句，家私就攏捎出來矣,',
        '你是咧陷眠是無？無，哪會講彼號無影無跡的話,',
        '我若講會到就做會到,',
        '伊講遐的話是為著欲敨氣，你聽了準煞,',
        '頭家臨時講欲開會，我無時間通攢資料,',
        '請你講較具體咧,',
        '有人講羊仔肉真臭羶,',
        '你是咧講啥潲？,',
        '相命仙共伊看手相講：「手縫櫳，財產空，隨趁隨空空。」,',
        '講伊是留美的博士，偌𠢕拄偌𠢕，予人黜一下隨破功,',
        '古早人講：「姑表相伨，親疊親。」這馬袂使矣,',
        '伊講話落風落風,',
        '嘿，你講按呢著,',
        '你曷使講彼號話？,',
        '講了真清楚,',
        '啥物人講講話大聲就贏？無這款道理啦！,',
        '講予伊知,',
        '你歁歁呢，敢佇伊的面頭前講白賊,',
        '這曷著講？,',
        '聽講深山林內有足濟魔神仔,',
        '人講這个神壇的符仔真靈,',
        '你講手指月娘會予月娘割耳仔，彼是欲騙囡仔的，我予你袂食聲得,',
        '伊定定講白賊，所以這馬攏無人欲插伊,',
        '加話減講寡,',
        '聽講這款藥仔會當通血路，毋知有影無？,',
        '老大人規日坐佇厝內，毋出去佮人開講，會一直侗戇去,',
        '你講過的話，一定愛會記得,',
        '較早的人講，查某人月內若無做好，後擺身體會較䆀,',
        '人講：「食佇面裡，穿佇身裡」，穿插若傷凊彩，人看袂上目,',
        '講無路來,',
        '咱咧講話，有時會插濫幾若種語言,',
        '飯會使烏白食，話毋通亂講！,',
        '彼箍講的話我攏無咧共\uf5ea,',
        '我無贊成你的講法,',
        '新正年頭見面攏會講好話,',
        '伊大舌所以講話袂輾轉,',
        '阿美定定佮我講私奇話,',
        '等一下麻煩你出喙共我鬥講寡好話好無？,',
        '伊的話講了較正範,',
        '我共你偷講，你毋通共別人講,',
        '這个囡仔講嘛講袂聽，實在無法伊,',
        '你佮伊講母語嘛會通,',
        '你講的我攏明白矣,',
        '若講著鵝肉冬粉料理，我就會流喙瀾,',
        '恁撨好勢才共我講結果,',
        '心肝內懷疑，但是毋敢講,',
        '李的定定無佇咧，\ue701某囝敢攏袂講話？,',
        '氣象講這幾工攏是烏陰天,',
        '我聽你咧講嘐潲話,',
        '彼个查某囡仔講話真大範,',
        '伊所講的佮事實有真大的出入,',
        '去對伊講,',
        '聲聲句句講欲做好囝，串做攏予人受氣的歹代誌,',
        '共你講這領褲傷絚你毋信，這馬裂開矣啦,',
        '恁毋通傷超過，頂頭咧講話矣,',
        '醫生講伊這个病會好也袂斷根,',
        '伊話猶未講出喙，就已經喉滇目箍紅矣,',
        '人講「食緊挵破碗」，你著照步來,',
        '\ue701嗤舞嗤呲佇遐咧講人的歹話,',
        '報名參加講習會,',
        '按呢講有通,',
        '伊佇尻川後講人的歹話,',
        '你按呢講無毋著,',
        '你敢講欲瞞騙伊一世人？,',
        '講伊規工若干樂是一个譬喻,',
        '雙爿講的話無走縒,',
        '按怎講都毋聽,',
        '聽伊講話就知影伊真有智識,',
        '聽人講這間媽祖廟的神明真有靈聖,',
        '伊講的話譀呱呱，敢有人會相信？,',
        '就我來講，我並無贊成伊的做法,',
        '你這个番婆！我講無提就是無提，你是欲諍到當時？,',
        '過年時仔，人攏會講幾句仔好話,',
        '人講食豬血會去垃儳,',
        '叫你毋通講你閣講，我實在活欲予你氣死！,',
        '\ue701兩个是毋是會結婚猶真僫講,',
        '代誌明明都伊做的，伊硬拗講是別人,',
        '外口當咧風聲講金仔欲起大價矣,',
        '聽伊講遐的話，真正會予伊惱死,',
        '伊講話誠歹聲嗽，予人聽著心肝頭袂爽快,',
        '咱來輸贏，看啥人講的較著,',
        '臺北人講烏白切，嘉義人講滷熟肉,',
        '厝邊咧凌治某囝，咱著通報113專線，毋通想講佮咱無底代,',
        '做股票了幾萬箍仔，對伊來講無礙著,',
        "幾十箍仔、幾千箍仔，幾箍仔，幾十箍、幾千箍，幾箍",
        '伊身懸較矮人，講話顛倒較大聲,',
        '你講的話敢有影？,',
        '這間厝的裝潢普普仔爾爾，無講偌媠,',
        '你講話傷過份,',
        '伊實在真軟汫，予人講兩句仔就流目屎矣,',
        '講著偌俗拄偌俗，結果比人加貴百外箍,',
        '千外箍,',
        '萬外箍,',
        '你按呢講會去傷著伊的自尊心,',
        '\ue701兩个兄嫂小姑誠有話講,',
        '伊講這件代誌是伊親目看著的,',
        '伊頭仔講欲去，尾仔煞反悔,',
        '話講無幾句，伊就起雄矣,',

        '伊生做矮矮，袂講蓋懸,',
        '我上討厭彼種講話無信用的人,',
        '逐禮拜五暗時七點，伊準時佇遮開講,',
        '我想講已經暗矣，歹勢共你攪吵,',
        '這層代誌咱後日才閣講,',
        '你講較簡單咧，伊才聽有,',
        '歁話講規擔,',
        '伊講話真有力,',
        '見講攏遐的話,',
        '聽講伊的工夫真厲害,',
        '這層是實抑是虛猶毋知，你毋通綴人烏白講,',
        '我挖心肝予你看，敢講你閣毋相信？,',
        '好好仔講就好，毋通按呢起跤動手,',
        '伊都開喙咧講矣，咱就照伊的意思去做好矣,',
        '\ue701講欲去夜市仔看人拍拳頭賣膏藥,',
        '請問你敢會曉講客話？,',
        '你閣講一遍,',
        '伊棍仔攑咧無講無呾就撼來，佳哉我緊閃開！,',
        '若講著車，伊是內行的,',
        '這件代誌我代先佮伊講好矣,',
        '伊真𠢕講話,',
        '伊是一个土人，講話較凊彩，你毋通佮伊計較,',
        '伊掠我金金相，講我佮\ue701查某囝生做仝款仔仝款,',
        '伊咧講啥物，我差不多攏聽無,',
        '伊酒啉甲馬西馬西，話捎咧亂講,',
        '咱來去茶館啉茶開講,',
        '伊串講攏講涼腔，免聽啦！,',
        '伊講話攏帶一个話母,',
        '是啥人遮𠢕牽？講遮久,',
        '伊講話的氣口真大！,',
        '我佮伊講話講了真投機,',
        '講無兩句話伊就共對方㧌落去矣,',
        '的確的代誌才通講,',
        '伊講話按呢反來反去，毋知伊到底是欲按怎,',
        '你是按呢講的嘛！,',
        '醫生講伊無要緊，你毋免煩惱啦！,',
        '氣象報告講會好天煞咧落雨,',
        '食人頭鍾酒，講人頭句話,',
        '唅？你講啥？,',
        '我若講伊幾句仔伊就無歡喜,',
        '土人講土話,',
        '伊共你𥍉目，就是暗示你毋通加講話,',
        '這句話翻做英語欲按怎講？,',
        '評審嚴格，逐家就無話講,',
        '伊講話定定會咬舌,',
        '袂曉就講袂曉，毋通袂博假博,',
        '這袂歹啉，是講，啉了對身體敢無敗害？,',
        '我來去共你講親情,',
        '講欲提一寡舊衫予我，到今閣無半絲,',
        '聽講擴頭的囡仔較巧,',
        '聽講張飛有羊仔目,',
        '為著欲娶你做某，就算講嘔心血，我嘛甘願,',
        '\ue701講話誠投機,',
        '伊講話真歹喙斗,',
        '謼，好啦，你講的準算,',
        '伊親喙講的，袂假啦！,',
        '根據伊的講法，咱應該著較早出門才著,',
        '伊講話的聲音真好聽,',
        '我聽講恁查某囝欲予人送定矣，敢有影？,',
        '伊德語講了真輾轉,',
        '這件代誌咱毋是頂日就講好矣？,',
        '你講若你講，我才毋相信,',
        '伊講當選了後，欲整頓市場，結果攏無影跡,',
        '這種無情理的話，干焦你才講會出來,',
        '代誌到這个地步矣，你猶閣有啥物話通講？,',
        '伊跋倒，雖然人無按怎，醫生講猶是照電光確定骨頭無含梢較好,',
        '我是凊彩講的，你毋通囥佇心肝內,',
        '鋪排話免講,',
        '伊穿的衫真講究,',
        '你這句廢話，有講等於無講,',
        '我講一句伊就拄一句,',
        '我聽你咧講啥物譀話！,',
        '譬論講你若做市長，你欲按怎來改革市政,',
        '伊真固執，予人袂講得,',
        '人講雙生仔定定會互相感應,',
        '你去看覓，才來共我講,',
        '對面的樓仔厝聽講欲拆掉重起,',
        '是講，伊哪會無去,',
        '你做一遍總講出來,',
        '伊嫌\ue701翁頇顢講話,',
        '伊講的是\ue701故鄉的土話，我聽攏無,',
        '你講彼號無空的,',
        '伊講話誠查某體,',
        '你的代誌叫我出錢，你是咧講啥物痟話？,',
        '你講這種話實在無意無思,',
        '伊足足講一點鐘的電話,',
        '伊定定講話共人侮辱,',
        '伊講的話其中有一寡問題,',
        '講風颱欲來矣，結局煞無來,',
        '未來社會會變按怎，真歹講,',
        '講話無攬無拈,',
        '恁阿公老番顛矣，講話去去倒倒,',
        '彼个外國人講臺語定定會走音,',
        '伊敲電話講欲來，隔轉日伊就來矣,',
        '講無兩句就搩起來矣,',
        '伊講話攏會共人刮,',
        '徛算講伊較毋捌代誌，你小讓伊一下,',
        '選舉的時，逐个候選人都講伊上好央教的,',
        '伊講這句話，有另外的作用,',
        '伊彼支喙佮機關銃仝款，講袂煞,',
        '你講這款話是啥物意思？,',
        '因為時間袂拄好，我才無去聽伊演講,',
        '伊覕佇門後咧偷聽人講話,',
        '我看伊面腔無偌好，毋敢加講話,',
        '聽講公司欲調整人事,',
        '佮伊講話，見講嘛講袂伸捙,',
        '老師共我講：「你猶少歲，日子猶誠長，前途著拍算一下。」,',
        '你心內有啥物冤屈，攏講出來無要緊,',
        '伊那講那流目屎，予人看著會心酸,',
        '明仔載的代誌明仔載才閣講,',
        '你記持誠䆀，隨講隨袂記得,',
        '伊講的話前後顛倒反，毋知影佗一句才是真的,',
        '伊講話喑噁，我攏聽無,',
        '講著臺北，伊真是頭目鳥,',
        '講著錢就攝落去矣,',
        '毋通定定講大話,',
        '這場演講足足有三點鐘,',
        '你敢毋驚人講？,',
        '頭家講欲招待逐家去日本𨑨迌,',
        '論真來講，你嘛有毋著，著共伊會失禮,',
        '伊的代誌講三工嘛講袂盡,',
        '你共心內的掛礙講出來逐家參考看覓,',
        '伊講遐的話是咧共你倒削,',
        '你敢講恁老師講了毋著，真正足有勇氣,',
        '伊驚一趒，那搭胸坎，那問講是按怎樣,',
        '算命仙的講\ue701兩人的八字袂合,',
        '佮序大人講話袂使無大無細,',
        '總講一句，是你家己做得來的，毋免去怪別人,',
        '伊見笑轉受氣，講話才會大細聲,',
        '講話攏無考慮，當然會失言,',
        '喙講無憑,',
        '我若緊張就會大舌，話攏講袂清楚,',
        '這个職位對你來講有較委屈,',
        '聽伊講話的腔口，就知影伊是在地人,',
        '囡仔人講話毋通遐爾粗,',
        '無論你講啥，我攏袂答應,',
        '\ue701親情內底有一个大官虎，講話攏會硩死人,',
        '伊若啉酒醉，攏講伊無醉,',
        '聽講這款藥仔會當止嗽化痰兼顧肺管,',
        '這種代誌你毋著冗早講，這馬欲反悔已經袂赴矣,',
        '你講了傷過頭矣，伊無影遮爾歹,',
        '你共恁爸講予伊清楚,',
        '伊去媽祖宮下願，講\ue701老母的病若會好，伊就欲倩一班歌仔戲來謝神,',
        '氣象報告講今仔日有大湧，你毋通去釣魚,',
        '講話毋通傷厚話屎,',
        '阿榮當咧轉大人，講話鴨雄仔聲,',
        '你誠毋知輕重，這款話你曷講會出喙,',
        '你有欠用就來共我講，我會當借你,',
        '\ue701兜足好額的講,',
        '有人講躡跤尾行路會減肥呢,',
        '我聽講別搭的價數比遮較俗,',
        '你若閣講袂聽，原性不改，以後食苦的是家己,',
        '我堂堂一个男子漢大丈夫，講會到就做會到,',
        '聖拄聖，我才臆伊無欲來，伊就敲電話講欲請假矣,',
        '逐家攏想講伊應該會贏，早就準備欲共伊恭喜矣,',
        '阮兜是阮某咧攏權的，有啥物代誌麻煩你共阮某講,',
        '我才無欲相信你講的話！,',
        '話講一半，就頓蹬。,',
        '伊解說先生傳授的道理，攏講了有倚意,',
        '看著\ue701有身的新婦佇咧摒掃，阿婆就會喝講：「大身大命喔！我來就好。」,',
        '有一寡政治人物，干焦佇選舉的時，才較捷講母語來佮民眾跋感情,',
        '氣象報告講明仔載會比今仔日較寒,',
        '氣一下袂講話,',
        '你話袂使濫使講,',
        '伊真𠢕講白賊話，你予伊騙去矣,',
        '你按呢講會得罪足濟人,',
        '伊有誠濟枉屈無地講,',
        '先看款才講,',
        '雙方講和,',
        '仙講都毋聽,',
        '無講無呾,',
        '伊真𠢕變面，你毋通佮伊講耍笑,',
        '咱人毋通烏白講人的長短,',
        '伊講話真文雅,',
        '我毋講，予你臆,',
        '人講拜菜頭是欲求一个好彩頭,',
        '我無聽著你咧講啥,',
        '人講姻緣是天註定，若是無緣，閣較按怎強求嘛無路用,',
        '阿姨毋是外人，你講，無要緊,',
        '伊講遐的話純然是咧騙你,',
        '我的話才講一半，就予伊拍斷去,',
        '伊講話重句，愈緊張愈嚴重,',
        '伊四界放風聲，講欲揣你算數,',
        '我見面就講伊袂佮咱合股,',
        '蠓仔會傳播疾病，毋通想講予蠓叮著，極加是足癢爾爾,',
        '講話著伸手摸心肝，毋通含血霧天誣賴人,',
        '我想一睏才了解伊講彼句話的意思,',
        '咱先明品一下，講過就準算，毋免保家,',
        '講話毋通噴喙瀾,',
        '你有啥物不滿，做你講出來,',
        '伊彼个人串講都無好話,',
        '免佮伊講，佮伊講，講袂伸捙,',
        '聽講彼兩間公司欲合併,',
        '你拄才講啥逐家聽現現，袂使閣反悔,',
        '聽講彼間厝有歹物,',
        '慢且是，等伊來才閣講,',
        '早就共你講，無彼號尻川就毋通食彼號瀉藥仔,',
        '出在人講,',
        '伊的人生，坎坎坷坷，講起來話頭長啦！,',
        '伊講話真文,',
        '伊真𠢕搬笑詼齣，毋過伊平常時罕得講耍笑,',
        '佮你這个番仔講話真忝,',
        '我有話欲共你講，真拄好，你來矣,',
        '頭先都講好勢矣，尾來煞來反僥,',
        '伊講白賊，予\ue701老爸拍手蹄仔,',
        '閒閒咧開講,',
        '伊佮下跤手人講話嘛真好聲說,',
        '你按呢講，袂輸講是我做毋著,',
        '這件代誌講起來就心火著,',
        '伊四界烏白講我，我欲告伊,',
        '伊講話臭奶呆，我聽攏無,',
        '敢講你對我一點仔感情都無？,',
        '伊按呢講，無歹意,',
        '我咧講話有一無兩,',
        '暫且共伊安搭一下，賰的後擺才閣講,',
        '我做的代誌逐家看現現，毋驚人講閒仔話,',
        '細漢的時，阮阿公就教我背冊，閣教我真濟古早人講的道理,',
        '人攏講伊食好做輕可，實在真好命,',
        '伊講的話攏有準算,',
        '話是在人講的,',
        '伊有喃講欲搬出去,',
        '欲合股做生理我先踏話頭，聽了會當接受，才繼續來講,',
        '你毋通講人的是非,',
        '俗語話講：「一好佮一䆀，無兩好相排。」,',
        '這幾工仔伊攏毋講話，是有啥物蹊蹺無？,',
        '以早遮是田，這馬做停車場，聽講以後欲起厝,',
        '毋管你按怎講，橫直我毋信,',
        '往過伊攏會來揣阮老爸開講,',
        '伊若欲上台演講攏會懍場,',
        '這張字紙頂懸有寫講你愛還偌濟錢,',
        '我才無欲聽你咧烏白講,',
        '佮伊講無兩句，就共伊揍落去,',
        '伊彼个人誠甕肚，有好空的攏毋共人講,',
        '頂輩若講伊幾句仔，伊就應喙應舌,',
        '你想講激外外就無代誌矣是無？,',
        '我共你講真的，你煞當做我咧共你滾笑,',
        '你若是加講話，連鞭就會出代誌,',
        '伊是咱遮出名的大嚨喉空，遠遠就會當聽著伊講話的聲矣,',
        '你講話若火雞母咧,',
        '伊講按呢傷過離譜,',
        '講話較細聲咧,',
        '伊講話誠幼聲,',
        '人講會做翁仔某是頂世人相欠債,',
        '伊那食物件那講話，無細膩煞著咳嗾,',
        '頭家今仔日心花開，講年底獎金欲發三個月,',
        '伊猶未講完，毋通僭話,',
        '人講斷掌查埔做相公，斷掌查某守空房,',
        '無佮意你就講，何乜苦共伊刁難？,',
        '講著種花伊閣有二步七仔！,',
        '這層代誌咱頂過已經講過矣！,',
        '你講的話我有聽著矣,',
        '伊講話聲調真低,',
        '你講話毋好遐大聲,',
        '逐家當頭對面共話講予清楚！,',
        '大兄將伊滿腹的苦情講予我聽,',
        '彼是某人講予我聽的,',
        '伊今仔日講話飛飛,',
        '伊講欲去臺北拍拚，結果煞有去無回頭,',
        '彼个查某囡仔袂講得媠,',
        '伊定定共阿生戲弄，講伊是一个大箍呆,',
        '你串講攏講遐的，無效啦！,',
        '拄才我明明有聽著人咧講話,',
        '伊講規晡，我嘛是掠無頭摠,',
        '伊是毋是會同意猶真僫講,',
        '伊袂講大聲話,',
        '你閣按怎講，伊也是聽袂入耳,',
        '聽講伊佮阿英咧交往，敢有影？,',
        '伊講話的聲嗽無通好,',
        '阮阿媽雖然毋捌字，毋過伊講出喙的話攏是金言玉語,',
    ]
    inputLIST = ["地動發生到今(4/10)是第八工，砂卡礑步道猶是走揣的重點。今仔早重機具佇步道繼續挖，有揣著兩名死者，可能是姓游的爸爸和查某囝，佇這兩位死者的下跤閣挖著兩个死者，是相攬的姿勢。第三位可能是媽媽，而且佇身軀頂有揣著伊和三个囡仔的健保卡，另外佇咧暗頭仔也閣挖著一位死者，應該是上細漢的查某囝，若無意外，挖出來這五个人就是一家伙仔。",]
    #for inputSTR in inputLIST:
    inputSTR = "伊講話誠幼聲".replace("。", "")
    resultDICT = articutTaigi.parse(inputSTR, level="lv2")
    pprint(resultDICT)
    #<ENTITY_pronoun>[^<]+</ENTITY_pronoun>(<FUNC_inner>[^<]+</FUNC_inner>)?<ENTITY_noun>[^<]+</ENTITY_noun><DegreeP>[^<]+</DegreeP>