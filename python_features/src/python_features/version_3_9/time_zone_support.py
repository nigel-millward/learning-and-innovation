# Propper Timezone support
# =========================
# Python has extensive support for working with dates and times through the datetime module in the standard library.
# However, support for working with time zones has been somewhat lacking. Until now, the recommended way of working
# with time zones has been to use third-party libraries like dateutil.

# Paul Ganssle has been the maintainer of dateutil for years. He joined the Python core developers in 2019
# and helped add a new zoneinfo standard library that makes working with time zones much more convenient.

# Using zoneinfo, you can get an object describing any time zone in the database:
from zoneinfo import ZoneInfo
ZoneInfo("America/Vancouver")
"zoneinfo.ZoneInfo(key='America/Vancouver')"


# 1. ACCESSING TIMEZONE INFO
# =============================
# zoneinfo provides access to the Internet Assigned Numbers Authority (IANA) Time Zone Database.
# The IANA updates its database several times each year, and it’s the most authoritative source for time zone information.

# Note: zoneinfo uses an IANA time zone database residing on your local computer. It’s possible—on Windows
# in particular—that you don’t have any such database or that zoneinfo won’t be able to locate it.
# If you get an error like the following, then zoneinfo hasn’t been able to locate a time zone database:

from zoneinfo import ZoneInfo
ZoneInfo("America/Vancouver")
""" 
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
ZoneInfoNotFoundError: 'No time zone found with key America/Vancouver'
"""
# A Python implementation of the IANA Time Zone Database is available on PyPI as tzdata. You can install it with pip:

# python -m pip install tzdata

# Once tzdata is installed, zoneinfo should be able to read information about all supported time zones.
# tzdata is maintained by the Python core team.
# Note that you need to keep the package updated in order to have access
# to the latest changes in the IANA Time Zone Database.


# 2. BEST PRACTICES
# =================
"""
Working with time zones can be tricky. However, with the availability of zoneinfo in the standard library,
it’s gotten a bit easier. Here are a few suggestions to keep in mind when working with dates and times:

    Civil times like the time of a meeting, a train departure, or a concert, are best stored in their native time zone. 
    You can often do this by storing a naive time stamp together with the IANA key of the time zone. 
    One example of a civil time stored as a string would be "2020-10-05T14:00:00,Europe/Oslo". 
    Having information about the time zone ensures that you can always recover the information, 
    even if the time zones themselves change.

    Time stamps represent specific moments in time and typically record an order of events. 
    Computer logs are an example of this. You don’t want your logs to be jumbled up just 
    because your time zone changes from Daylight Saving Time to standard time.
     Usually, you would store these kinds of time stamps as naive datetimes in UTC.

Because the IANA time zone database is updated all the time, you should be conscious of keeping your 
local time zone database in sync. This is particularly important if you’re running any applications
that are sensitive to time zones
"""