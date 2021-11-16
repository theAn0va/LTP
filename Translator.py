import logging
import requests
import time
from etherpad_lite import EtherpadLiteClient
"""
To-Dos:
*-Improve HTTP Request Speed (2s per set or Get currently except on work laptop)
*-Only translate after \n (and only lines that have changed)
*-Check Dict for parallel Movement -> no need to retranslate known data
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
    # List Comprehension
    args_string = "".join([f"&{key}={value}" for key, value in kwargs.items()])

    api_version = METHOD_DICT[method_to_call]

    # Manual HTTP request
    x = requests.get(
        f"http://localhost:9001/api/{api_version}/{method_to_call}?apikey={ETH_API_KEY}{args_string}"
    )
    return x.json()


def call_deepL(text):
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


# Start and stop Main Loop
active = False


def start_loop():
    global active
    if active:
        logging.info("Already Running")
    else:
        active = True
        logging.info("Translator starting")


def stop_loop():
    global active

    if not active:
        # logging.info("Translator already stopped")
        pass
    else:
        active = False
        logging.info("Translator stopping")


# Break Main Loop
def break_main_loop():
    global break_this
    if not break_this:
        break_this = True
        logging.debug("Translator terminated")


def create_pads(id_source):
    # Create Source and Sink Pad if it doesn't exist
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


# Initialise variable
break_this = True
global char_left
usagedict = call_deepL_usage()
char_left = usagedict["character_limit"] - usagedict["character_count"]

# Main Loop


def translatorloop(id_source):
    global break_this
    break_this = False
    # Check if Pads exist
    if id_source not in call_ether_methods("listAllPads")["data"]["padIDs"]:
        logging.info("Pads dont exist yet")

    # Initialise Pad IDs
    id_sink = id_source + "trans"

    # initialize Document Dictionary
    line_dic = {}

    # Main Loop
    while True:
        global active

        if active:
            logging.debug("translater running")
            # ct = Currenttext aus Source Pad auslesen, in liste schreiben und letzten eintrag (der der aktuell geschrieben wird) entfernen
            engtext = []
            sinktext = ""
            gertext = c.getText(padID=id_source)["text"].splitlines()
            del gertext[-1]

            for line in gertext:
                # check if in line dic (either adds line translation and then append or append directly)
                if line not in line_dic:
                    line_dic[line] = call_deepL(line)
                    logging.info("translated line " + str(gertext.index(line)+1))
                
                engtext.append(line_dic[line])

            for line in engtext:
                sinktext += line + "\n"

            # Sinktext in Sink Pad schreiben
            c.setText(padID=id_sink, text=sinktext)

            # Calculate Remaining Translatable Characters
            global char_left
            usagedict = call_deepL_usage()
            char_left = usagedict["character_limit"] - \
                usagedict["character_count"]

        else:
            time.sleep(1)

        if break_this:
            break


if __name__ == "__main__":
    id_source = input("Enter Source Pad Name:  ")
    create_pads(id_source)
    start_loop()
    translatorloop(id_source)
