# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from twisted.application.service import ServiceMaker

AmpTrac = ServiceMaker(
    "Amptrac",
    "amptrac_server.service",
    ("A parasite upon issue trackers."),
    "amptrac")
