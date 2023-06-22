#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re

shiftRule =[
    (re.compile("(?<=<ACTION_verb>[^<]</ACTION_verb>)<ACTION_verb>甲</ACTION_verb>"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("(?<=</ACTION_verb>)<ACTION_verb>傷</ACTION_verb>(?=<MODIFIER>)"), ("ACTION_verb",), ("FUNC_degreeHead",)),
    (re.compile("<ENTITY_num>[^<]+</ENTITY_num><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</ENTITY_num><ENTITY_classifier>", "ENTITY_num"), ("", "ENTITY_classifier")),
    (re.compile("<MODIFIER>一</MODIFIER><ENTITY_classifier>[^<]</ENTITY_classifier>"), ("</MODIFIER><ENTITY_classifier>", "MODIFIER"), ("", "ENTITY_classifier")),
    (re.compile("<ENTITY_classifier>錢</ENTITY_classifier>"), ("ENTITY_classifier",), ("ENTITY_noun",)),
    (re.compile("<ENTITY_noun>[^<]+</ENTITY_noun><ENTITY_oov>仔</ENTITY_oov>"), ("</ENTITY_noun><ENTITY_oov>", "oov"), ("", "noun")),
    (re.compile("(<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER>){2,}"), ("</MODIFIER><MODIFIER>",), ("",)),
    (re.compile("(<MODIFIER>[一二三四五六七八九十百千萬億兆]+</MODIFIER><ACTION_verb>箍</ACTION_verb>)"), ("</MODIFIER><ACTION_verb>", "MODIFIER", "ACTION_verb"), ("", "ENTITY_currency", "ENTITY_currency")),
    (re.compile("<ENTITY_num>三</ENTITY_num><ENTITY_currency>萬一千箍</ENTITY_currency>"), ("</ENTITY_num><ENTITY_currency>", "ENTITY_num"), ("", "ENTITY_currency")),
    (re.compile("<ENTITY_classifier>時</ENTITY_classifier>"), ("classifier",), ("noun",)),
    (re.compile("(?<=<ENTITY_classifier>一時</ENTITY_classifier>)<ACTION_verb>煞"), ("<ACTION_verb>煞",), ("<FUNC_inner>煞</FUNC_inner><ACTION_verb>",)),
    # <CLAUSE => QUANTIFIER>
    (re.compile("(?<=<CLAUSE_Q>幾</CLAUSE_Q><FUNC_conjunction>若</FUNC_conjunction>)<ACTION_verb>[^<]</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<CLAUSE_Q>幾</CLAUSE_Q><FUNC_conjunction>若</FUNC_conjunction>"), ("</CLAUSE_Q><FUNC_conjunction>", "CLAUSE_Q", "FUNC_conjunction"), ("", "QUANTIFIER", "QUANTIFIER")),
    # </CLAUSE => QUANTIFIER>
    (re.compile("((?<=</ENTITY_pronoun>)|(?<=</ENTITY_person>)|(?<=</ACTION_verb>))<CLAUSE_particle>咧</CLAUSE_particle>(?=<ACTION_verb>)"), ("CLAUSE_particle",), ("ASPECT",)),
    (re.compile("<ACTION_verb>加</ACTION_verb>(?=<ACTION_verb>)"), ("ACTION_verb",), ("MODIFIER",)),
    (re.compile("<ENTITY_pronoun>自</ENTITY_pronoun><ACTION_verb>對</ACTION_verb>(?=<LOCATION>)"), ("</ENTITY_pronoun><ACTION_verb>", "ENTITY_pronoun", "ACTION_verb"), ("", "FUNC_inner", "FUNC_inner")),
    (re.compile("(?<=</ACTION_verb>)<ACTION_verb>了</ACTION_verb><MODIFIER>後</MODIFIER>"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "RANGE_period", "RANGE_period")),
    (re.compile("((?<=</ENTITY_pronoun>)|(?<=</ENTITY_person>))<ACTION_verb>對</ACTION_verb>(?=<ENTITY)"), ("ACTION_verb",), ("FUNC_inner",)),
    (re.compile("<MODIFIER>較</MODIFIER><ENTITY_noun>[^<]</ENTITY_noun>"), ("</MODIFIER><ENTITY_noun>", "MODIFIER", "ENTITY_noun"), ("", "DegreeP", "DegreeP")),
    # <N => V>
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_oov>[^<]</ENTITY_oov>"), ("</ACTION_verb><ENTITY_oov>", "ENTITY_oov"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_noun>[^<]</ENTITY_noun>"), ("</ACTION_verb><ENTITY_noun>", "ENTITY_noun"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_nouny>[^<]</ENTITY_nouny>"), ("</ACTION_verb><ENTITY_nouny>", "ENTITY_nouny"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<]</ACTION_verb><ENTITY_nounHead>[^<]</ENTITY_nounHead>"), ("</ACTION_verb><ENTITY_nounHead>", "ENTITY_nounHead"), ("", "ACTION_verb")),
    (re.compile("<ACTION_verb>[^<想要欲愛]</ACTION_verb><ACTION_verb>[^<]</ACTION_verb>"), ("</ACTION_verb><ACTION_verb>",), ("",)),
    # </N => V>
    (re.compile("(?<=</ENTITY_classifier>)<ACTION_verb>數</ACTION_verb>"), ("ACTION_verb",), ("ENTITY_noun",)),
    (re.compile("<FUNC_inner>予伊</FUNC_inner>"), ("<FUNC_inner>予伊</FUNC_inner>",), ("<ACTION_verb>予</ACTION_verb><ENTITY_pronoun>伊</ENTITY_pronoun>",)),
    (re.compile("<MODIFIER>([^<])</MODIFIER><MODIFIER>\\1</MODIFIER>"), ("</MODIFIER><MODIFIER>",), ("",)),
    (re.compile("<MODIFIER>毋敢</MODIFIER>"), ("<MODIFIER>毋敢</MODIFIER>",), ("<FUNC_negation>毋</FUNC_negation><ACTION_verb>敢</ACTION_verb>",)),
    (re.compile("<MODIFIER>較</MODIFIER><MODIFIER>[^<]{1,2}</MODIFIER>"), ("</MODIFIER><MODIFIER>", "MODIFIER"), ("", "DegreeP")),
    (re.compile("<ACTION_verb>[^<]{1,2}</ACTION_verb><MODIFIER>一下</MODIFIER>"), ("</ACTION_verb><MODIFIER>", "ACTION_verb", "MODIFIER"), ("", "ACTION_quantifiedVerb", "ACTION_quantifiedVerb")),
    (re.compile("<ENTITY_pronoun>[阮𪜶你我他伊]</ENTITY_pronoun>(?=<ENTITY_noun>阿[舅叔嬸婆爺爹娘父公爸母]</ENTITY_noun>)"), ("ENTITY_pronoun",), ("ENTITY_possessive",)),
    (re.compile("<ENTITY_pronoun>[阮𪜶你我他伊]</ENTITY_pronoun>(?=<ENTITY_noun>[家兜厝舅叔嬸婆爺爹娘父公爸母]</ENTITY_noun>)"), ("ENTITY_pronoun",), ("ENTITY_possessive",)),
    (re.compile("<ACTION_verb>攏會</ACTION_verb>"), ("<ACTION_verb>攏會</ACTION_verb>",), ("<QUANTIFIER>攏</QUANTIFIER><MODAL>會</MODAL>",))
]