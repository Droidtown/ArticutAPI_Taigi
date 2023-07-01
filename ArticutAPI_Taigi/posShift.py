#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re

shiftRule =[
    (re.compile("(?<=</FUNC_inner>)<ACTION_verb>款</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    # <NN => N>
    (re.compile("<ENTITY_noun>[^<]+</ENTITY_noun><ENTITY_oov>仔</ENTITY_oov>"), ("</ENTITY_noun><ENTITY_oov>", "oov"), ("", "noun")),
    (re.compile("<ENTITY_noun>[^<]{1,3}</ENTITY_noun><ENTITY_noun>族</ENTITY_noun>"), ("</ENTITY_noun><ENTITY_noun>",), ("",)),
    (re.compile("<ENTITY_classifier>[^<]</ENTITY_classifier><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_classifier><ENTITY_classifier>",), ("",)),
    (re.compile("<ENTITY_classifier>[^<]{2}</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("(?<!</FUNC_determiner>)<ENTITY_classifier>[^<]</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("<ACTION_verb>好</ACTION_verb><ENTITY_noun>[^<]</ENTITY_noun>"), ("</ACTION_verb><ENTITY_noun>", "ACTION_verb", "ENTITY_noun"), ("", "MODIFIER", "MODIFIER")),
    (re.compile("<ENTITY_pronoun>彼</ENTITY_pronoun><ENTITY_noun>[間]</ENTITY_noun>"), ("</ENTITY_pronoun><ENTITY_noun>", "ENTITY_pronoun", "ENTITY_noun"), ("", "ENTITY_DetPhrase", "ENTITY_DetPhrase")),
    # </NN => N>
    (re.compile("(?<=<ACTION_verb>[^<]</ACTION_verb>)<ACTION_verb>甲</ACTION_verb>"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("((?<=</ACTION_verb>)|(?<=</FUNC_negation>))<ACTION_verb>傷</ACTION_verb>(?=<MODIFIER>)"), ("ACTION_verb",), ("FUNC_degreeHead",)),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_noun>个</ENTITY_noun>"), ("</ENTITY_num><ENTITY_noun>", "ENTITY_num", "ENTITY_noun"), ("", "ENTITY_classifier", "ENTITY_classifier")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_num><ENTITY_classifier>", "ENTITY_num"), ("", "ENTITY_classifier")),
    (re.compile("<MODIFIER>一</MODIFIER><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</MODIFIER><ENTITY_classifier>", "MODIFIER"), ("", "ENTITY_classifier")),
    (re.compile("<ENTITY_classifier>錢</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("(?<=一[^<]</MODIFIER>)<ACTION_verb>會</ACTION_verb>"), ("ACTION_verb",), ("MODAL",)),
    (re.compile("((?<=</ACTION_verb>)|(?<=</MODAL>))<ENTITY_classifier>落</ENTITY_classifier>"), ("ENTITY_classifier",), ("ACTION_verb",)),
    (re.compile("(<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER>){2,}"), ("</MODIFIER><MODIFIER>",), ("",)),
    (re.compile("(<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER><ACTION_verb>箍</ACTION_verb>)"), ("</MODIFIER><ACTION_verb>", "MODIFIER", "ACTION_verb"), ("", "ENTITY_currency", "ENTITY_currency")),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_currency>[^<]+</ENTITY_currency>"), ("</ENTITY_num><ENTITY_currency>", "ENTITY_num"), ("", "ENTITY_currency")),
    (re.compile("<ENTITY_classifier>時</ENTITY_classifier>"), ("classifier",), ("noun",)),
    (re.compile("(?<=<ENTITY_classifier>一時</ENTITY_classifier>)<ACTION_verb>煞"), ("<ACTION_verb>煞",), ("<FUNC_inner>煞</FUNC_inner><ACTION_verb>",)),
    (re.compile("<ACTION_verb>歹</ACTION_verb>(?=<ENTITY)"), ("ACTION_verb",), ("MODIFIER",)),
    # <CLAUSE => QUANTIFIER>
    (re.compile("(?<=<CLAUSE_Q>幾</CLAUSE_Q><FUNC_conjunction>若</FUNC_conjunction>)<ACTION_verb>[^<]</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<CLAUSE_Q>幾</CLAUSE_Q><FUNC_conjunction>若</FUNC_conjunction>"), ("</CLAUSE_Q><FUNC_conjunction>", "CLAUSE_Q", "FUNC_conjunction"), ("", "QUANTIFIER", "QUANTIFIER")),
    # </CLAUSE => QUANTIFIER>
    (re.compile("((?<=</ENTITY_pronoun>)|(?<=</ENTITY_person>)|(?<=</ACTION_verb>)|(?<=</QUANTIFIER>)|(?<=</MODIFIER>))<CLAUSE_particle>咧</CLAUSE_particle>(?=<ACTION_verb>)"), ("CLAUSE_particle",), ("ASPECT",)),
    (re.compile("<ENTITY_noun>閣</ENTITY_noun>(?=<ACTION_verb>)"), ("ENTITY_noun",), ("MODIFIER",)),
    (re.compile("<ACTION_verb>加</ACTION_verb>(?=<ACTION_verb>)"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("<ENTITY_pronoun>自</ENTITY_pronoun><ACTION_verb>對</ACTION_verb>(?=<LOCATION>)"), ("</ENTITY_pronoun><ACTION_verb>", "ENTITY_pronoun", "ACTION_verb"), ("", "FUNC_inner", "FUNC_inner")),
    (re.compile("(?<=</ACTION_verb>)<ACTION_verb>了</ACTION_verb><MODIFIER>後</MODIFIER>"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "RANGE_period", "RANGE_period")),
    (re.compile("((?<=</ENTITY_pronoun>)|(?<=</ENTITY_person>))<ACTION_verb>對</ACTION_verb>(?=<ENTITY)"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("<MODIFIER>較</MODIFIER><ENTITY_noun>[^<]</ENTITY_noun>"), ("</MODIFIER><ENTITY_noun>", "MODIFIER", "ENTITY_noun"), ("", "DegreeP", "DegreeP")),
    (re.compile("<MODIFIER>摸</MODIFIER>(?=<ACTION_verb>著</ACTION_verb>)"), ("MODIFIER",), ("ACTION_verb",)),
    (re.compile("((?<=</ACTION_verb>)|(?<=</FUNC_negation>))<ACTION_verb>[著完]</ACTION_verb>"), ("ACTION_verb",), ("ASPECT",)),
    # <N => V>
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_oov>[^<]</ENTITY_oov>"), ("</ACTION_verb><ENTITY_oov>", "ENTITY_oov"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_noun>[^<]</ENTITY_noun>"), ("</ACTION_verb><ENTITY_noun>", "ENTITY_noun"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_nouny>[^<]</ENTITY_nouny>"), ("</ACTION_verb><ENTITY_nouny>", "ENTITY_nouny"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_nounHead>[^<]</ENTITY_nounHead>"), ("</ACTION_verb><ENTITY_nounHead>", "ENTITY_nounHead"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<想要欲愛]</ACTION_verb><ACTION_verb>[^<]</ACTION_verb>(?!<ACTION_verb>著)"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    # </N => V>
    (re.compile("(?<=</FUNC_negation>)<ENTITY_noun>買賣</ENTITY_noun>"), ("ENTITY_noun",), ("ACTION_verb",)),
    (re.compile("<ENTITY_noun>落</ENTITY_noun>(?=<FUNC_inner>)"), ("ENTITY_noun",), ("ACTION_verb",)),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ACTION_verb>起來</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("<ENTITY_noun>才</ENTITY_noun>(?=<ACTION_verb>)"), ("ENTITY_noun",), ("FUNC_inner",)),
    (re.compile("(?<=</ENTITY_classifier>)<ACTION_verb>數</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<FUNC_inner>予伊</FUNC_inner>"), ("<FUNC_inner>予伊</FUNC_inner>",), ("<ACTION_verb>予</ACTION_verb><ENTITY_pronoun>伊</ENTITY_pronoun>",)),
    (re.compile("<MODIFIER>([^<])</MODIFIER><MODIFIER>\\1</MODIFIER>"), ("</MODIFIER><MODIFIER>",), ("",)),
    (re.compile("<ACTION_verb>無愛</ACTION_verb>"), ("<ACTION_verb>無愛</ACTION_verb>",), ("<FUNC_negation>無</FUNC_negation><ACTION_verb>愛</ACTION_verb>",)),
    (re.compile("<MODIFIER>毋敢</MODIFIER>"), ("<MODIFIER>毋敢</MODIFIER>",), ("<FUNC_negation>毋</FUNC_negation><ACTION_verb>敢</ACTION_verb>",)),
    (re.compile("<MODIFIER>[較誠真]</MODIFIER><MODIFIER>[^<]{1,2}</MODIFIER>"), ("</MODIFIER><MODIFIER>", "MODIFIER"), ("", "DegreeP")),
    (re.compile("<ACTION_verb>[^<]{1,2}</ACTION_verb><MODIFIER>一下</MODIFIER>"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "ACTION_quantifiedVerb", "ACTION_quantifiedVerb")),
    (re.compile("<ENTITY_pronoun>[阮𪜶你我他伊]</ENTITY_pronoun>(?=<ENTITY_noun>[阿老][舅叔嬸婆爺爹娘父公爸母]</ENTITY_noun>)"), ("ENTITY_pronoun",), ("ENTITY_possessive",)),
    (re.compile("<ENTITY_pronoun>[阮𪜶你我他伊]</ENTITY_pronoun>(?=<ENTITY_noun>[家兜厝舅叔嬸婆爺爹娘父公爸母]</ENTITY_noun>)"), ("ENTITY_pronoun",), ("ENTITY_possessive",)),
    (re.compile("<ACTION_verb>攏會</ACTION_verb>"), ("<ACTION_verb>攏會</ACTION_verb>",), ("<QUANTIFIER>攏</QUANTIFIER><MODAL>會</MODAL>",)),
    (re.compile("<MODIFIER>總</MODIFIER>(?=<ACTION_verb>)"), ("MODIFIER",), ("QUANTIFIER",)),
    (re.compile("<MODIFIER>苦</MODIFIER><ACTION_verb>[^<]</ACTION_verb>"), ("</MODIFIER><ACTION_verb>","MODIFIER"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>拄</ACTION_verb>(?=<ACTION_verb>)"), ("ACTION_verb",), ("TIME_justtime",)),
    (re.compile("<MODIFIER>到今</MODIFIER>"), ("<MODIFIER>到今</MODIFIER>",), ("<ACTION_verb>到</ACTION_verb><TIME_justtime>今</TIME_justtime>",)),
    (re.compile("((?<=</LOCATION>)|(?<=</ENTITY_noun>))<ENTITY_noun>內</ENTITY_noun>"), ("ENTITY_noun",), ("RANGE_locality",)),
    (re.compile("<ENTITY_classifier>才</ENTITY_classifier>"), ("ENTITY_classifier",), ("FUNC_inner",)),
    (re.compile("<MODIFIER>平</MODIFIER><ACTION_verb>懸</ACTION_verb>"), ("MODIFIER", "ACTION_verb"), ("FUNC_degreeHead", "MODIFIER")),
    (re.compile("<MODIFIER>平</MODIFIER>(?=<MODIFIER>)"), ("MODIFIER",), ("FUNC_degreeHead",)),
    # <degreeHead + MODIFIER => DegreeP>
    (re.compile("<FUNC_degreeHead>[^<]</FUNC_degreeHead><MODIFIER>[^<]+</MODIFIER>"), ("</FUNC_degreeHead><MODIFIER>", "FUNC_degreeHead", "MODIFIER"), ("", "DegreeP", "DegreeP")),
    # <degreeHead + MODIFIER => DegreeP>

    # <V => VP>
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ASPECT>[著]</ASPECT>"), ("</ACTION_verb><ASPECT>", "ACTION_verb", "ASPECT"), ("", "VerbP", "VerbP")),
    # </V => VP>
]