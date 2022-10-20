#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
from glob import iglob
import json
from pprint import pprint
import re
import tempfile

class ArticutTG:
    def __init__(self, username="", apikey=""):
        self.articut = Articut(username=username, apikey=apikey)
        self.posPat = re.compile("<[^<]*>([^<]*)</([^<]*)>")
        self.userDefinedDICT = {}
        self.cjkPAT = re.compile('[\u4e00-\u9fff]')
        self.moeCSV = [[t.replace("\n", "") for t in l.split(",")] for l  in open("./moe_dict/詞目總檔.csv", "r", encoding="utf-8").readlines()]
        for i in iglob("./moe_dict/*.json"):
            self.userDefinedDICT[i.split("/")[-1].replace(".json", "")] = json.load(open("{}".format(i), encoding="utf-8"))

        for i in iglob("./my_dict/*.json"):
            POS = i.split("/")[-1].replace(".json", "")
            if POS in self.userDefinedDICT.keys():
                pass
            else:
                self.userDefinedDICT[POS] = []

        for POS in self.userDefinedDICT.keys():
            try:
                posLIST = json.load(open("./my_dict/{}.json".format(POS), encoding="utf-8"))
                tmpLIST = []
                for p in posLIST:
                    if re.search(self.cjkPAT, p.strip()):
                        tmpLIST.append(p.strip())
                    else:
                        for w in (p.strip().lower(), p.strip().upper(), p.strip().title(), p.strip().capitalize(), p.strip()):
                            tmpLIST.append(" {}".format(w))
                            tmpLIST.append("{} ".format(w))
                            tmpLIST.append(" {} ".format(w))
                            tmpLIST.append("{}".format(w))
                if tmpLIST != []:
                    self.userDefinedDICT[POS].extend(tmpLIST)
                self.userDefinedDICT[POS] = list(set(self.userDefinedDICT[POS]))
            except FileNotFoundError:
                pass

        self.userDefinedDictFILE = tempfile.NamedTemporaryFile(mode="w+")
        json.dump(self.userDefinedDICT, self.userDefinedDictFILE)
        self.userDefinedDictFILE.flush()

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
                if word["text"] in [token[2] for token in self.moeCSV]:
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

    def parse(self, inputSTR, level="lv2", convert=None):
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
        #Todo: Add some Preprocessing here.
        articutResultDICT = self.articut.parse(inputSTR, level=level, userDefinedDictFILE=self.userDefinedDictFILE.name)

        POScandidateLIST = []
        for tkn in articutResultDICT["result_segmentation"].split("/"):
            for k in self.userDefinedDICT.keys():
                if tkn in self.userDefinedDICT[k]:
                    POScandidateLIST.append(("<UserDefined>{}</UserDefined>".format(tkn), "<{0}>{1}</{0}>".format(k, tkn)))

        for i, s in enumerate(articutResultDICT["result_pos"]):
            for p in POScandidateLIST:
                articutResultDICT["result_pos"][i] = articutResultDICT["result_pos"][i].replace(p[0],p[1])

        articutResultDICT["result_obj"] = self._pos2Obj(articutResultDICT["result_pos"])

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
    #台語漢字 CWS/POS TEST
    #inputSTR = "阮真歡迎 Ta̍k-ke 做伙來做台灣語言"
    #inputSTR = "台語線頂字典主要 le-ê 用途是"
    inputSTR = "台灣語言,大寒時節ê台語線頂字典"
    #inputSTR = "大寒時節"
    articutTaigi = ArticutTG()
    resultDICT = articutTaigi.parse(inputSTR, level="lv3", convert="TL")
    pprint(resultDICT)