#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re

shiftRule =[
    (re.compile("(?<=<ACTION_verb>[^<]</ACTION_verb>)<ACTION_verb>甲</ACTION_verb>"), "ACTION_verb", "FUNC_inner"),
]