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
        self.cjkPAT = re.compile(u'[\u4e00-\u9fff]')
        for i in iglob("./moe_dict/*.json"):
            self.userDefinedDICT[i.split("/")[-1].replace(".json", "")] = json.load(open("{}".format(i), encoding="utf-8"))

        for i in iglob("./my_dict/*.json"):
            POS = i.split("/")[-1].replace(".json", "")
            if POS in self.userDefinedDICT.keys():
                pass
            else:
                self.userDefinedDICT[POS] = []

            for k in self.userDefinedDICT.keys():
                posLIST = json.load(open("{}".format(i), encoding="utf-8"))
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
                    self.userDefinedDICT[k].extend(tmpLIST)
                self.userDefinedDICT[k] = list(set(self.userDefinedDICT[k]))

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

    def parse(self, inputSTR, level="lv1"):
        #Todo: Add some Preprocessing here.
        resultDICT = self.articut.parse(inputSTR, level=level, userDefinedDictFILE=self.userDefinedDictFILE.name)
        POScandidateLIST = []
        for tkn in resultDICT["result_segmentation"].split("/"):
            for k in self.userDefinedDICT.keys():
                if tkn in self.userDefinedDICT[k]:
                    POScandidateLIST.append(("<UserDefined>{}</UserDefined>".format(tkn), "<{0}>{1}</{0}>".format(k, tkn)))

        for i, s in enumerate(resultDICT["result_pos"]):
            for p in POScandidateLIST:
                resultDICT["result_pos"][i] = resultDICT["result_pos"][i].replace(p[0],p[1])

        resultDICT["result_obj"] = self._pos2Obj(resultDICT["result_pos"])
        return resultDICT



if __name__ == "__main__":
    #台語漢字 CWS/POS TEST
    inputSTR = "阮真歡迎 Ta̍k-ke 做伙來做台灣語言"
    #inputSTR = "台語線頂字典主要 le-ê 用途是"

    articutTaigi = ArticutTG()
    resultDICT = articutTaigi.parse(inputSTR)
    pprint(resultDICT)