from etherpad_lite import EtherpadLiteClient

def call_deepL_decoy(text):
    """
    Changes the given text arbitrarily to save DeepL Resources
    """
    return text.swapcase()

# The Ether Key is in the etherpad root directory and the DeepL Key in your account Settings
ETH_API_KEY = open("ETH_API_KEY.txt", "r").read()

# initalize parameters
# id_source = input()
id_source = "lorem"
id_sink = id_source + "trans"

i=0

# initialize Document Dictionary
doc_dic = {}
line_dic = {}


# Initialising the Pad Client c
c = EtherpadLiteClient(base_params={"apikey": ETH_API_KEY})
while True:
    # ct = Currenttext aus Source Pad auslesen, in liste schreiben und letzten eintrag (der der aktuell geschrieben wird) entfernen
    engtext = []
    sinktext=""
    gertext=c.getText(padID=id_source)["text"].splitlines()
    del gertext[-1]

    for line in gertext:
        #check if in line dic
        if line not in line_dic:
            line_dic[line] = call_deepL_decoy(line)
            print("translated line " + str(gertext.index(line)+1))
            

    for line in gertext:
        # Create Sinktext
        engtext.append(line_dic[line])
        
    for line in engtext:
        sinktext += line + "\n"


    # Sinktext in Sink Pad schreiben
    c.setText(padID=id_sink, text=sinktext)


"""
# ct = Currenttext aus Source Pad auslesen
            ct = c.getText(padID=id_source)["text"]

            # Create Document Dictionary line per line if not already created or changed
            for line_number, line in enumerate(ct.splitlines(), start=1):

                # Write new line if not in dic
                if line_number not in doc_dic:
                    doc_dic[line_number] = {"ger": line, "en": "", "ch_flag": True}
                    continue

                # Update line from German source pad if changed
                elif line != doc_dic[line_number]["ger"]:
                    doc_dic[line_number] = {"ger": line, "en": "", "ch_flag": True}

            # Remove excess lines after deleting lines in Source Pad
            for i in range(line_number + 1, len(doc_dic) + 1):
                doc_dic.pop(i)

            # Translate Dictionary line per line if not already translated or empty
            for line_number, line in enumerate(ct.splitlines(), start=1):
                if (
                    doc_dic[line_number]["ch_flag"] == True
                    and doc_dic[line_number]["ger"].replace("\t", "") != ""
                ):
                    doc_dic[line_number]["en"] = call_deepL(line)
                    logging.debug(
                        id_source + " Line " + str(line_number) + " translated"
                    )
                    doc_dic[line_number]["ch_flag"] = False

            # Create Sinktext
            ctsink = ""
            for i in range(1, len(doc_dic) + 1):
                ctsink += doc_dic[i]["en"] + "\n"

            # Sinktext in Sink Pad schreiben
            c.setText(padID=id_sink, text=ctsink)
"""