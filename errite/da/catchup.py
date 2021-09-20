
def ifAllNewDeviations(da_items, db_items):
    found = True
    for deviant_item in da_items:
        for database_item in db_items:
            if deviant_item["deviationid"] == database_item:
                found = False
                break;
    return found

def ifAllNewDeviationsListOnly(da_items, db_items):
    found = True
    for deviant_item in da_items:
        for database_item in db_items:
            if deviant_item == database_item:
                found = False
                break;
    return found


def idlistHasId(id:str, given_list):
    limit = len(given_list["results"])
    for item in given_list["results"]:
        deviation_id = item["deviationid"]
        if deviation_id == id:
            return True
    return False

