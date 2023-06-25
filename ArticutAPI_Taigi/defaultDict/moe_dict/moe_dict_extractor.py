#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut

username = ""
apikey = ""
articut = Articut(username, apikey)

def verbExtractor():
    verbLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("動詞",):
            idLIST.append(i[0])
    for e in entryLIST:
        if e[0] in idLIST and e[2] not in verbLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<ACTION_verb>{}</ACTION_verb>".format(e[2]):
                pass
            else:
                verbLIST.append(e[2])
    with open("ACTION_verb.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_ActionVerb = ", '","'.join(verbLIST)))

def modifierExtractor():
    modifierLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("副詞", "形容詞"):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in modifierLIST and e[2] not in "一二三四五六七八九十兩":
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<MODIFIER>{}</MODIFIER>".format(e[2]):
                pass
            else:
                modifierLIST.append(e[2])
    with open("MODIFIER.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_Modifier = ", '","'.join(modifierLIST)))

def idiomExtractor():
    idiomLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("熟語",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in idiomLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<IDIOM>{}</IDIOM>".format(e[2]):
                pass
            else:
                idiomLIST.append(e[2])
    with open("IDIOM.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_Idiom = ", '","'.join(idiomLIST)))

def particleExtractor():
    particleLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("擬聲詞",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in particleLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<CLAUSE_particle>{}</CLAUSE_particle>".format(e[2]):
                pass
            else:
                particleLIST.append(e[2])
    with open("CLAUSE_particle.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_ClauseParticle = ", '","'.join(particleLIST)))

def pronounExtractor():
    pronounLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("代詞",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in pronounLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<ENTITY_pronoun>{}</ENTITY_pronoun>".format(e[2]):
                pass
            else:
                pronounLIST.append(e[2])
    with open("ENTITY_pronoun.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_EntityPronoun = ", '","'.join(pronounLIST)))

def locativeExtractor():
    pronounLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("方位詞",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in pronounLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<RANGE_locality>{}</RANGE_locality>".format(e[2]):
                pass
            else:
                pronounLIST.append(e[2])
    with open("RANGE_locality.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_RangeLocality = ", '","'.join(pronounLIST)))

def conjunctionExtractor():
    conjunctionLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("連詞",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in conjunctionLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<FUNC_conjunction>{}</FUNC_conjunction>".format(e[2]):
                pass
            else:
                conjunctionLIST.append(e[2])
    with open("FUNC_conjunction.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_FuncConjunction = ", '","'.join(conjunctionLIST)))

def classifierExtractor():
    classifierLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("量詞",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in classifierLIST and e[2] not in "一二三四五六七八九十兩"::
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<ENTITY_classifier>{}</ENTITY_classifier>".format(e[2]):
                pass
            else:
                classifierLIST.append(e[2])
    with open("ENTITY_classifier.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_EntityClassifier = ", '","'.join(classifierLIST)))

def justtimeExtractor():
    justtimeLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("時間詞",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in justtimeLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0].startswith("<TIME_"):
                pass
            else:
                justtimeLIST.append(e[2])
    with open("TIME_justtime.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_TimeJusttime = ", '","'.join(justtimeLIST)))

def funcinnerExtractor():
    funcinnerLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        if len(i) == 1:
            pass
        elif i[2] in ("介詞",):
            idLIST.append(i[0])

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in funcinnerLIST:
            resultDICT = articut.parse(e[2])
            if resultDICT["result_pos"][0] == "<FUNC_inner>{}</FUNC_inner>".format(e[2]):
                pass
            else:
                funcinnerLIST.append(e[2])
    with open("FUNC_inner.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_FuncInner = ", '","'.join(funcinnerLIST)))

def locationExtractor():
    locationLIST = []
    with open("詞目.csv", encoding="utf-8") as f:
        entryLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    with open("義項.csv", encoding="utf-8") as f:
        meaningLIST = [i.replace("\n", "").split(",") for i in f.read().split("\n")]
    idLIST = []
    for i in meaningLIST:
        try:
            if len(i) == 1:
                pass
            elif "－地名－" in i[3]:
                idLIST.append(i[0])
            elif "—山線" in i[4]:
                idLIST.append(i[0])
            elif "支線—" in i[4]:
                idLIST.append        (i[0])
            elif i[-1].replace("\n", "").endswith("站名"):
                idLIST.append(i[0])
            elif i[-1].replace("\n", "").endswith("捷運"):
                idLIST.append(i[0])
            elif i[-1].replace("\n", "").endswith("鐵路"):
                idLIST.append(i[0])
            elif i[-1].replace("\n", "").endswith("線"):
                idLIST.append(i[0])
            elif i[-1].replace("\n", "").endswith("輕軌"):
                idLIST.append(i[0])
        except IndexError:
            pass

    for e in entryLIST:
        if e[0] in idLIST and e[2] not in locationLIST:
            locationLIST.append(e[2])
    with open("LOCATION.py", mode="w", encoding="utf-8") as f:
        f.write('{}["{}"]'.format("moe_Location = ", '","'.join(locationLIST)))

if __name__ == "__main__":
    #verbExtractor()
    #modifierExtractor()
    #idiomExtractor()
    #particleExtractor()
    #pronounExtractor()
    #locationExtractor()
    locativeExtractor()
    #conjunctionExtractor()
    #classifierExtractor()
    #justtimeExtractor()
    #funcinnerExtractor()
    #locationExtractor()