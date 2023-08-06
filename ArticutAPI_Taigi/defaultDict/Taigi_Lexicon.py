#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import tempfile
import platform

try:
    from moe_dict.ACTION_verb import moe_ActionVerb
    from moe_dict.CLAUSE_particle import moe_ClauseParticle
    from moe_dict.CLAUSE_Q import moe_ClauseQ
    from moe_dict.ENTITY_classifier import moe_EntityClassifier
    from moe_dict.ENTITY_noun import moe_EntityNoun
    from moe_dict.ENTITY_pronoun import moe_EntityPronoun
    from moe_dict.FUNC_conjunction import moe_FuncConjunction
    from moe_dict.FUNC_inner import moe_FuncInner
    from moe_dict.FUNC_inter import moe_FuncInter
    from moe_dict.IDIOM import moe_Idiom
    from moe_dict.LOCATION import moe_Location
    from moe_dict.MODIFIER import moe_Modifier
    from moe_dict.RANGE_locality import moe_RangeLocality
    from moe_dict.TIME_justtime import moe_TimeJusttime
    from moe_dict.TIME_season import moe_TimeSeason

    from DroidtownTG_dict.ACTION_eventQuantifier import DT_ActionEventQuantifier
    from DroidtownTG_dict.ACTION_lightVerb import DT_ActionLightVerb
    from DroidtownTG_dict.ACTION_quantifiedVerb import DT_ActionQuantifiedVerb
    from DroidtownTG_dict.ACTION_verb import DT_ActionVerb
    from DroidtownTG_dict.ASPECT import DT_Aspect
    from DroidtownTG_dict.AUX import DT_Aux
    from DroidtownTG_dict.CLAUSE_particle import DT_ClauseParticle
    from DroidtownTG_dict.CLAUSE_Q import DT_ClauseQ
    from DroidtownTG_dict.ENTITY_classifier import DT_EntityClassifier
    from DroidtownTG_dict.ENTITY_DetPhrase import DT_EntityDetPhrase
    from DroidtownTG_dict.ENTITY_measurement import DT_EntityMeasurement
    from DroidtownTG_dict.ENTITY_noun import DT_EntityNoun
    from DroidtownTG_dict.ENTITY_num import DT_EntityNum
    from DroidtownTG_dict.ENTITY_person import DT_EntityPerson
    from DroidtownTG_dict.ENTITY_possessive import DT_EntityPossessive
    from DroidtownTG_dict.ENTITY_pronoun import DT_EntityPronoun
    from DroidtownTG_dict.FUNC_degreeHead import DT_FuncDegreeHead
    from DroidtownTG_dict.FUNC_inner import DT_FuncInner
    from DroidtownTG_dict.FUNC_inter import DT_FuncInter
    from DroidtownTG_dict.FUNC_negation import DT_FuncNegation
    from DroidtownTG_dict.FUNC_conjunction import DT_FuncConjunction
    from DroidtownTG_dict.IDIOM import DT_Idiom
    from DroidtownTG_dict.LOCATION import DT_Location
    from DroidtownTG_dict.TIME_justtime import DT_TimeJusttime
    from DroidtownTG_dict.MODAL import DT_Modal
    from DroidtownTG_dict.MODIFIER import DT_Modifier
    from DroidtownTG_dict.MODIFIER_color import DT_ModifierColor
    from DroidtownTG_dict.QUANTIFIER import DT_Quantifier

    from DroidtownTG_dict.toTL import DT_TL
except:
    from .moe_dict.ACTION_verb import moe_ActionVerb
    from .moe_dict.CLAUSE_particle import moe_ClauseParticle
    from .moe_dict.CLAUSE_Q import moe_ClauseQ
    from .moe_dict.ENTITY_classifier import moe_EntityClassifier
    from .moe_dict.ENTITY_noun import moe_EntityNoun
    from .moe_dict.ENTITY_pronoun import moe_EntityPronoun
    from .moe_dict.FUNC_conjunction import moe_FuncConjunction
    from .moe_dict.FUNC_inner import moe_FuncInner
    from .moe_dict.FUNC_inter import moe_FuncInter
    from .moe_dict.IDIOM import moe_Idiom
    from .moe_dict.LOCATION import moe_Location
    from .moe_dict.MODIFIER import moe_Modifier
    from .moe_dict.RANGE_locality import moe_RangeLocality
    from .moe_dict.TIME_justtime import moe_TimeJusttime
    from .moe_dict.TIME_season import moe_TimeSeason

    from .DroidtownTG_dict.ACTION_eventQuantifier import DT_ActionEventQuantifier
    from .DroidtownTG_dict.ACTION_lightVerb import DT_ActionLightVerb
    from .DroidtownTG_dict.ACTION_quantifiedVerb import DT_ActionQuantifiedVerb
    from .DroidtownTG_dict.ACTION_verb import DT_ActionVerb
    from .DroidtownTG_dict.ASPECT import DT_Aspect
    from .DroidtownTG_dict.AUX import DT_Aux
    from .DroidtownTG_dict.CLAUSE_particle import DT_ClauseParticle
    from .DroidtownTG_dict.CLAUSE_Q import DT_ClauseQ
    from .DroidtownTG_dict.ENTITY_classifier import DT_EntityClassifier
    from .DroidtownTG_dict.ENTITY_DetPhrase import DT_EntityDetPhrase
    from .DroidtownTG_dict.ENTITY_measurement import DT_EntityMeasurement
    from .DroidtownTG_dict.ENTITY_noun import DT_EntityNoun
    from .DroidtownTG_dict.ENTITY_num import DT_EntityNum
    from .DroidtownTG_dict.ENTITY_person import DT_EntityPerson
    from .DroidtownTG_dict.ENTITY_possessive import DT_EntityPossessive
    from .DroidtownTG_dict.ENTITY_pronoun import DT_EntityPronoun
    from .DroidtownTG_dict.FUNC_degreeHead import DT_FuncDegreeHead
    from .DroidtownTG_dict.FUNC_inner import DT_FuncInner
    from .DroidtownTG_dict.FUNC_inter import DT_FuncInter
    from .DroidtownTG_dict.FUNC_negation import DT_FuncNegation
    from .DroidtownTG_dict.FUNC_conjunction import DT_FuncConjunction
    from .DroidtownTG_dict.IDIOM import DT_Idiom
    from .DroidtownTG_dict.LOCATION import DT_Location
    from .DroidtownTG_dict.TIME_justtime import DT_TimeJusttime
    from .DroidtownTG_dict.MODAL import DT_Modal
    from .DroidtownTG_dict.MODIFIER import DT_Modifier
    from .DroidtownTG_dict.MODIFIER_color import DT_ModifierColor
    from .DroidtownTG_dict.QUANTIFIER import DT_Quantifier

    from .DroidtownTG_dict.toTL import DT_TL

def dictCombiner():
    '''
    Combine moe dictionary and DroidtownTG_dict
    '''
    combinedDICT = {"ACTION_verb"           : None,
                    "ACTION_lightVerb"      : None,
                    "ACTION_quantifiedVerb" : None,
                    "ACTION_eventQuantifier": None,
                    "ASPECT"                : None,
                    "AUX"                   : None,
                    "CLAUSE_particle"       : None,
                    "CLAUSE_Q"              : None,
                    "ENTITY_classifier"     : None,
                    "ENTITY_DetPhrase"      : None,
                    "ENTITY_measurement"    : None,
                    "ENTITY_noun"           : None,
                    "ENTITY_num"            : None,
                    "ENTITY_person"         : None,
                    "ENTITY_possessive"     : None,
                    "ENTITY_pronoun"        : None,
                    "FUNC_conjunction"      : None,
                    "FUNC_degreeHead"       : None,
                    "FUNC_inner"            : None,
                    "FUNC_inter"            : None,
                    "FUNC_negation"         : None,
                    "FUNC_conjunction"      : None,
                    "IDIOM"                 : None,
                    "LOCATION"              : None,
                    "MODAL"                 : None,
                    "MODIFIER"              : None,
                    "MODIFIER_color"        : None,
                    "QUANTIFIER"            : None,
                    "RANGE_locality"        : None,
                    "RANGE_period"          : None,
                    "TIME_justtime"         : None,
                    "TIME_season"           : None
                    }

    moeDICT = {"ACTION_verb"      : moe_ActionVerb,
               "CLAUSE_particle"  : moe_ClauseParticle,
               "CLAUSE_Q"         : moe_ClauseQ,
               "ENTITY_classifier": moe_EntityClassifier,
               "ENTITY_noun"      : moe_EntityNoun,
               "ENTITY_pronoun"   : moe_EntityPronoun,
               "FUNC_conjunction" : moe_FuncConjunction,
               "FUNC_inner"       : moe_FuncInner,
               "FUNC_inter"       : moe_FuncInter,
               "IDIOM"            : moe_Idiom,
               "LOCATION"         : moe_Location,
               "MODIFIER"         : moe_Modifier,
               "RANGE_locality"   : moe_RangeLocality,
               "TIME_justtime"    : moe_TimeJusttime,
               "TIME_season"      : moe_TimeSeason
    }

    DTDICT = {"ACTION_verb"           : DT_ActionVerb,
              "ACTION_lightVerb"      : DT_ActionLightVerb,
              "ACTION_quantifiedVerb" : DT_ActionQuantifiedVerb,
              "ACTION_eventQuantifier": DT_ActionEventQuantifier,
              "ASPECT"                : DT_Aspect,
              "AUX"                   : DT_Aux,
              "CLAUSE_particle"       : DT_ClauseParticle,
              "CLAUSE_Q"              : DT_ClauseQ,
              "ENTITY_classifier"     : DT_EntityClassifier,
              "ENTITY_DetPhrase"      : DT_EntityDetPhrase,
              "ENTITY_measurement"    : DT_EntityMeasurement,
              "ENTITY_noun"           : DT_EntityNoun,
              "ENTITY_num"            : DT_EntityNum,
              "ENTITY_person"         : DT_EntityPerson,
              "ENTITY_possessive"     : DT_EntityPossessive,
              "ENTITY_pronoun"        : DT_EntityPronoun,
              "FUNC_degreeHead"       : DT_FuncDegreeHead,
              "FUNC_inner"            : DT_FuncInner,
              "FUNC_inter"            : DT_FuncInter,
              "FUNC_negation"         : DT_FuncNegation,
              "FUNC_conjunction"      : DT_FuncConjunction,
              "IDIOM"                 : DT_Idiom,
              "LOCATION"              : DT_Location,
              "TIME_justtime"         : DT_TimeJusttime,
              "MODAL"                 : DT_Modal,
              "MODIFIER"              : DT_Modifier,
              "MODIFIER_color"        : DT_ModifierColor,
              "QUANTIFIER"            : DT_Quantifier,
              "RANGE_period"          : []
    }


    for POS in combinedDICT.keys():
        try:
            tmpLIST = moeDICT[POS]
            for k in DTDICT.keys():
                tmpLIST = list(set(tmpLIST)-set(DTDICT[k]))
            if POS in DTDICT.keys():
                tmpLIST.extend(DTDICT[POS])
            tmpLIST = list(set(tmpLIST))
            combinedDICT[POS] = tmpLIST
        except KeyError:
            combinedDICT[POS] = DTDICT[POS]

        #try:
            #tmpLIST = []
            #for p in posLIST:
                #if re.search(self.cjkPAT, p.strip()):
                    #tmpLIST.append(p.strip())
                #else:
                    #for w in (p.strip().lower(), p.strip().upper(), p.strip().title(), p.strip().capitalize(), p.strip()):
                        #tmpLIST.append(" {}".format(w))
                        #tmpLIST.append("{} ".format(w))
                        #tmpLIST.append(" {} ".format(w))
                        #tmpLIST.append("{}".format(w))
            #if tmpLIST != []:
                #combinedDICT[POS].extend(tmpLIST)
            #combinedDICT[POS] = list(set(combinedDICT[POS]))
        #except FileNotFoundError:
            #pass

    #if platform.system() == "Windows":
        #defaultDictFILE = tempfile.NamedTemporaryFile(mode="w+", delete=False)
    #else:
        #defaultDictFILE = tempfile.NamedTemporaryFile(mode="w+")
    #json.dump(combinedDICT, defaultDictFILE)
    #defaultDictFILE.flush()


    return combinedDICT


if __name__ == "__main__":
    combinedDICT = dictCombiner()
    print(combinedDICT["TIME_justtime"])