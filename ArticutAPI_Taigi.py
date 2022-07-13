#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
from glob import iglob
import json
import tempfile

class ArticutTG:
    def __init__(self, username="", apikey=""):
        self.articut = Articut(username=username, apikey=apikey)

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

        return resultDICT



if __name__ == "__main__":
    #台語漢字 CWS/POS TEST
    inputSTR = "阮真歡迎ta̍k-ke做伙來做台灣語言"
    articutTaigi = ArticutTG()
    resultDICT = articutTaigi.parse(inputSTR)
    print(resultDICT["result_pos"])
    print(resultDICT["result_segmentation"])