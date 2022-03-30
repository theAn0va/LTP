import logging
import requests
from etherpad_lite import EtherpadLiteClient

"""
To-Dos:
*-Web Implementation
*-Check if Server Running
-Have other PCs join the etherpad from a Local Network
"""


# Methods only work if given the specific API Version it belongs to, so here is a dict to pair every method to its version
METHOD_DICT = {
    "createGroup": "1",
    "createGroupIfNotExistsFor": "1",
    "deleteGroup": "1",
    "listPads": "1",
    "createGroupPad": "1",
    "listAllGroups": "1.1",
    "createAuthor": "1",
    "createAuthorIfNotExistsFor": "1",
    "listPadsOfAuthor": "1",
    "getAuthorName": "1.1",
    "createSession": "1",
    "deleteSession": "1",
    "getSessionInfo": "1",
    "listSessionsOfGroup": "1",
    "listSessionsOfAuthor": "1",
    "getText": "1",
    "setText": "1",
    "appendText": "1.2.13",
    "getHTML": "1",
    "setHTML": "1",
    "getAttributePool": "1.2.8",
    "getRevisionChangeset": "1.2.8",
    "createDiffHTML": "1.2.7",
    "restoreRevision": "1.2.11",
    "getChatHistory": "1.2.7",
    "getChatHead": "1.2.7",
    "appendChatMessage": "1.2.12",
    "createPad": "1",
    "getRevisionsCount": "1",
    "getSavedRevisionsCount": "1.2.11",
    "listSavedRevisions": "1.2.11",
    "saveRevision": "1.2.11",
    "padUsersCount": "1",
    "padUsers": "1.1",
    "deletePad": "1",
    "copyPad": "1.2.8",
    "copyPadWithoutHistory": "1.2.15",
    "movePad": "1.2.8",
    "getReadOnlyID": "1",
    "getPadID": "1.2.10",
    "setPublicStatus": "1",
    "getPublicStatus": "1",
    "listAuthorsOfPad": "1",
    "getLastEdited": "1",
    "sendClientsMessage": "1.1",
    "checkToken": "1.2",
    "listAllPads": "1.2.1",
    "getStats": "1.2.14"
}

# The Ether Key is in the etherpad root directory and the DeepL Key in your account Settings
ETH_API_KEY = open("ETH_API_KEY.txt", "r").read()
DEEPL_API_KEY = open("DEEPL_API_KEY.txt", "r").read()

# Initialising the Pad Client c
c = EtherpadLiteClient(base_params={"apikey": ETH_API_KEY})


def call_ether_methods(method_to_call, **kwargs):
    """
    Method to use any "non 1.0" API-Methods
    """
    try:
        # List Comprehension
        args_string = "".join([f"&{key}={value}" for key, value in kwargs.items()])

        api_version = METHOD_DICT[method_to_call]

        # Manual HTTP request
        x = requests.get(
            f"http://localhost:9001/api/{api_version}/{method_to_call}?apikey={ETH_API_KEY}{args_string}"
        )
        y=x.json()
    except:
        print("Ether Method failed")

    return y


def call_deepL_translate(text):
    """
    Returns translated text that is given
    """

    # Manual HTTP request
    x = requests.get(
        f"https://api-free.deepl.com/v2/translate?auth_key={DEEPL_API_KEY}&text={text}&target_lang=en-GB&source_lang=de&preserve_formatting=1&tag_handling=0"
    )
    return x.json()["translations"][0]["text"]


def call_deepL_decoy(text):
    """
    Changes the given text arbitrarily to save DeepL Resources
    """
    return text.swapcase()


def call_deepL_usage():
    """
    Returns used characters and character limit
    """
    # Manual HTTP request
    x = requests.get(
        f"https://api-free.deepl.com/v2/usage?auth_key={DEEPL_API_KEY}")
    return x.json()


def create_pads(id_source):
    # Create Source and Sink Pad if it doesn't exist
    try:        
        if id_source not in call_ether_methods("listAllPads")["data"]["padIDs"]:
            c.createPad(padID=id_source)
            logging.info(id_source + " created")
        else:
            logging.info(id_source + " already exists")

        id_sink = id_source + "trans"

        if id_sink not in call_ether_methods("listAllPads")["data"]["padIDs"]:
            c.createPad(padID=id_sink)
            logging.info(id_sink + " created")
        else:
            logging.info(id_sink + " already exists")
    except:
        print("Create failed somehow")

# Initialise variable
global char_left
#usagedict = call_deepL_usage()
#char_left = usagedict["character_limit"] - usagedict["character_count"]
char_left = 500000

# Main Loop
def translateonce(id_source):
    # Check if Pads exist
    if id_source not in call_ether_methods("listAllPads")["data"]["padIDs"]:
        logging.info("Pads dont exist yet")

    # Initialise Pad IDs
    id_sink = id_source + "trans"

    # initialize Document Dictionary
    line_dic = {}
    gerold = []
    active_line = -1 
    
    deepl_call_count = 0

    # Main Function
    #try:

    logging.debug("translater running")
    engtext = []
    gertext =  c.getText(padID=id_source)["text"].splitlines()

    
    # detect active_line to not translate to save resources
    if len(gertext) == len(gerold):
        active_line = len(gertext) - 1 
        for i in range(0, len(gertext)):
            if gertext[i] != gerold[i]:
                active_line = i
                logging.debug(str(active_line+1))

    else:
        gerold=gertext
        logging.debug("line has changed")
        return

    # Translate gertext: Add text to engtext
    for i, line in enumerate(gertext):
        # check if in line dic (either adds line translation and then append or append directly)
        if line not in line_dic and i != active_line:
            line_dic[line] = call_deepL_decoy(line)
            deepl_call_count =+ 1
            logging.info("translated, count= " + str(deepl_call_count))                  
    
    for i, line in enumerate(gertext):

        # append (not translated) line (e.g. active line)
        if line not in line_dic:
            engtext.append(line)
            return

        engtext.append(line_dic[line])

    # Sinktext in Sink Pad schreiben
    c.setText(padID=id_sink, text='\n'.join(engtext))
    

    # Calculate Remaining Translatable Characters
    global char_left
    #usagedict = call_deepL_usage()
    #char_left = usagedict["character_limit"] - \   usagedict["character_count"]
    char_left = 500000

    gerold = gertext
    #except:
    #    print("F*ck")
        


if __name__ == "__main__":
    id_source = input("Enter Source Pad Name:  ")
    create_pads(id_source)
    while True:
        translateonce(id_source)
