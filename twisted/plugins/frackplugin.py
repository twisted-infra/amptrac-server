# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from twisted.application.service import ServiceMaker

Frack = ServiceMaker(
    "Amptrac",
    "amptrac.service",
    ("A parasite upon issue trackers."),
    "amptrac")
