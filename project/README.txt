CPSC 433 Project: Lotad (Group 18)
Nish
Kian Sieppert L01 T01 301344666


---------------------------------------------------------------------------------------------------------------------


Course Scheduling with AND-Tree Search.

This project is a course scheduling solver using an AND-Tree search algorithm.
It schedules lectures and tutorials into available time slots while satisfying hard and soft constraints.


---------------------------------------------------------------------------------------------------------------------


Project structure:

and_tree.py        – Core AND-Tree search and heuristic evaluation
csv_parsable.py    – Base class for parsing CSV-style input lines into objects
main.py            – Main; runs search, prints results, logs time & memory
models.py          – All dataclasses (slots, lectures, tutorials, prefs, etc.)
parser.py          – File parser that reads input sections and builds InputData


---------------------------------------------------------------------------------------------------------------------


Running the program:

python3 main.py [filename] w_min_filled w_pref w_pair w_sec_diff pen_lec_min pen_tut_min pen_not_paired pen_section

where,
w_min_filled : weight of minimum capactiy penalties
w_pref : weight of preference values
w_pair : weight on pairing penalties
w_sec_diff : weight on section penalties
pen_lec_min : penalty per missing lecture
pen_tut_min : penalty per missing tutorial
pen_not_paired : penalty for paired items placed seperately
pen_section : penalty for sections of lectures scheduled at the same time

E.g.
python3 main.py input.txt 1 0 1 0 10 10 10 10


---------------------------------------------------------------------------------------------------------------------


Input File Format:

The input file is divided into headered sections (e.g. "Lecture slots:")
Each section has its own format (e.g. "DAY, TIME, max_cap, min_cap, alt_max")
The following is every header and its input format, with examples.

Lecture slots:
DAY, TIME, max_cap, min_cap, alt_max		# E.g. TU, 19:00, 2, 0, 0

Tutorial slots:
DAY, TIME, max_cap, min_cap, alt_max		# E.g. MO, 18:00, 3, 0, 0

Lectures:
COURSE_CODE LEC NUMBER, evening_flag		# E.g. CPSC 413 LEC 01, false

Tutorials:
COURSE_CODE TUT NUMBER, evening_flag		# E.g. CPSC 413 TUT 01, false
						                    # TUT can also be LAB
Preferences:
DAY, TIME, identifier, value			    # E.g. MO, 10:00, CPSC 413 TUT 01, 10
						                    # positive score (reduces penalty)
Pair:
identifier1, identifier2			        # E.g. CPSC 413 LEC 01,  CPSC 913, LEC 01

Partial assignments:
identifier, DAY, TIME				        # E.g. CPSC 231 TUT 01, TU, 10:00

Not compatible:
identifier1, identifier2			        # E.g. CPSC 441 LEC 01, CPSC 355 LEC 01

Unwanted:
identifier, DAY, TIME				        # E.g. CPSC 441 LEC 1, MO, 8:00


---------------------------------------------------------------------------------------------------------------------


Output File Format:

The solver outputs assigned day/time for each lecture/tutorial.
E.g.
CPSC 413 LEC 01 : MO, 8:00
CPSC 413 TUT 01 : MO, 10:00
CPSC 913 LEC 01 : TU, 8:00
CPSC 913 TUT 01 : TU, 10:00


---------------------------------------------------------------------------------------------------------------------