#!/usr/bin/env python3

import sys
import json
import datetime
import hashlib

""" Program to manage donations. """

def load_donor_file(donor_file="donors.json"):
    """ load donors from file into dict, donors """
    try:
        with open(donor_file,'r') as donor_data:
            try:
                donors = json.load(donor_data)
            except (json.decoder.JSONDecodeError) as e:
                # catch malformed json
                print("The donors file is corrupt!")
                print(e)
                print("Please correct or delete the file.")
                sys.exit(1)
            return donors
    except (FileNotFoundError):
            # if the file isn't found, that's ok, give them
            # an empty donor list and we'll save anything
            # they enter upon exit.
            return []
    except (PermissionError):
        # if the file is there, but you can't read it, don't continue
        # because you won't be able to save the file on exit, risking
        # loss of data.  Fail early, fail often.
        print("Insufficent permission to access the donor file!")
        print("Please correct the permissions.")
        sys.exit(1)


def save_donor_file(donors,donor_file="donors.json"):
    """ save donors to json file """
    try:
        with open(donor_file,'w') as donor_data:
            donor_data.write(json.dumps(donors))
        return True
    except (PermissionError,OSError) as e:
        print("Sorry, couldn't write the donor file!")
        print(e)
        return False


def safe_input(prompt=">",mock=False,mock_in=""):
    """ Generic input routine. """
    # return null if anything goes wrong
    if not mock:
        # normal input mode
        try:
            selection=input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            # don't exit the program on ctrl-c, ctrl-d
            selection=""
        return selection
    else:
        # return what the test program told you to
        return mock_in


def print_lines(lines=2,dest=sys.stdout):
    """ Print variable number of linefeeds for clarity. """

    for i in range(lines):
        print("",file=dest)


def print_report(dest=sys.stdout):
    """ Print formatted list of all donors. """

    print_lines(2,dest)
  
    # print report header
    #      index    name   total gvn #gifts  avg gift
    print("{0:5} | {1:20} | {2:14} | {3:9} | {4:12}".format(
        "ID","Donor Name","Total Given","Num Gifts","Average Gift"),file=dest)
    print("-"*72,file=dest)

    # enumerate so we have the list index handy
    for donor_index, donor in enumerate(donors):

        num_donations=len(donor["donations"])

        total_donations = 0
        for donation in donor["donations"]:
            total_donations += donation["amount"]

        average_donation = total_donations / num_donations

        #      index      name     total gvn    #gifts    avg gift
        print("{0:05d}   {1:20}  ${2:14,.2f}   {3:9.0f}  ${4:12,.2f}".format(
            donor_index,donor["full_name"],
            total_donations,num_donations,average_donation),file=dest)


def parse_name(full_name):
        """ Convert string name into constituent parts, return dict of parts. """

        # capture suffix, if present.  we assume it will follow a comma
        try:
            suffix=full_name.split(",")[1].strip().upper()
        except:
            suffix=""

        # name with suffix removed
        informal_name=full_name.split(",")[0].strip().title()

        # we assume the last name is one word minus the suffix
        last_name=informal_name.split()[-1].strip().title()
       
        # we assume the first name(s) is everything to the left of the last name
        first_name=" ".join(informal_name.split()[0:-1]).title()

        # ensure standard capitalization in stuffix
        if suffix:
            new_full_name=", ".join([informal_name, suffix])
        else:
            new_full_name=informal_name

        return { "full_name": new_full_name, "informal_name": informal_name,
            "suffix": suffix, "last_name": last_name, "first_name": first_name }


def get_donation_amount(current_donor):
    """ Get a donation. """

    menu =  "\n"
    menu += "GIFT ENTRY (ammount)\n"
    menu += "-----------------------\n"
    menu += "\n"
    menu += "Enter the numeric amount {informal_name} has donated or\n"
    menu += "(q)uit to return to cancel the donation and\n"
    menu += "return to the previous menu.\n"
    menu += "\n"

    amount=0
    while amount==0:

        print_lines()

        print(menu.format(**current_donor))
        selection=safe_input("Donation amount or (q)uit: ")

        # let them bail if they want
        if selection.lower() in ["q", "quit"]:
            return None

        # protect against non numeric input
        try:
            amount=float(selection)
            return amount
        except ValueError:
            print_lines()
            print("The value must be numeric.  Please try again or (q)uit.")


def print_thank_you(current_donor,hint="wonderful",dest=sys.stdout):
    """ Print a thank you letter. """

    letter =  "\n"
    letter += "Dearest {full_name},\n"
    letter += "\n"
    letter += "We are are grateful for the generious donation on the behalf of\n"
    letter += "the {last_name} family.\n"
    letter += "\n"
    letter += "It is through the donations of {} patrions like yourself that\n"
    letter += "allows us to continue to support the community.\n"
    letter += "\n"
    letter += "Sincerely,\n"
    letter += "\n"
    letter += "Tux Humboldt\n"
    letter += "Shark Loss Prevention Institue\n"

    print_lines(2,dest)
    print("-"*80,file=dest)

    print(letter.format(hint,**current_donor),file=dest)

    print("-"*80,file=dest)
    print_lines(2,dest)


def thank_you_entry():
    """ Enter new donation and send thank you. """

    menu =  "\n"
    menu += "DONATION ENTRY (Donor Name)\n"
    menu += "---------------------------\n"
    menu += "\n"
    menu += "Enter the full name (first last) of the donor\n"
    menu += "for whom you would like to enter a donation,\n"
    menu += "(l)ist to see a list of the existing donors, or\n"
    menu += "(q)uit to return to the previous menu.\n"
    menu += "\n"

    while True:

        print_lines()

        print(menu)
        selection=safe_input("Donor Name, (l)ist or (q)uit: ")

        # check for a quit directive
        if selection.lower() in ["q", "quit"]:
            return

        # check for a list directive
        if selection.lower() in ["l", "list"]:
            print_report()
            continue

        # protect against no entry
        if not selection:
            continue

        # parse the string into name components
        current_donor=parse_name(selection)

        if current_donor["first_name"] == "" or current_donor["last_name"] == "":
            print("You must enter both a first and last name.")
            continue

        # determine if the provided name matches an existing record
        donor_id=None
        for donor_index, existing_donor in enumerate(donors):
            # assemble full name from first_name, last_name
            existing_full_name = existing_donor["first_name"]+" "+existing_donor["last_name"]
            # if we get a match, store the index of the donor record
            if existing_full_name.lower().strip() == current_donor["full_name"].lower().strip():
                current_donor=existing_donor
                #print("CUR:", current_donor)
                donor_id=donor_index

        # prompt for new donation, cancel if None returned
        new_donation=get_donation_amount(current_donor)
        if new_donation is None:
            print_lines()
            print("Donation cancelled!")
            return

        # donor_id will be None if it didn't match an existing entry

        today = datetime.datetime.utcnow().date().isoformat() + "Z"
        # datetime.datetime.strptime(<iso date>,'%Y-%m-%dZ')

        # add donation to an existing donor
        if donor_id is not None:
            donors[donor_id]["donations"].append({ "amount": new_donation, "date": today })
            hint="returning"
        else:
            now = datetime.datetime.utcnow().isoformat() + "Z"
            # datetime.datetime.strptime(<iso time>,'%Y-%m-%dT%H:%M:%S.%fZ')

            id_source = current_donor["full_name"] + now
            user_id = hashlib.md5( id_source.encode() ).hexdigest()
            donors.append( { 
                # "last_name": ", ".join(filter(None,[current_donor["last_name"], current_donor["suffix"]])),
                # "first_name": current_donor["first_name"],
                "created": now,
                "user_id": user_id,
                "donations": [ { "amount": new_donation, "date": today } ],
                **current_donor } )
            # set the donor_id to the new donor
            donor_id=len(donors)-1
            hint="new"

        # thank the donor for the new donation
        print_thank_you(current_donor,hint)


def thank_all_donors():
    """ loop through donors, open file, print a thank you letter. """
    for index in range(len(donors)):
        donor=donors[index]
        file_name="_".join(filter( None, [ "thank_you", donor["last_name"], donor["suffix"], donor["first_name"] ])).lower()
        file_name=file_name.replace(" ", "_")
        dest = open(file_name, "w")
        print_thank_you(donor,"wonderful",dest)
        dest.close()


def main():
    """ Main menu / input loop. """
    
    menu =  "\n"
    menu += "DONATION WIZARD MAIN MENU\n"
    menu += "-------------------------\n"
    menu += "\n"
    menu += "Select from the following:\n"
    menu += "\n"
    menu += "(L)ist Donors\n"
    menu += "(E)nter/(A)dd Donation\n"
    menu += "(P)rint Donor Letters\n"
    menu += "(Q)uit\n"
    menu += "\n"

    selection=None
    while selection not in ["0", "quit", "q"]:

        print_lines()

        print(menu)
        selection=safe_input("(l)ist, (e)nter, (q)uit: ").lower()

        if selection in ["l", "list"]:
            print_report()

        if selection in ["p", "print"]:
            thank_all_donors()

        # accept either send or enter
        if selection in ["s", "send", "e", "enter", "a", "add"]:
            thank_you_entry()

        if selection in ["d", "debug"]:
            print_lines()
            print("Donors:", donors)

        if selection in ["q", "quit"]:
            saved = save_donor_file(donors)
            if saved:
                print("{} donor records saved.".format(len(donors)))
            else:
                print("Please resolve the issues with the donor file before exiting.")
                # if you are testing, don't get stuck in the loop
                if mock:
                    mock_in="exit"
                shall_abort = safe_input("Enter 'exit' to quit anyways and abandon changes:",mock)
                if not 'exit' in shall_abort:
                    # if they don't want to exit, clear the selection so we don't exit
                    selection = None

    print_lines()
    print("Thank you for using Donation Wizard!")
    print_lines()


# call the main input loop
if __name__ == "__main__":
    donors = load_donor_file()
    main()


