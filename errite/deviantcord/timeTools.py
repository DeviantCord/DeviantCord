"""

    DeviantCord 2 Discord Bot
    Copyright (C) 2020  Errite Games LLC/ ErriteEpticRikez

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
import time
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.parser import *

def prefixTimeOutSatisfied(timestamp):
    print("Invoked")
    current = datetime.now()
    obtained_date = parse(str(timestamp))
    req_date = obtained_date + timedelta(minutes=15)
    if current > req_date:
        return True
    else:
        return False


def epochSatisfied(epoch, days):
    req_time = 60*60*24*days
    now = time.time()
    if now - int(epoch) >= req_time:
        return True
    else:
        return False