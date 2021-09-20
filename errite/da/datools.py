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

def localDetermineNewDeviation(source, tasks, inverse):
    source_length = 0
    tasks_length = 0
    new_deviations = 0
    if not len(source) == 0 and not len(tasks) == 0:
        if source is not None:
            source_length = len(source)
        if tasks is not None:
            tasks_length = len(tasks)
        doContinue = True
        if inverse:
            most_recent_task = 0
            index = 0
        elif not inverse:
            most_recent_task = tasks_length - 1
            index = source_length - 1

        while doContinue :
            if not source[index] == tasks[most_recent_task]:
                print(source[index] + " vs " + tasks[most_recent_task])
                print("new deviation found")
                new_deviations = new_deviations + 1
            elif source[index] == tasks[most_recent_task]:
                print("Found match")
                doContinue = False
            else:
                doContinue = False
            if inverse:
                index = index + 1
                if index == source_length:
                    doContinue = False
            if not inverse:
                index = index - 1
                if index == 0:
                    doContinue = False
    elif len(tasks) == 0 and not len(source) == 0:
        new_deviations = len(source)
    return new_deviations

def determineNewJournals(source_data, listener_ids):
    # NOTE: source_data must be the response from DeviantArt or this will not work
    doContinue = True
    new_deviations = 0
    max = len(source_data)
    index = 0
    if len(source_data) == 0:
        return 0
    elif len(listener_ids) == 0:
        return len(source_data)
    else:
        while doContinue:
            if source_data[index] == listener_ids[0]:
                doContinue = False
            elif not source_data[index] == listener_ids[0]:
                new_deviations = new_deviations + 1
                index = index + 1
            elif index == max:
                doContinue = False
            else:
                index = index + 1
                new_deviations = new_deviations + 1

        return new_deviations

def determineNewDeviations(data1, id_list):
    #NOTE: data1 must be the response from DeviantArt or this will not work
    doContinue = True
    new_deviations = 0
    index = 0
    if len(data1) == 0:
        return 0
    for response_entry in data1:
        new_deviation_found = False
        for id_entry in id_list:
            if response_entry["deviationid"] == id_entry:
                new_deviation_found = True
                break
        if new_deviation_found:
            new_deviations = new_deviations + 1
    return new_deviations