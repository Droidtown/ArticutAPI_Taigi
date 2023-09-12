#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re

shiftRule =[
    (re.compile(r"<MODIFIER>([^<])</MODIFIER><MODIFIER>(\1)</MODIFIER><MODIFIER>\2</MODIFIER>"), ("</MODIFIER><MODIFIER>",), ("",),),
    (re.compile("<FUNC_conjunction>莫講</FUNC_conjunction><ENTITY_noun>話</ENTITY_noun>"), ("<FUNC_conjunction>莫講</FUNC_conjunction><ENTITY_noun>話</ENTITY_noun>",), ("<FUNC_negation>莫</FUNC_negation><ACTION_verb>講話</ACTION_verb>",)),
    (re.compile("<FUNC_conjunction>莫講</FUNC_conjunction>"), ("<FUNC_conjunction>莫講</FUNC_conjunction>",), ("<FUNC_negation>莫</FUNC_negation><ACTION_verb>講</ACTION_verb>",)),
    (re.compile("<FUNC_conjunction>莫怪</FUNC_conjunction>"), ("<FUNC_conjunction>莫怪</FUNC_conjunction>",), ("<FUNC_negation>莫</FUNC_negation><ACTION_verb>怪</ACTION_verb>",)),
    (re.compile("<ENTITY_noun>歹代</ENTITY_noun><ENTITY_oov>誌</ENTITY_oov>"), ("<ENTITY_noun>歹代</ENTITY_noun><ENTITY_oov>誌</ENTITY_oov>",), ("<MODIFIER>歹</MODIFIER><ENTITY_noun>代誌</ENTITY_noun>"))
    (re.compile("<ACTION_verb>[^<]+</ACTION_verb><CLAUSE_particle>咧</CLAUSE_particle><ACTION_verb>[^<]+</ACTION_verb><CLAUSE_particle>咧</CLAUSE_particle>"), ("</ACTION_verb><CLAUSE_particle>", "</CLAUSE_particle><ACTION_verb>", "CLAUSE_particle", "ACTION_verb"), ("", "", "ACTION_quantifiedVerb", "ACTION_quantifiedVerb")),
    (re.compile("<ACTION_verb>花</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("(?<=</ENTITY_num>)<ACTION_verb>甲</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_measurement",)),
    (re.compile("<ENTITY_noun>串</ENTITY_noun>(?=<ACTION_verb>)"), ("ENTITY_noun",), ("MODIFIER",)),
    (re.compile("<FUNC_conjunction>佇咧</FUNC_conjunction>$"), ("FUNC_conjunction",), ("ACTION_verb",)),
    (re.compile("<ENTITY_pronoun>阮</ENTITY_pronoun><ENTITY_noun>囝</ENTITY_noun>"), ("pronoun", "noun"), ("possessive", "pronoun")),
    (re.compile("<ACTION_verb>做臭人</ACTION_verb>"), ("<ACTION_verb>做臭人</ACTION_verb>",), ("<ACTION_verb>做</ACTION_verb><ENTITY_noun>臭人</ENTITY_noun>",)),
    (re.compile("</MODIFIER_color><MODIFIER_color>"), ("</MODIFIER_color><MODIFIER_color>",), ("",)),
    (re.compile("<ACTION_verb>[^<]來</ACTION_verb><ACTION_verb>[^<]去</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("<ENTITY_noun>坐相</ENTITY_noun><ACTION_verb>倚</ACTION_verb>"), ("<ENTITY_noun>坐相</ENTITY_noun><ACTION_verb>倚</ACTION_verb>",), ("<ACTION_verb>坐</ACTION_verb><MODIFIER>相倚</MODIFIER>",)),
    (re.compile("<ACTION_verb>提頭</ACTION_verb><ENTITY_classifier>名</ENTITY_classifier>"), ("<ACTION_verb>提頭</ACTION_verb><ENTITY_classifier>名</ENTITY_classifier>",), ("<ACTION_verb>提</ACTION_verb><ENTITY_noun>頭名</ENTITY_noun>",)),
    (re.compile("(?<=夠</MODIFIER>)<ENTITY_classifier>分</ENTITY_classifier>"), ("ENTITY_classifier",), ("MODIFIER",)),
    (re.compile("(?<=<ENTITY_classifier>本</ENTITY_classifier>)<ENTITY_classifier>冊</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("<ENTITY_pronoun>[遮遐]</ENTITY_pronoun><MODIFIER>[大小]</MODIFIER><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_pronoun><MODIFIER>", "</MODIFIER><ENTITY_classifier>", "ENTITY_pronoun", "ENTITY_classifier"), ("", "", "DegreeP", "DegreeP")),
    (re.compile("<ENTITY_pronoun>[遮遐]</ENTITY_pronoun><MODIFIER>[大小]</MODIFIER><ENTITY_noun>空</ENTITY_noun>"), ("</ENTITY_pronoun><MODIFIER>", "</MODIFIER><ENTITY_noun>", "ENTITY_pronoun", "ENTITY_noun"), ("", "", "DegreeP", "DegreeP")),
    (re.compile("<CLAUSE_particle>咧</CLAUSE_particle>(?=<ACTION_verb>)"), ("CLAUSE_particle",), ("ASPECT",)),
    (re.compile("^<FUNC_conjunction>佮</FUNC_conjunction>"), ("FUNC_conjunction",), ("ACTION_verb",)),
    (re.compile("<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER>"), ("MODIFIER",), ("ENTITY_num",)),
    (re.compile("<ENTITY_noun>[一二三四五六七八九十百千萬億兆]+</ENTITY_noun>"), ("ENTITY_noun",), ("ENTITY_num",)),
    (re.compile("<ACTION_verb>規</ACTION_verb>((?=<ENTITY_classifier>)|(?=<ENTITY_noun>))"), ("ACTION_verb",), ("QUANTIFIER",)),
    (re.compile("<ACTION_verb>惜囝</ACTION_verb>"), ("<ACTION_verb>惜囝</ACTION_verb>",), ("<ACTION_verb>惜</ACTION_verb><ENTITY_noun>囝</ENTITY_noun>",)),
    (re.compile("</ENTITY_num><ENTITY_num>"), ("</ENTITY_num><ENTITY_num>",), ("",)),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>工</ENTITY_classifier><MODIFIER>[前後]</MODIFIER>"), ("</ENTITY_num><ENTITY_classifier>", "</ENTITY_classifier><MODIFIER>", "ENTITY_num", "MODIFIER"), ("", "", "TIME_justtime", "TIME_justtime")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER>"), ("</ENTITY_num><MODIFIER>", "MODIFIER"), ("", "ENTITY_num")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>[^<]*[坪斤分]</ENTITY_classifier>"), ("</ENTITY_num><ENTITY_classifier>", "num", "classifier",), ("", "measurement", "measurement")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ACTION_verb>度</ACTION_verb>"), ("</ENTITY_num><ACTION_verb>", "num", "ACTION_verb",), ("", "measurement", "measurement")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_noun>錢</ENTITY_noun>"), ("</ENTITY_num><ENTITY_noun>", "ENTITY_num", "ENTITY_noun"), ("", "ENTITY_measurement", "ENTITY_measurement")),
    (re.compile("(?<=</ENTITY_measurement>)<ACTION_verb>重</ACTION_verb>"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ACTION_verb>張</ACTION_verb>"), ("</ENTITY_num><ACTION_verb>", "noun", "ACTION_verb"), ("", "classifier", "ENTITY_classifier")),
    (re.compile("<ENTITY_oov>阿</ENTITY_oov><ENTITY_noun>[^<]</ENTITY_noun>"), ("</ENTITY_oov><ENTITY_noun>", "ENTITY_oov", "ENTITY_noun"), ("", "ENTITY_pronoun", "ENTITY_pronoun")),
    (re.compile("(?<=</ENTITY_num>)<ACTION_verb>排</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<ENTITY_noun>第</ENTITY_noun><ENTITY_num>[^<]+</ENTITY_num><ACTION_verb>號</ACTION_verb>"), ("</ENTITY_noun><ENTITY_num>", "</ENTITY_num><ACTION_verb>", "ENTITY_noun", "ACTION_verb"), ("", "", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("<ENTITY_noun>第</ENTITY_noun><ENTITY_num>[^<]+</ENTITY_num>((?=<MODIFIER>)|(?=<ACTION_verb>))"), ("</ENTITY_noun><ENTITY_num>", "ENTITY_noun", "ENTITY_num"), ("", "MODIFIER", "MODIFIER")),
    (re.compile("<ENTITY_noun>第</ENTITY_noun><ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_noun><ENTITY_num>", "</ENTITY_num><ENTITY_classifier>", "ENTITY_noun", "ENTITY_classifier"), ("", "", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("<ENTITY_noun>第</ENTITY_noun><ENTITY_num>[^<]+</ENTITY_num><ENTITY_noun>[^<]</ENTITY_noun>"), ("</ENTITY_noun><ENTITY_num>", "</ENTITY_num><ENTITY_noun>", "ENTITY_noun"), ("", "", "ENTITY_DetPhrase")),
    (re.compile("<ENTITY_pronoun>[彼這]</ENTITY_pronoun><ACTION_verb>[張套]</ACTION_verb>"), ("</ENTITY_pronoun><ACTION_verb>", "pronoun", "ACTION_verb"), ("", "DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>點鐘</ENTITY_classifier>"), ("</ENTITY_num><ENTITY_classifier>", "ENTITY_num", "ENTITY_classifier"), ("", "TIME_justtime" , "TIME_justtime")),
    (re.compile("<ENTITY_noun>好囝</ENTITY_noun><ENTITY_noun>孫</ENTITY_noun>"), ("<ENTITY_noun>好囝</ENTITY_noun>", "孫"), ("<MODIFIER>好</MODIFIER>", "囝孫",)),
    (re.compile("<ENTITY_noun>好囝</ENTITY_noun>"), ("<ENTITY_noun>好囝</ENTITY_noun>",), ("<MODIFIER>好</MODIFIER><ENTITY_noun>囝<ENTITY_noun>",)),
    (re.compile("(?<=</FUNC_inner>)<ACTION_verb>款</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("(?<=<MODIFIER>真</MODIFIER>)<ACTION_verb>[大小]</ACTION_verb><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ACTION_verb><ENTITY_classifier>", "ACTION_verb", "ENTITY_classifier"), ("", "MODIFIER", "MODIFIER")),
    (re.compile("(?<=<MODIFIER>真</MODIFIER>)<ACTION_verb>重</ACTION_verb>"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("(?<=<MODIFIER>真</MODIFIER>)<ENTITY_noun>長</ENTITY_noun>"), ("ENTITY_noun",), ("MODIFIER",)),
    (re.compile("(?<=好</MODIFIER>)<ENTITY_noun>生張</ENTITY_noun>"), ("ENTITY_noun",), ("ACTION_verb",)),
    (re.compile("<MODIFIER>勉強</MODIFIER>(?!=<ENTITY)"), ("MODIFIER",), ("ACTION_verb",)),
    (re.compile("<ACTION_verb>食暗</ACTION_verb><ACTION_verb>頓</ACTION_verb>"), ("<ACTION_verb>食暗</ACTION_verb><ACTION_verb>頓</ACTION_verb>",), ("<ACTION_verb>食</ACTION_verb><ENTITY_noun>暗頓</ENTITY_noun>",)),
    (re.compile("<ENTITY_noun>食物</ENTITY_noun><ENTITY_classifier>件</ENTITY_classifier>"), ("<ENTITY_noun>食物</ENTITY_noun><ENTITY_classifier>件</ENTITY_classifier>",), ("<ACTION_verb>食</ACTION_verb><ENTITY_noun>物件</ENTITY_noun>",)),
    (re.compile("<IDIOM>是按怎</IDIOM>"), ("<IDIOM>是按怎</IDIOM>",), ("<AUX>是</AUX><CLAUSE_Q>按怎</CLAUSE_Q>",)),
    (re.compile("<AUX>是</AUX><FUNC_negation>無</FUNC_negation>$"), ("</AUX><FUNC_negation>", "AUX", "FUNC_negation"), ("", "CLAUSE_Q", "CLAUSE_Q")),
    (re.compile("(?<=[桌床棚]</ENTITY_noun>)<ACTION_verb>頂</ACTION_verb>"), ("ACTION_verb",), ("RANGE_locality",)),
    (re.compile("(?<=[桌床棚仔]</ENTITY_noun>)<ENTITY_classifier>跤</ENTITY_classifier>"), ("ENTITY_classifier",), ("RANGE_locality",)),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>年</ENTITY_classifier><ACTION_verb>甲</ACTION_verb><ENTITY_classifier>班</ENTITY_classifier>"), ("classifier", "ACTION_verb"), ("noun", "noun")),
    (re.compile("<ACTION_verb>車</ACTION_verb>(?=<ACTION_verb>駛</ACTION_verb>)"), ("ACTION_verb",), ("ENTITY_noun",)),
    # <NN => N>
    (re.compile("<ACTION_verb>傷</ACTION_verb><ENTITY_classifier>過</ENTITY_classifier>((?=<ACTION_verb>)|(?=<MODIFIER>))"), ("</ACTION_verb><ENTITY_classifier>", "ACTION_verb", "ENTITY_classifier"), ("", "FUNC_degreeHead", "FUNC_degreeHead")),
    (re.compile("(?<=[想欲]</ACTION_verb>)<ENTITY_classifier>過</ENTITY_classifier>"), ("ENTITY_classifier",), ("ACTION_verb",)),
    (re.compile("(?<=[活子]</ENTITY_noun>)<ENTITY_classifier>過</ENTITY_classifier>"), ("ENTITY_classifier",), ("ACTION_verb",)),
    (re.compile("<ENTITY_noun>[^<]+</ENTITY_noun><ENTITY_oov>仔</ENTITY_oov>"), ("</ENTITY_noun><ENTITY_oov>", "oov"), ("", "noun")),
    (re.compile("<ENTITY_classifier>[^<]+</ENTITY_classifier><ENTITY_oov>仔</ENTITY_oov>"), ("</ENTITY_classifier><ENTITY_oov>", "classifier"), ("", "noun")),
    (re.compile("<ENTITY_oov>阿[^<]</ENTITY_oov><ENTITY_noun>[^<]仔</ENTITY_noun>"), ("</ENTITY_oov><ENTITY_noun>", "ENTITY_oov"), ("", "ENTITY_noun")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_noun>月</ENTITY_noun>(<ENTITY_noun>底</ENTITY_noun>)?"), ("</ENTITY_noun><ENTITY_noun>", "</ENTITY_num><ENTITY_noun>", "ENTITY_num", "ENTITY_noun"), ("", "", "TIME_justtime", "TIME_justtime")),
    (re.compile("<ENTITY_classifier>月</ENTITY_classifier><ENTITY_noun>底</ENTITY_noun>"), ("</ENTITY_classifier><ENTITY_noun>", ), ("", )),
    (re.compile("<ENTITY_noun>[^<]{1,3}</ENTITY_noun><ENTITY_noun>族</ENTITY_noun>"), ("</ENTITY_noun><ENTITY_noun>",), ("",)),
    (re.compile("<ENTITY_classifier>[^<]</ENTITY_classifier><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_classifier><ENTITY_classifier>",), ("",)),
    (re.compile("<ENTITY_classifier>[^<]{2}</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("<ACTION_verb>育𤆬</ACTION_verb><ENTITY_noun>囡仔</ENTITY_noun>"), ("<ACTION_verb>育𤆬</ACTION_verb><ENTITY_noun>囡仔</ENTITY_noun>",), ("<ACTION_verb>育</ACTION_verb><ENTITY_noun>𤆬囡仔</ENTITY_noun>",)),
    (re.compile("(?<!</FUNC_determiner>)(?<!</QUANTIFIER>)<ENTITY_classifier>[^<]</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("<MODIFIER>無半步</MODIFIER>"), ("<MODIFIER>無半步</MODIFIER>",), ("<FUNC_negation>無</FUNC_negation><ENTITY_noun>半步</ENTITY_noun>",)),
    (re.compile("<ACTION_verb>好</ACTION_verb><ENTITY_noun>[^<]</ENTITY_noun>"), ("</ACTION_verb><ENTITY_noun>", "ACTION_verb", "ENTITY_noun"), ("", "MODIFIER", "MODIFIER")),
    (re.compile("<ENTITY_pronoun>[彼這逐]</ENTITY_pronoun><ENTITY_noun>[片爿條支枝隻幅本尾口盆台囷組塊匹坩間粒味雙个蕊件個坵甌副項層部帖軀碗盤包箱籃齣句胎陣門橛目子]</ENTITY_noun>"), ("</ENTITY_pronoun><ENTITY_noun>", "ENTITY_pronoun", "ENTITY_noun"), ("", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("<ENTITY_pronoun>[彼這逐]</ENTITY_pronoun><ACTION_verb>[種排盤領把囷封帕幫束營注節緟重行袋縛款頓]</ACTION_verb>"), ("</ENTITY_pronoun><ACTION_verb>", "ENTITY_pronoun", "ACTION_verb"), ("", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("<ENTITY_pronoun>[彼這逐]</ENTITY_pronoun><ACTION_verb>出</ACTION_verb>(?=<ENTITY_noun>菜)"), ("</ENTITY_pronoun><ACTION_verb>", "ENTITY_pronoun", "ACTION_verb"), ("", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("<ACTION_verb>領</ACTION_verb><ENTITY_oov>仔</ENTITY_oov>"), ("</ACTION_verb><ENTITY_oov>", "ACTION_verb", "ENTITY_oov"), ("", "ENTITY_classifier", "ENTITY_classifier")),
    (re.compile("<ACTION_verb>規</ACTION_verb><ENTITY_noun>[^<]頂</ENTITY_noun>"), ("</ACTION_verb><ENTITY_noun>", "ACTION_verb", "ENTITY_noun"), ("", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("(?<=仔)</ENTITY_noun><ENTITY_noun>(?=子)"), ("</ENTITY_noun><ENTITY_noun>",), ("",)),
    (re.compile("(?<=</ENTITY_DetPhrase>)<ACTION_verb>車</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    # </NN => N>
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_oov>仔</ENTITY_oov><ENTITY_num>[^<]+</ENTITY_num>"), ("</ENTITY_num><ENTITY_oov>", "</ENTITY_oov><ENTITY_num>"), ("", "")),
    (re.compile("<ACTION_verb>甲</ACTION_verb>(?=<ENTITY_noun>乙)"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("((?<=<ACTION_verb>[^<]{2}</ACTION_verb>)|(?<=<ACTION_verb>[^<]</ACTION_verb>)|(?<=</MODIFIER>))<ACTION_verb>甲</ACTION_verb>(?!$)"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("((?<=<ACTION_verb>[^<]{2}</ACTION_verb>)|(?<=<ACTION_verb>[^<]</ACTION_verb>)|(?<=</MODIFIER>))<ACTION_verb>甲</ACTION_verb>(?=$)"), ("ACTION_verb",), ("FUNC_degreeHead",)),
    (re.compile("<ENTITY_noun>風吹</ENTITY_noun><ACTION_verb>甲</ACTION_verb>"), ("吹</ENTITY_noun><ACTION_verb>甲</ACTION_verb>",), ("</ENTITY_noun><ACTION_verb>吹</ACTION_verb><FUNC_inner>甲</FUNC_inner>",)),
    (re.compile("<ENTITY_noun>火燒</ENTITY_noun><ACTION_verb>甲</ACTION_verb>"), ("燒</ENTITY_noun><ACTION_verb>甲</ACTION_verb>",), ("</ENTITY_noun><ACTION_verb>燒</ACTION_verb><FUNC_inner>甲</FUNC_inner>",)),
    (re.compile("<ACTION_verb>甲</ACTION_verb>(?=<FUNC_negation>)"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("<ACTION_verb>甲</ACTION_verb>(?=<ENTITY_pronoun>遐</ENTITY_pronoun><MODIFIER>)"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("(?<=甲</FUNC_inner>)<ENTITY_pronoun>遐</ENTITY_pronoun>"), ("ENTITY_pronoun",), ("FUNC_degreeHead",)),
    (re.compile("(?<=</FUNC_inner>)<FUNC_inner>若</FUNC_inner>"), ("FUNC_inner",), ("AUX",)),
    (re.compile("<MODIFIER>攏是</MODIFIER>"), ("<MODIFIER>攏是</MODIFIER>",), ("<QUANTIFIER>攏</QUANTIFIER><AUX>是</AUX>",)),
    (re.compile("<MODIFIER>曷著</MODIFIER>"), ("<MODIFIER>曷著</MODIFIER>",), ("<FUNC_inner>曷</FUNC_inner><ACTION_verb>著</ACTION_verb>",)),
    (re.compile("<ACTION_verb>袂記得</ACTION_verb>"), ("<ACTION_verb>袂記得</ACTION_verb>",), ("<FUNC_negation>袂</FUNC_negation><ACTION_verb>記得</ACTION_verb>",)),
    (re.compile("(?<=欲</ACTION_verb>)<MODIFIER>得</MODIFIER>"), ("MODIFIER",), ("ACTION_verb",)),
    (re.compile("<ENTITY_noun>[養分]的</ENTITY_noun>"), ("ENTITY_noun", "的</ACTION_verb>",), ("ACTION_verb", "</ACTION_verb><FUNC_inner>的</FUNC_inner>")),
    (re.compile("<MODIFIER>疼</MODIFIER>(?=<ENTITY)"), ("MODIFIER",), ("ACTION_verb",)),
    (re.compile("<ACTION_verb>[足傷]</ACTION_verb>((?=<ACTION_verb>)|(?=<MODIFIER>))"), ("ACTION_verb",), ("FUNC_degreeHead",)),
    (re.compile("((?<=</ACTION_verb>)|(?<=</FUNC_negation>))<ACTION_verb>傷</ACTION_verb>(?=<MODIFIER>)"), ("ACTION_verb",), ("FUNC_degreeHead",)),
    (re.compile("(?<=</ENTITY_num>)<ENTITY_noun>碗公</ENTITY_noun>"), ("ENTITY_noun",), ("ENTITY_classifier",)),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ACTION_verb>[種排領盤把囷封帕幫束營注節緟重行袋縛]</ACTION_verb>"), ("</ENTITY_num><ACTION_verb>", "ENTITY_num", "ACTION_verb"), ("", "ENTITY_classifier", "ENTITY_classifier")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_noun>[片爿條支枝隻幅本尾口盆台囷組塊匹坩間粒味雙个蕊件個坵甌副項層部帖軀碗盤包箱籃齣句胎陣門橛目子]</ENTITY_noun>"), ("</ENTITY_num><ENTITY_noun>", "ENTITY_num", "ENTITY_noun"), ("", "ENTITY_classifier", "ENTITY_classifier")),
    (re.compile("<MODIFIER>半</MODIFIER><ENTITY_noun>[片爿條支枝隻本尾幅口盆台囷組塊匹坩間粒味雙个蕊件個坵甌副項層部帖軀碗盤包箱籃齣句胎陣門橛目子]</ENTITY_noun>"), ("</MODIFIER><ENTITY_noun>", "MODIFIER", "ENTITY_noun"), ("", "ENTITY_classifier", "ENTITY_classifier")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_num><ENTITY_classifier>", "ENTITY_num"), ("", "ENTITY_classifier")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_measurement>[^<]+</ENTITY_measurement>"), ("</ENTITY_num><ENTITY_measurement>", "ENTITY_num"), ("", "ENTITY_measurement")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_noun>[逝遍]</ENTITY_noun>"), ("</ENTITY_num><ENTITY_noun>", "ENTITY_num", "ENTITY_noun"), ("", "ACTION_eventQuantifier", "ACTION_eventQuantifier")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ACTION_verb>[攬]</ACTION_verb><ACTION_verb>大</ACTION_verb>"), ("</ENTITY_num><ACTION_verb>", "</ACTION_verb><ACTION_verb>", "ENTITY_num", "ACTION_verb"), ("", "", "ENTITY_measurement", "ENTITY_measurement")),
    (re.compile("<ENTITY_num>一</ENTITY_num><ENTITY_noun>雙手</ENTITY_noun><ENTITY_noun>骨</ENTITY_noun>"), ("</ENTITY_num><ENTITY_noun>雙", "</ENTITY_noun><ENTITY_noun>", "ENTITY_num"), ("雙</ENTITY_classifier><ENTITY_noun>", "", "ENTITY_classifier")),
    (re.compile("<ENTITY_pronoun>這</ENTITY_pronoun><ENTITY_noun>[改場回擺]</ENTITY_noun>"), ("</ENTITY_pronoun><ENTITY_noun>", "ENTITY_pronoun", "ENTITY_noun"), ("", "ACTION_eventQuantifier", "ACTION_eventQuantifier")),
    (re.compile("<MODIFIER>一</MODIFIER><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</MODIFIER><ENTITY_classifier>", "MODIFIER"), ("", "ENTITY_classifier")),
    (re.compile("<ENTITY_classifier>錢</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("((?<=</ACTION_verb>)|(?<=</MODAL>))<ENTITY_classifier>落</ENTITY_classifier>"), ("ENTITY_classifier",), ("ACTION_verb",)),
    (re.compile("(<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER><ACTION_verb>箍</ACTION_verb>)"), ("</MODIFIER><ACTION_verb>", "MODIFIER", "ACTION_verb"), ("", "ENTITY_currency", "ENTITY_currency")),
    (re.compile("(<ENTITY_num>[^<]+</ENTITY_num><ACTION_verb>箍</ACTION_verb>)"), ("</ENTITY_num><ACTION_verb>", "ENTITY_num", "ACTION_verb"), ("", "ENTITY_currency", "ENTITY_currency")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_currency>[^<]+</ENTITY_currency>"), ("</ENTITY_num><ENTITY_currency>", "ENTITY_num"), ("", "ENTITY_currency")),
    (re.compile("<ENTITY_classifier>時</ENTITY_classifier>"), ("classifier",), ("noun",)),
    (re.compile("(?<=<ENTITY_classifier>一時</ENTITY_classifier>)<ACTION_verb>煞"), ("<ACTION_verb>煞",), ("<FUNC_inner>煞</FUNC_inner><ACTION_verb>",)),
    (re.compile("<MODIFIER>煞</MODIFIER>(?=<ACTION_verb>)"), ("MODIFIER",), ("FUNC_inner",)),
    (re.compile("<ACTION_verb>歹</ACTION_verb>(?=<ENTITY)"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("<ACTION_verb>較</ACTION_verb>(?=<ACTION)"), ("ACTION_verb",), ("MODIFIER",)),
    # <CLAUSE/MODIFIER => QUANTIFIER>
    (re.compile("(?<=<CLAUSE_Q>幾</CLAUSE_Q><FUNC_conjunction>若</FUNC_conjunction>)<ACTION_verb>[^<]</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<CLAUSE_Q>幾</CLAUSE_Q><FUNC_conjunction>若</FUNC_conjunction>"), ("</CLAUSE_Q><FUNC_conjunction>", "CLAUSE_Q", "FUNC_conjunction"), ("", "QUANTIFIER", "QUANTIFIER")),
    (re.compile("<MODIFIER>規[^<氣]</MODIFIER>"), ("MODIFIER",), ("QUANTIFIER",)),
    (re.compile("<ENTITY_noun>規[^<]</ENTITY_noun>"), ("<ENTITY_noun>規",), ("<QUANTIFIER>規</QUANTIFIER><ENTITY_noun>",)),
    (re.compile("<ENTITY_noun>規身[^<]</ENTITY_noun>"), ("<ENTITY_noun>規身",), ("<QUANTIFIER>規</QUANTIFIER><ENTITY_noun>身",)),
    # </CLAUSE/MODIFIER => QUANTIFIER>
    (re.compile("((?<=</ENTITY_pronoun>)|(?<=</ENTITY_person>)|(?<=</ACTION_verb>)|(?<=</QUANTIFIER>)|(?<=</MODIFIER>))<CLAUSE_particle>咧</CLAUSE_particle>(?=<ACTION_verb>)"), ("CLAUSE_particle",), ("ASPECT",)),
    (re.compile("((?<=</FUNC_inner>)|(?<=</ACTION_verb>)|(?<=</FUNC_negation>))<FUNC_conjunction>閣</FUNC_conjunction>"), ("FUNC_conjunction",), ("MODIFIER",)),
    (re.compile("<ENTITY_noun>閣</ENTITY_noun>(?=<ACTION_verb>)"), ("ENTITY_noun",), ("MODIFIER",)),
    (re.compile("<ACTION_verb>加</ACTION_verb>(?=<ACTION_verb>)"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("<ENTITY_pronoun>自</ENTITY_pronoun><ACTION_verb>對</ACTION_verb>(?=<LOCATION>)"), ("</ENTITY_pronoun><ACTION_verb>", "ENTITY_pronoun", "ACTION_verb"), ("", "FUNC_inner", "FUNC_inner")),
    (re.compile("(?<=</ACTION_verb>)<ACTION_verb>了</ACTION_verb><MODIFIER>後</MODIFIER>"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "RANGE_period", "RANGE_period")),
    (re.compile("((?<=</ENTITY_pronoun>)|(?<=</ENTITY_person>)|(?<=</QUANTIFIER>))<ACTION_verb>對</ACTION_verb>(?=<ENTITY)"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("<MODIFIER>較</MODIFIER><ENTITY_noun>[^<]</ENTITY_noun>"), ("</MODIFIER><ENTITY_noun>", "MODIFIER", "ENTITY_noun"), ("", "DegreeP", "DegreeP")),
    (re.compile("<MODIFIER>摸</MODIFIER>(?=<ACTION_verb>著</ACTION_verb>)"), ("MODIFIER",), ("ACTION_verb",)),
    (re.compile("((?<=</ACTION_verb>)|(?<=</FUNC_negation>))<ACTION_verb>[著完]</ACTION_verb>"), ("ACTION_verb",), ("ASPECT",)),
    (re.compile("<ENTITY_pronoun>遮</ENTITY_pronoun><ACTION_verb>[懸撇]</ACTION_verb>"), ("</ENTITY_pronoun><ACTION_verb>", "ENTITY_pronoun", "ACTION_verb"), ("", "DegreeP", "DegreeP")),
    (re.compile("<ACTION_verb>大氣喘</ACTION_verb>"), ("<ACTION_verb>大氣喘</ACTION_verb>",), ("<ENTITY_noun>大氣</ENTITY_noun><ACTION_verb>喘</ACTION_verb>",)),
    (re.compile("(?<=</QUANTIFIER>)<ACTION_verb>泡</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<ENTITY_pronoun>逐</ENTITY_pronoun>(?=<ENTITY_noun>[^<]{1}</ENTITY_noun>)"), ("ENTITY_pronoun",), ("QUANTIFIER",)),
    (re.compile("<ENTITY_pronoun>逐</ENTITY_pronoun>(?=<ENTITY_noun>[^<]{2}</ENTITY_noun>)"), ("ENTITY_pronoun",), ("QUANTIFIER",)),
    (re.compile("(?<=的</FUNC_inner>)<ACTION_verb>病</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    # <N => V>
    (re.compile("<ACTION_verb>[^<有予共]</ACTION_verb><ENTITY_oov>[^<囝]</ENTITY_oov>"), ("</ACTION_verb><ENTITY_oov>", "ENTITY_oov"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<有予共]</ACTION_verb><ENTITY_noun>[^<人囝]</ENTITY_noun>"), ("</ACTION_verb><ENTITY_noun>", "ENTITY_noun"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<有予共]</ACTION_verb><ENTITY_nouny>[^<]</ENTITY_nouny>"), ("</ACTION_verb><ENTITY_nouny>", "ENTITY_nouny"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<有予共]</ACTION_verb><ENTITY_nounHead>[^<]</ENTITY_nounHead>"), ("</ACTION_verb><ENTITY_nounHead>", "ENTITY_nounHead"), ("", "ACTION_verb")),
    (re.compile("(?<=<ACTION_verb>[^<]{2}</ACTION_verb>)<ENTITY_noun>戶</ENTITY_noun>"), ("noun",), ("nounHead",)),
    (re.compile("(?<=真</MODIFIER>)<ACTION_verb>光</ACTION_verb>"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("<ACTION_verb>[^<想要著欲愛學去來會講]</ACTION_verb><ACTION_verb>[^<較予光欲有]</ACTION_verb>(?!<ACTION_verb>著)(?!<FUNC_negation>袂)"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("<TIME_justtime>天光</TIME_justtime>(?=<CLAUSE_particle>)"), ("TIME_justtime",), ("ACTION_verb",)),
    (re.compile("(?<=<ACTION_lightVerb>[^<]</ACTION_lightVerb><ENTITY_pronoun>[^<]</ENTITY_pronoun>)<ENTITY_noun>針</ENTITY_noun>"), ("ENTITY_noun",), ("ACTION_verb",)),
    (re.compile("(?<=<ACTION_lightVerb>[^<]</ACTION_lightVerb><ENTITY_pronoun>[^<]{2}</ENTITY_pronoun>)<ENTITY_noun>針</ENTITY_noun>"), ("ENTITY_noun",), ("ACTION_verb",)),
    (re.compile("(?<=</ENTITY_noun>)<ENTITY_noun>收入</ENTITY_noun>"), ("ENTITY_noun",), ("ACTION_verb",)),
    # </N => V>
    (re.compile("<ACTION_verb>通</ACTION_verb><MODIFIER>好</MODIFIER>(?=<ACTION_verb>)"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "MODAL", "MODAL")),
    (re.compile("<ACTION_verb>通</ACTION_verb>(?=<ACTION_verb>)"), ("ACTION_verb",), ("MODAL",)),
    (re.compile("((?<=一[^<]</MODIFIER>)|(?<=</FUNC_inner>)|(?<=</ACTION_verb>))<ACTION_verb>會</ACTION_verb>"), ("ACTION_verb",), ("MODAL",)),
    (re.compile("<ACTION_verb>會</ACTION_verb>(?=<ACTION)"), ("ACTION_verb",), ("MODAL",)),
    (re.compile("(?<=</FUNC_negation>)<ENTITY_noun>買賣</ENTITY_noun>"), ("ENTITY_noun",), ("ACTION_verb",)),
    (re.compile("<ENTITY_noun>落</ENTITY_noun>(?=<FUNC_inner>)"), ("ENTITY_noun",), ("ACTION_verb",)),
    (re.compile("<ACTION_verb>[^<]起</ACTION_verb><ACTION_verb>來</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ACTION_verb>起來</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("<ENTITY_noun>才</ENTITY_noun>((?=<ACTION_verb>)|(?=<FUNC_negation>))"), ("ENTITY_noun",), ("FUNC_inner",)),
    (re.compile("<MODIFIER>敢</MODIFIER>((?=<FUNC_negation>)|(?=<ACTION_verb>欲))"), ("MODIFIER",), ("FUNC_inner",)),
    (re.compile("(?<=</ENTITY_classifier>)<ACTION_verb>數</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<FUNC_inner>予伊</FUNC_inner>(?!<ACTION_verb>)"), ("<FUNC_inner>予伊</FUNC_inner>",), ("<ACTION_verb>予</ACTION_verb><ENTITY_pronoun>伊</ENTITY_pronoun>",)),
    (re.compile("<FUNC_inner>予伊</FUNC_inner>(?=<ACTION_verb>)"), ("<FUNC_inner>予伊</FUNC_inner>",), ("<ACTION_lightVerb>予</ACTION_lightVerb><ENTITY_pronoun>伊</ENTITY_pronoun>",)),
    (re.compile("<ACTION_verb>予</ACTION_verb>((?=<ENTITY_pronoun>[^<]</ENTITY_pronoun><ACTION_verb>)|(?=<ENTITY_possessive>)|(?=<ENTITY_noun>[^<]人)|(?=<ENTITY_noun>人))"), ("verb",), ("lightVerb",)),
    (re.compile("(?<=</ACTION_verb>)<ACTION_verb>予</ACTION_verb>"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("<MODIFIER>([^<])</MODIFIER><MODIFIER>\\1</MODIFIER>"), ("</MODIFIER><MODIFIER>",), ("",)),
    (re.compile("<ACTION_verb>毋值</ACTION_verb>"), ("<ACTION_verb>毋值</ACTION_verb>",), ("<FUNC_negation>毋</FUNC_negation><ACTION_verb>值</ACTION_verb>",)),
    (re.compile("<ACTION_verb>毋知</ACTION_verb>"), ("<ACTION_verb>毋知</ACTION_verb>",), ("<FUNC_negation>毋</FUNC_negation><ACTION_verb>知</ACTION_verb>",)),
    (re.compile("<ACTION_verb>無愛</ACTION_verb>"), ("<ACTION_verb>無愛</ACTION_verb>",), ("<FUNC_negation>無</FUNC_negation><ACTION_verb>愛</ACTION_verb>",)),
    (re.compile("<ACTION_verb>無去</ACTION_verb>"), ("<ACTION_verb>無去</ACTION_verb>",), ("<FUNC_negation>無</FUNC_negation><ACTION_verb>去</ACTION_verb>",)),
    (re.compile("<ACTION_verb>哈哈</ACTION_verb>"), ("<ACTION_verb>哈哈</ACTION_verb>",), ("<CLAUSE_particle>哈</CLAUSE_particle><CLAUSE_particle>哈</CLAUSE_particle>")),
    (re.compile("<MODIFIER>毋敢</MODIFIER>"), ("<MODIFIER>毋敢</MODIFIER>",), ("<FUNC_negation>毋</FUNC_negation><ACTION_verb>敢</ACTION_verb>",)),
    (re.compile("((?<=<MODIFIER>[較誠真]</MODIFIER>)|(?<=</FUNC_degreeHead>)|(?<=</CLAUSE_Q>))<ACTION_verb>艱苦</ACTION_verb>"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("<MODIFIER>[較誠真]</MODIFIER><MODIFIER>[^<]{1,2}</MODIFIER>"), ("</MODIFIER><MODIFIER>", "MODIFIER"), ("", "DegreeP")),
    (re.compile("<MODIFIER>[較誠真]</MODIFIER><ENTITY_noun>趣味</ENTITY_noun>"), ("</MODIFIER><ENTITY_noun>", "MODIFIER", "ENTITY_noun"), ("", "DegreeP", "DegreeP")),
    (re.compile("<ACTION_verb>[^<]+</ACTION_verb><ACTION_verb>光</ACTION_verb><ACTION_verb>光</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("<ACTION_verb>[^<]{1,2}</ACTION_verb><ACTION_verb>看覓</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>", "ACTION_verb"), ("", "ACTION_quantifiedVerb")),
    (re.compile("<ACTION_verb>[^<]+看</ACTION_verb><ENTITY_nouny>嘜</ENTITY_nouny>"), ("</ACTION_verb><ENTITY_nouny>", "ACTION_verb", "ENTITY_noun"), ("", "ACTION_quantifiedVerb", "ACTION_quantifiedVerb")),
    (re.compile("<ACTION_verb>[^<]+</ACTION_verb><VerbP>看嘜</VerbP>"), ("</ACTION_verb><VerbP>", "ACTION_verb", "VerbP"), ("", "ACTION_quantifiedVerb", "ACTION_quantifiedVerb")),
    (re.compile("<ACTION_verb>[^<]{1,2}</ACTION_verb><MODIFIER>一下</MODIFIER>"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "ACTION_quantifiedVerb", "ACTION_quantifiedVerb")),
    (re.compile("<ENTITY_pronoun>[阮𪜶你我他伊]</ENTITY_pronoun>(?=<ENTITY_noun>[阿老][舅叔嬸婆爺爹娘父公爸母某翁]</ENTITY_noun>)"), ("ENTITY_pronoun",), ("ENTITY_possessive",)),
    (re.compile("<ENTITY_pronoun>[阮𪜶你我他伊]</ENTITY_pronoun>(?=<ENTITY_noun>[家兜厝舅叔嬸婆爺爹娘父公爸母某翁]</ENTITY_noun>)"), ("ENTITY_pronoun",), ("ENTITY_possessive",)),
    (re.compile("(?<=</ENTITY_possessive>)<ENTITY_noun>[阿老]?[舅叔嬸婆爺爹娘父公爸母某翁]</ENTITY_noun>"), ("ENTITY_noun",), ("ENTITY_pronoun",)),
    (re.compile("<ACTION_verb>攏會</ACTION_verb>"), ("<ACTION_verb>攏會</ACTION_verb>",), ("<QUANTIFIER>攏</QUANTIFIER><MODAL>會</MODAL>",)),
    (re.compile("<ACTION_verb>看會</ACTION_verb>"), ("<ACTION_verb>看會</ACTION_verb>",), ("<ACTION_verb>看</ACTION_verb><FUNC_inner>會</FUNC_inner>",)),
    (re.compile("<MODIFIER>總</MODIFIER>(?=<ACTION_verb>)"), ("MODIFIER",), ("QUANTIFIER",)),
    (re.compile("<MODIFIER>苦</MODIFIER><ACTION_verb>[^<]</ACTION_verb>"), ("</MODIFIER><ACTION_verb>","MODIFIER"), ("", "ACTION_verb")),
    (re.compile("<MODIFIER>上教</MODIFIER>"), ("MODIFIER",), ("ACTION_verb",)),
    (re.compile("<ACTION_verb>拄</ACTION_verb>(?=<ACTION_verb>)"), ("ACTION_verb",), ("TIME_justtime",)),
    (re.compile("<MODIFIER>到今</MODIFIER>"), ("<MODIFIER>到今</MODIFIER>",), ("<ACTION_verb>到</ACTION_verb><TIME_justtime>今</TIME_justtime>",)),
    (re.compile("((?<=</LOCATION>)|(?<=</ENTITY_noun>))<ENTITY_noun>內</ENTITY_noun>"), ("ENTITY_noun",), ("RANGE_locality",)),
    (re.compile("<ENTITY_classifier>才</ENTITY_classifier>"), ("ENTITY_classifier",), ("FUNC_inner",)),
    (re.compile("<MODIFIER>[平較]</MODIFIER><ACTION_verb>懸</ACTION_verb>"), ("MODIFIER", "ACTION_verb"), ("FUNC_degreeHead", "MODIFIER")),
    (re.compile("<MODIFIER>平</MODIFIER>(?=<MODIFIER>)"), ("MODIFIER",), ("FUNC_degreeHead",)),
    (re.compile("<ENTITY_noun>太</ENTITY_noun>(?=<MODIFIER>)"), ("ENTITY_noun",), ("FUNC_degreeHead",)),
    # <degreeHead + MODIFIER => DegreeP>
    (re.compile("<FUNC_degreeHead>[^<]</FUNC_degreeHead><MODIFIER>[^<]+</MODIFIER>"), ("</FUNC_degreeHead><MODIFIER>", "FUNC_degreeHead", "MODIFIER"), ("", "DegreeP", "DegreeP")),
    (re.compile("<ACTION_verb>較</ACTION_verb><MODIFIER>[^<]</MODIFIER>"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "DegreeP", "DegreeP")),
    (re.compile("<ENTITY_noun>閣</ENTITY_noun>(?=<ACTION_verb>)"), ("ENTITY_noun",), ("MODIFIER",)),
    (re.compile("<ENTITY_pronoun>遮</ENTITY_pronoun>(?=<MODIFIER>[^<])"), ("ENTITY_pronoun",), ("FUNC_degreeHead",)),
    (re.compile("<FUNC_degreeHead>足</FUNC_degreeHead><ACTION_verb>[^<]{1,3}</ACTION_verb>"), ("</FUNC_degreeHead><ACTION_verb>", "FUNC_degreeHead", "ACTION_verb"), ("", "DegreeP", "DegreeP")),
    # </degreeHead + MODIFIER => DegreeP>
    (re.compile("<IDIOM>變啥魍</IDIOM>"), ("<IDIOM>變啥魍</IDIOM>",), ("<ACTION_verb>變</ACTION_verb><CLAUSE_Q>啥魍</CLAUSE_Q>",)),
    (re.compile("<IDIOM>料想袂到</IDIOM>"), ("<IDIOM>料想袂到</IDIOM>",), ("<ACTION_verb>料想</ACTION_verb><FUNC_negation>袂</FUNC_negation><ACTION_verb>到</ACTION_verb>",)),
    (re.compile("<FUNC_conjunction>袂輸</FUNC_conjunction>"), ("<FUNC_conjunction>袂輸</FUNC_conjunction>",), ("<FUNC_negation>袂</FUNC_negation><ACTION_verb>輸</ACTION_verb>",)),
    # <V => VP>
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ASPECT>[著]</ASPECT>"), ("</ACTION_verb><ASPECT>", "ACTION_verb", "ASPECT"), ("", "VerbP", "VerbP")),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><MODIFIER>好</MODIFIER>"), ("</ACTION_verb><MODIFIER>","MODIFIER"), ("","ACTION_verb")),
    # </V => VP>
    (re.compile("(?<=</ENTITY_pronoun>)<ACTION_verb>共</ACTION_verb>"), ("verb",), ("lightVerb",)),
    (re.compile("<ACTION_verb>共</ACTION_verb>((?=<ENTITY_pronoun>)|(?=<ACTION_verb>)|(?=<ENTITY_noun>)|(?=<ENTITY_pronoun>)|(?=<ENTITY_DetPhrase>)|(?=<ENTITY_noun>人))"), ("verb",), ("lightVerb",)),
    (re.compile("<ACTION_verb>[^<]{2}</ACTION_verb><ENTITY_nounHead>[^<]+</ENTITY_nounHead>"), ("</ACTION_verb><ENTITY_nounHead>","ACTION_verb", "ENTITY_nounHead"), ("", "ENTITY_noun","ENTITY_noun")),
    (re.compile("(?<=[海山]</ENTITY_noun>)<ACTION_verb>[上下]</ACTION_verb>"), ("ACTION_verb",), ("RANGE_locality",)),
    (re.compile("<FUNC_conjunction>就按呢</FUNC_conjunction>"), ("<FUNC_conjunction>就按呢</FUNC_conjunction>",), ("<FUNC_inner>就</FUNC_inner><ENTITY_DetPhrase>按呢</ENTITY_DetPhrase>",)),
    (re.compile("(?<=</QUANTIFIER>)<ACTION_verb>塗</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("(?<=</ENTITY_noun>)<ENTITY_noun>邊</ENTITY_noun>"), ("ENTITY_noun",), ("RANGE_locality",)),
    (re.compile("(?<=[身車]</ENTITY_noun>)<ACTION_verb>上</ACTION_verb>"), ("ACTION_verb",), ("RANGE_locality",)),
    (re.compile("<ACTION_verb>較</ACTION_verb>(?=<MODIFIER>)"), ("ACTION_verb",), ("FUNC_degreeHead",)),
    (re.compile("<ENTITY_noun>頭</ENTITY_noun><ENTITY_classifier>[^<]+</ENTITY_classifier>"), ("</ENTITY_noun><ENTITY_classifier>", "ENTITY_noun", "ENTITY_classifier"), ("", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    (re.compile("<FUNC_inner>當</FUNC_inner>(?=<ENTITY_pronoun>)"), ("FUNC_inner",), ("ACTION_verb",)),
    (re.compile("<FUNC_conjunction>閣</FUNC_conjunction>$"), ("FUNC_conjunction",), ("CLAUSE_particle",)),
    (re.compile("<ENTITY_pronoun>遐</ENTITY_pronoun>(?=<MODIFIER>)"), ("ENTITY_pronoun",), ("FUNC_degreeHead",)),
    (re.compile("<FUNC_degreeHead>[^<]+</FUNC_degreeHead><MODIFIER>[^<]+</MODIFIER>"), ("</FUNC_degreeHead><MODIFIER>", "FUNC_degreeHead", "MODIFIER"), ("", "DegreeP", "DegreeP")),
    (re.compile("<MODIFIER>若無</MODIFIER>"), ("<MODIFIER>若無</MODIFIER>",), ("<FUNC_inter>若</FUNC_inter><FUNC_negation>無</FUNC_negation>",)),
    (re.compile("<ACTION_verb>通</ACTION_verb><FUNC_inner>用</FUNC_inner>"), ("ACTION_verb", "FUNC_inner"), ("MODAL", "ACTION_verb") ),
    (re.compile("</ACTION_verb><ACTION_verb>(?=落去</ACTION_verb>)"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("(?<=</ENTITY_pronoun>)<MODIFIER>亂</MODIFIER>$"), ("MODIFIER",), ("ACTION_verb",)),
    (re.compile("(?<=</ENTITY_classifier>)<ACTION_verb>[結花薰]</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<ENTITY_noun>牽豬哥</ENTITY_noun>"), ("<ENTITY_noun>牽豬哥</ENTITY_noun>",), ("<ACTION_verb>牽</ACTION_verb><ENTITY_noun>豬哥</ENTITY_noun>",)),
    (re.compile("(?<=<FUNC_inner>的</FUNC_inner>)<ACTION_verb>艱苦</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("(?<=<FUNC_inner>的</FUNC_inner>)<ACTION_verb>[^<]+</ACTION_verb>$"), ("ACTION_verb",), ("ENTITY_noun",))
]