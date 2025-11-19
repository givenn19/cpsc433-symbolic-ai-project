from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, NamedTuple
import logging

from project.models import LectureSlot, TutorialSlot, Tutorial, Lecture, NotCompatible, Unwanted, Preference, Pair, PartialAssignment, LecTut

logger = logging.getLogger(__name__)

class DayTime(NamedTuple):
    day: str
    time: str

class DayTimePref(DayTime):
    pref_val: str

@dataclass
class InputData:
    name: str
    lec_slots: List[LectureSlot]
    tut_slots: List[TutorialSlot]
    tutorials: List[Tutorial]
    lectures: List[Lecture]
    not_compatible: List[NotCompatible]
    unwanted: Dict[str, List[Unwanted]]
    preferences: Dict[str, Preference]
    pair: Dict[str, str]
    part_assign: Dict[LecTut, DayTime]
    w_min_filled: str
    pen_lec_min: int
    pen_tut_min: int
    pen_not_paired: int
    pen_section: int

@dataclass
class ParsedFile:
    name: str = ""
    lec_slots: List[LectureSlot] = field(default_factory=list)
    tut_slots: List[TutorialSlot] = field(default_factory=list)
    tutorials: List[Tutorial] = field(default_factory=list)
    lectures: List[Lecture] = field(default_factory=list)
    not_compatible: List[NotCompatible] = field(default_factory=list)
    unwanted: List[Unwanted] = field(default_factory=list)
    preferences: List[Preference] = field(default_factory=list)
    pair: List[Pair] = field(default_factory=list)
    part_assign: List[PartialAssignment] = field(default_factory=list)


headers = {
    "Lecture slots:": ("lec_slots", LectureSlot),
    "Tutorial slots:": ("tut_slots", TutorialSlot),
    "Lectures:": ("lectures", Lecture),
    "Tutorials:": ("tutorials", Tutorial),
    "Not compatible:": ("not_compatible", NotCompatible),
    "Unwanted:": ("unwanted", Unwanted),
    "Preferences:": ("preferences", Preference),
    "Pair:": ("pair", Pair),
    "Partial assignments:": ("part_assign", PartialAssignment),
}

def _parse_file(path: str | Path):
    parsed = ParsedFile()

    with open(path) as f:
        current_attr = None
        current_cls = None

        for raw in f:
            line = raw.strip()
            if not line:
                continue
            line = line.replace("LAB", "TUT")
            logger.info(line)

            if line in headers:
                header_name = line

                current_attr, current_cls = headers[header_name]
                continue
            
            assert current_cls
            assert current_attr
            entry = current_cls.from_csv(line)
            getattr(parsed, current_attr).append(entry)

    return parsed
            



def get_input_data(path: str | Path, w_min_filled: str, w_pref: str, w_pair: str, w_sec_diff: str, pen_lec_min: str, pen_tut_min: str, pen_not_paired: str, pen_section: str) -> InputData:
    """Get all the inputted data and raise exceptions on invalid inputs"""
    parsed_file = _parse_file(path)

    id_map: Dict[str, LecTut] = {}
    # for lec in parsed_file.lectures:
    #     id_map[lec.identifier] = lec
    #     print(lec.identifier, lec)
    # for tut in parsed_file.tutorials:
    #     id_map[tut.identifier] = tut
    #     print(tut.identifier, tut)

    for slot in parsed_file.lec_slots:
        print(slot)

    print(" ")

    for lt in parsed_file.lectures:
        print(lt)



    pair: Dict[str, str] = {}
    for pr in parsed_file.pair:
        pair[pr.id1] = pr.id2
        pair[pr.id2] = pr.id1

    unwanted: Dict[str, List[Unwanted]] = defaultdict(list)

    for uw in parsed_file.unwanted:
        unwanted[uw.identifier].append(uw)

    preferences: Dict[str, Preference] = {}

    for pref in parsed_file.preferences:
        pref.pref_val *= int(w_pref)
        preferences[pref.identifier] = pref

    part_assign: Dict[LecTut, DayTime] = {}

    return InputData(
        name=parsed_file.name,
        lec_slots=parsed_file.lec_slots,
        tut_slots=parsed_file.tut_slots,
        tutorials=parsed_file.tutorials,
        lectures=parsed_file.lectures,
        not_compatible=parsed_file.not_compatible,
        unwanted=unwanted,
        preferences=preferences,
        pair=pair,
        part_assign=part_assign,
        w_min_filled=w_min_filled,
        pen_lec_min=int(pen_lec_min),
        pen_not_paired=int(pen_not_paired)*int(w_pair),
        pen_tut_min=int(pen_tut_min),
        pen_section=int(pen_section)*int(w_sec_diff)
    )