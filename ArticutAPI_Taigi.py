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
        for i in iglob("./moe_dict/*.json"):
            self.userDefinedDICT[i.split("/")[-1].replace(".json", "")] = json.load(open("{}".format(i), encoding="utf-8"))

        posLIST = []
        for i in iglob("./my_dict/*.json"):
            POS = i.split("/")[-1].replace(".json", "")
            if POS in self.userDefinedDICT.keys():
                pass
            else:
                self.userDefinedDICT[POS] = []
            posLIST.extend(json.load(open("{}".format(i), encoding="utf-8")))

        for k in self.userDefinedDICT.keys():
            self.userDefinedDICT[k] = list(set(self.userDefinedDICT[k])-set(posLIST))
            try:
                self.userDefinedDICT[k].extend(json.load(open("./my_dict/{}.json".format(k), encoding="utf-8")))
            except FileNotFoundError:
                pass
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
    inputSTR = "你ē-sái請逐家提供字句hō͘你做試驗。"
    articutTaigi = ArticutTG()
    resultDICT = articutTaigi.parse(inputSTR)
    pprint(resultDICT)