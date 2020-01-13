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
def checkDeviationTask(given_data, check_artist:str, check_folder:str):
    for artist in given_data:
        #Index 0 is the first column in DeviationData table.
        if str(artist[0]).lower() == check_artist.lower():
            if str(artist[1]).lower() == check_folder.lower():
                return True
    return False



