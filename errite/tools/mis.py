

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