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

def hasDuplicate(dictionary, artist, foldername, inverse, hybrid, mature):
    max_index = dictionary["max-index"] - 1
    currentindex = 0
    if len(dictionary) == 1:
        return False
    while not currentindex == max_index:
        if dictionary[currentindex]["authorname"] == artist.upper():
            if dictionary[currentindex]["inverse"] == foldername.upper():
                if dictionary[currentindex]["inverse"] == inverse:
                    if dictionary[currentindex]["hybrid"] == hybrid:
                        if dictionary[currentindex]["mature"] == mature:
                            return True
        currentindex = currentindex + 1
    return False