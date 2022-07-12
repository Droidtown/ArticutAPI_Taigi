#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
import json
import os
import re
import tempfile


class ArticutTaigi:
    def __init__(self, username="", apikey=""):
        self.articut = Articut(username=username, apikey=apikey)

        self.moeDICT = {}
        for i in os.listdir("./moe_dict"):
            self.moeDICT[i.replace(".json", "")] = json.load(open("./moe_dict/{}".format(i), encoding="utf-8"))
        self.userDefinedDICT = tempfile.NamedTemporaryFile(mode="w+")
        json.dump(self.moeDICT, self.userDefinedDICT)
        self.userDefinedDICT.flush()

    def parse(self, inputSTR):
        resultDICT = self.articut.parse(inputSTR, level="lv1", userDefinedDictFILE=self.userDefinedDICT.name)

        POScandidateLIST = []
        for tkn in resultDICT["result_segmentation"].split("/"):
            for k in self.moeDICT.keys():
                if tkn in self.moeDICT[k]:
                    POScandidateLIST.append(("<UserDefined>{}</UserDefined>".format(tkn), "<{0}>{1}</{0}>".format(k, tkn)))

        for i, s in enumerate(resultDICT["result_pos"]):
            for p in POScandidateLIST:
                resultDICT["result_pos"][i] = resultDICT["result_pos"][i].replace(p[0],p[1])

        return resultDICT



if __name__ == "__main__":
    #台語漢字 CWS/POS TEST
    inputSTR = "查埔人千萬嘸通剩一支嘴"
    articutTaigi = ArticutTaigi()
    resultDICT = articutTaigi.parse(inputSTR)
    print(resultDICT["result_pos"])
    print(resultDICT["result_segmentation"])