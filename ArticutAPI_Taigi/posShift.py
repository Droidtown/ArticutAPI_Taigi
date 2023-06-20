#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re

shiftRule =[
    (re.compile("(?<=<ACTION_verb>[^<]</ACTION_verb>)<ACTION_verb>甲</ACTION_verb>"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("(?<=</ACTION_verb>)<ACTION_verb>傷</ACTION_verb>(?=<MODIFIER>)"), ("ACTION_verb",), ("FUNC_degreeHead",)),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_num><ENTITY_classifier>", "ENTITY_num"), ("", "ENTITY_classifier")),
    (re.compile("<ACTION_verb>[^<想要欲愛]</ACTION_verb><ACTION_verb>[^<]</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    (re.compile("<ENTITY_classifier>錢</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("<ENTITY_noun>[^<]+</ENTITY_noun><ENTITY_oov>仔</ENTITY_oov>"), ("</ENTITY_noun><ENTITY_oov>", "oov"), ("", "noun")),
    (re.compile("(<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER>){2,}"), ("</MODIFIER><MODIFIER>",), ("",)),
    (re.compile("(<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER><ACTION_verb>箍</ACTION_verb>)"), ("</MODIFIER><ACTION_verb>", "MODIFIER", "ACTION_verb"), ("", "ENTITY_currency", "ENTITY_currency")),
    (re.compile("<ENTITY_num>三</ENTITY_num><ENTITY_currency>萬一千箍</ENTITY_currency>"), ("</ENTITY_num><ENTITY_currency>", "ENTITY_num"), ("", "ENTITY_currency")),
]