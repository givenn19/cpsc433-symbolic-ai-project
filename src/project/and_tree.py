from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Union
from project.models import LecTut, Lecture, LectureSlot, TutorialSlot, LecTutSlot, is_tut, is_lec
from project.parser import InputData

@dataclass(frozen=True, slots=True)
class ScheduledItem:
    lt: LecTut
    slot: LecTutSlot
    cap_at_assign: int

@dataclass
class DummyLecTut(LecTut):
    identifier: str = "Dummy"
    alrequired: bool = False

@dataclass(frozen=True)
class DummyScheduledItem(ScheduledItem):
    lt: LecTut = field(default_factory=DummyLecTut)
    start_time: float = 0.0
    end_time: float = 0.0
    day: str = ""
    slot: Optional[LecTutSlot] = None
    cap_at_assign: int = 0

@dataclass(frozen=True, slots=True)
class Node:
    most_recent_item: ScheduledItem = field(default_factory=DummyScheduledItem)


def _overlap(start1: float, end1: float, start2: float, end2: float) -> bool:
    return not ((end1 < start2) or (end2 < start1))

class AndTreeSearch:

    def __init__(self, input_data: InputData) -> None:
        self._input_data = input_data
        self._unassigned_lecs = self._input_data.lectures.copy()
        self._unassigned_tuts = self._input_data.tutorials.copy()

        # CHANGE THESE TO A MIN HEAP STRUCUTE FOR EVAL IN THE FUTURE?
        self._open_lecture_slots = {item.identifier: item for item in self._input_data.lec_slots}
        self._open_tut_slots = {item.identifier: item for item in self._input_data.tut_slots}

        self._successors: Dict[str, LecTut] = {}

        self._curr_schedule: Dict[str, ScheduledItem] = {}

        self._results = []

        self.num_leafs = 0 # for observability

    
    def _fail_hc(self, curr_sched: Dict[str, ScheduledItem], next_lt: LecTut, next_day: str, next_start: float, next_end: float) -> bool:
        # Handle tutorial and lecture TIME OVERLAPS
        if is_tut(next_lt) and next_lt.parent_lecture_id in curr_sched:
            sched_lecture = curr_sched[next_lt.parent_lecture_id]
            if _overlap(sched_lecture.slot.start_time, sched_lecture.slot.end_time, next_start, next_end):
                return True

        # Handle not compatible TIME OVERLAPS
        for non_c in self._input_data.not_compatible:
            id1, id2 = non_c.id1, non_c.id2
            if next_lt.identifier not in (id1, id2):
                continue
            if id1 in curr_sched:
                sched_item = curr_sched[id1]
            elif id2 in curr_sched:
                sched_item = curr_sched[id2]
            else:
                continue
            if _overlap(sched_item.slot.start_time, sched_item.slot.end_time, next_start, next_end):
                return True

        # Handle unwanted SLOT ASSIGNMENTS

        if (ident := next_lt.identifier) in self._input_data.unwanted:
            for uw in self._input_data.unwanted[ident]:
                if next_day == uw.day and next_start == uw.start_time:
                    return True
        
        return False
    

    def _get_expansions(self, leaf: Node) -> List[ScheduledItem]:
        
        # THIS IS BASICALLY THE F_TRANS PICKING WHAT TO SCHEDULE NEXT
        if (ident := leaf.most_recent_item.lt.identifier) in self._successors:
            next_lectut = self._successors[ident]
        else:
            if self._unassigned_lecs:
                next_lectut = self._unassigned_lecs.pop()
            elif self._unassigned_tuts:
                next_lectut = self._unassigned_tuts.pop()
            else:
                return []
            self._successors[leaf.most_recent_item.lt.identifier] = next_lectut
        
        if is_lec(next_lectut):
            open_slots = self._open_lecture_slots
        else:
            open_slots = self._open_tut_slots
        
        expansions = []
        for _, os in open_slots.items():
            if self._fail_hc(self._curr_schedule, next_lectut, os.day, os.start_time, os.end_time):
                continue
            expansions.append(ScheduledItem(next_lectut, os, os.current_cap))
        return expansions

    def _pre_process(self) -> Node:
        return Node (DummyScheduledItem())
    
    def _pre_dfs_slot_update(self, slot: LecTutSlot) -> None:

        """
        NEED TO HANDLE ACTIVE LEARNING
        """
        slot.increment_current_cap()

        if slot.current_cap >= slot.max_cap:
            if slot.identifier in self._open_lecture_slots:
                del self._open_lecture_slots[slot.identifier]
            else:
                del self._open_tut_slots[slot.identifier]
    
    def _post_dfs_slot_update(self, slot: LecTutSlot) -> None:
        """
        NEED TO HANDLE ACTIVE LEARNING
        """
        slot.decrement_current_cap()
        if slot.current_cap < slot.max_cap:
            if isinstance(slot, LectureSlot):
                self._open_lecture_slots[slot.identifier] = slot
            else:
                self._open_tut_slots[slot.identifier] = slot

    def _pre_dfs_updates(self, scheduled_item: ScheduledItem):
        self._pre_dfs_slot_update(scheduled_item.slot)
        self._curr_schedule[scheduled_item.lt.identifier] = scheduled_item

    def _post_dfs_updates(self, scheduled_item: ScheduledItem):
        self._post_dfs_slot_update(scheduled_item.slot)
        del self._curr_schedule[scheduled_item.lt.identifier]

    def _dfs(self, current_leaf: Node):

        expansions = self._get_expansions(current_leaf)

        if not expansions:
            self.num_leafs += 1
            if len(self._curr_schedule) == len(self._input_data.lectures) + len(self._input_data.tutorials):
                self._results.append(self._curr_schedule.copy())
            return

        for next_item in expansions:
            new_leaf = Node(most_recent_item=next_item)
            self._pre_dfs_updates(next_item)
            self._dfs(new_leaf)
            self._post_dfs_updates(next_item)


    def search(self) -> List:

        s_0 = self._pre_process()
        self._dfs(s_0)


        return self._results

