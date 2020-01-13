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
from errite.da.jsonTools import findDuplicateElementArray


def enumerateAllID(data):
    length = len(data)
    if length < 10:
        use_offset = 0
    else:
        use_offset = length - 10
    gathered_id = []

    for entry in data:
        gathered_id.append(entry)
    return gathered_id
def checkHybridResources(da_data, artdata):
    data_resources = {}
    data_resources["all-hybrids"] = []
    data_resources["all-hybrid-urls"] = []
    data_resources["all-hybrid-img-urls"] = []
    data_resources["seen-hybrid-urls"] = []
    data_resources["seen-hybrid-img-urls"] = []
    data_resources["seen-hybrids"] = []
    data_resources["new-hybrids"] = 0
    for entry in da_data["results"]:
        #This blocks writings from being detected
        try:
            check_var = entry["excerpt"]
        except KeyError:
            if not findDuplicateElementArray(artdata, entry["deviationid"]):
                ++data_resources["new-hybrids"]
            else:
                data_resources["seen-hybrids"].append(entry["deviationid"])
                data_resources["seen-hybrid-urls"].append(entry["url"])
                data_resources["seen-hybrid-img-urls"].append(entry["content"]["src"])
            data_resources["all-hybrids"].append(entry["deviationid"])
            data_resources["all-hybrid-urls"].append(entry["url"])
            data_resources["all-hybrid-img-urls"].append(entry["content"]["src"])
    return data_resources

def createIDList(data):
    hybrid_ids = []
    for entry in data["results"]:
        try:
            check_var = entry["excerpt"]
        except KeyError:
            hybrid_ids.append(entry["deviationid"])
    return hybrid_ids

def createIDURLList(data):
    data_resources = {}
    data_resources["ids"] = []
    data_resources["urls"] = []
    data_resources["img-urls"] = []
    for entry in data["results"]:
        try:
            check_var = entry["excerpt"]
        except KeyError:
            data_resources["ids"].append(entry["deviationid"])
            data_resources["urls"].append(entry["url"])
            data_resources["img-urls"].append(entry["content"]["src"])
    return data_resources

def gatherGalleryFolderResources(data):
    data_resources = {}
    data_resources["deviation-ids"] = []
    data_resources["deviation-urls"] = []
    data_resources["img-urls"] = []
    for entry in data["results"]:
        try:
            check_var = entry["excerpt"]
        except KeyError:
            data_resources["deviation-ids"].append(entry["deviationid"])
            data_resources["deviation-urls"].append(entry["url"])
            data_resources["img-urls"].append(entry["content"]["src"])
    return data_resources

def convertBoolString(bool):
    if bool == True:
        return "true";
    if bool == False:
        return "false";
    else:
        return "invalid";

def convertStringBool(string):
    if string.lower() == "true":
        return True;
    if string.lower() == "false":
        return False;
    else:
        return False;

def fileExists(file):
    try:
        fh = open(file, 'r')
        return True;
        # Store configuration file values
    except FileNotFoundError:
        return False;