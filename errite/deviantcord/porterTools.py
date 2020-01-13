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
def determineNonInverseDeviations(jsonData, da_data):
    #Used for Non Inverted folders only
    found = False
    jsondata_len = len(jsonData) - 1
    da_data_len = len(jsonData) - 1
    information = {}
    information["action"] = None
    information["obt_list"] = None
    if len(jsonData) <= 25:
        information["action"] = "use-obt-list"
        information["obt_list"] = jsonData
        return information
    else:
        current_index = 0
        while not current_index == da_data_len:
            if jsonData[jsondata_len] == da_data[current_index]:
                found = True
                information["obt_list"] = jsonData[jsondata_len - current_index:jsondata_len]
                information["action"] = "use-obt-list"
                break
            current_index = current_index + 1
        if found:
            return information
        elif not found:
            information["action"] = "use-da"
            return information

def determineInverseIDAge(jsonData, DA_IDS, inverted):

    information = {}
    information["action"] = "none"
    information["outdated"] = False
    information["obt_list"] = None
    newest_at_top = False
    found_near_bottom = False
    found = False
    if inverted:
        if len(jsonData) <= 25:
            information["action"] = "use-json"
            information["obt_list"] = jsonData
        if jsonData[1] == DA_IDS[0]:
            newest_at_top = True
        elif jsonData[len(jsonData) - 1] == DA_IDS[len(DA_IDS) - 1]:
            found_near_bottom = True
        else:
            da_length = len(DA_IDS) -1
            json_length = len(jsonData) - 1
            current_index = 0
            while not current_index == da_length:
                if jsonData[json_length] == DA_IDS[current_index]:
                    found = True
                    found_near_bottom = True
                    information["obt_list"] = jsonData[json_length - current_index:json_length]
                    information["action"] = "use-obt-list"
                    break
                current_index = current_index + 1
            if not found:
                current_index = 0
                json_length = 1
                while not current_index == da_length:
                    if jsonData[json_length] == DA_IDS[current_index]:
                        found = True
                        newest_at_top = True
                        information["obt_list"] = jsonData[1:26]
                        information["action"] = "use-obt-list"
                        break
                    current_index = current_index + 1
            if found:
                return information
            elif not found: #This is intentional DO NOT delete
                information["action"] = "use-da"
                information["outdated"] = True
                return information
        if found_near_bottom:
            information["action"] = "use-da"
        if newest_at_top:
            information["action"] = "use-da"
        return information