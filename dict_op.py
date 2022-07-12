#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

if __name__ == "__main__":
    with open("moedict-data-twblg/uni/詞目總檔.csv", encoding="utf-8") as f:
        masterCSV = [c.replace("\n", "").split(",") for c in f.readlines()]

    with open("moedict-data-twblg/uni/釋義.csv", encoding="utf-8") as f:
        csv = [c.replace("\n", "").split(",") for c in f.readlines()]

    targetLIST = [((1,), "FUNC_inner"),
                  ((2,), "ENTITY_pronoun"),
                  ((3,), "ENTITY_noun"),
                  ((4,), "RANGE_locality"),
                  ((5,8,13), "MODIFIER"),
                  ((14,), "CLAUSE_Q"),
                  ((10,), "FUNC_conjunction"),
                  ]
    for t in targetLIST:
        indexLIST = []
        for c in csv[1:]:
            if int(c[3]) in t[0]:
                indexLIST.append(int(c[1]))
        resultLIST = []
        for m in masterCSV[1:]:
            if int(m[0]) in indexLIST:
                resultLIST.append(m[2])
        resultLIST = list(set(resultLIST))
        resultLIST.sort()
        with open("moe_dict/{}.json".format(t[1]), mode="w", encoding="utf-8") as j:
            json.dump(resultLIST, j, ensure_ascii=False)


    appendixLIST = [((11,), "TIME_season"),
                    ((13, 14, 15, 16, 17, 18, 19, 20, 21), "LOCATION"),
                    ((25,), "IDIOM"),
                    ]
    attributeLIST = []
    for a in appendixLIST:
        resultLIST = []
        for m in masterCSV[1:]:
            if int(m[1]) in a[0]:
                resultLIST.append(m[2])
        resultLIST = list(set(resultLIST))
        resultLIST.sort()
        with open("moe_dict/{}.json".format(a[1]), mode="w", encoding="utf-8") as j:
            json.dump(resultLIST, j, ensure_ascii=False)