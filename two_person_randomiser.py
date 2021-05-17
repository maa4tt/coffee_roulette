import random
from itertools import zip_longest
import pandas as pd

INPUT_DATAFILE = "test1.csv"  # change this to the input datafile
OUTPUT_DATAFILE = "output.csv"  # change this to the name of desired output datafile
OLD_PAIRINGS = "old.csv"  # change this to historic pairings
SUBSTITUTE = ""  # this is what is substitute in the case of an odd number
OVERWRITE_OLD = True  # if True OLD_PAIRINGS csv will be overwritten by OUTPUT_DATAFILE


def data_reader(name):
    """This function reads the input data and returns one list of all subscribed email addresses"""
    df = pd.read_csv(name)
    email_addresses = []
    # User list comprehension to create a list of lists from Dataframe rows
    list_of_rows = [list(row) for row in df.values]
    # Print list of lists i.e. rows
    for i in list_of_rows:
        if i[3] == "Yes\\, and I'm happy for my name & email to be shared with everyone signed up to coffee roulette":
            email_addresses.append(i[2])  # this corresponds to the row containing the email address
    return email_addresses


def old_reader(name):
    df = pd.read_csv(name)
    old_dict = {}
    list_of_rows = [list(row) for row in df.values]
    for i in list_of_rows:
        old_dict[i[1]] = i[2]
    return old_dict


def check_old_pair(old_dict, new_pairing_tuple):
    """ This function returns a list of all matches that are identical to the old pairs and an empty list if none.

    """
    duplicates = []
    for i in new_pairing_tuple:
        if old_dict[i[0]] == i[1]:
            duplicates.append(i)
    return duplicates


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # Taken from itertools recipes:
    # https://docs.python.org/2/library/itertools.html#recipes
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n  # these two lines are an excellent shortcut using itertools for grouping.
    return zip_longest(fillvalue=fillvalue, *args)


def merge(list1, list2):
    """this function takes two lists and returns a list of tuples paired itemwise list1[i]:list2[i]"""
    merged_list = tuple(zip(list1, list2))
    return merged_list


def pairing_gen(email_addresses):
    """This function generates the final pairings and outputs an alphabetically sorted pandas dataframe with all
    elements in both columns """
    pairing_1 = []
    pairing_2 = []
    for first_member, second_member in grouper(email_addresses, 2, SUBSTITUTE):
        pairing_1.append(first_member)
        pairing_2.append(second_member)
    paired_tuple = (merge(pairing_1, pairing_2))
    paired_singular = paired_tuple  # a version of the tuple that is unsorted and only contains each value once (I.E.
    # not all in left hand column). (in the current code iteration this is not truly needed. However, if you were
    # going to deal with duplicates individually this is more useful than storing each twice in the list?
    paired_tuple += (merge(pairing_2, pairing_1))  # adds the reverse pairing so left column contains all members
    paired_df = pd.DataFrame.from_records(
        paired_tuple, columns=['person_1', 'person_2'])
    paired_df = paired_df.sort_values(by=['person_1'])  # sort the pairings alphabetically
    return paired_singular, paired_df


counter = 0
email_addresses = data_reader(f'{INPUT_DATAFILE}')  # load in the data
random.shuffle(email_addresses)  # shuffle the data
new_pairings = pairing_gen(email_addresses)
new_pairings_tuple = new_pairings[0]  # the pairings tuple
new_pairings_df = new_pairings[1]  # the pairings dataframe
old_dict = old_reader(OLD_PAIRINGS)  # create dictionary of old pairs
duplicates = (check_old_pair(old_dict, new_pairings_tuple))
while duplicates:
    random.shuffle(email_addresses)
    new_pairings = pairing_gen(email_addresses)
    new_pairings_tuple = new_pairings[0]  # the pairings tuple
    new_pairings_df = new_pairings[1]  # the pairings dataframe
    counter += 1
    duplicates = (check_old_pair(old_dict, new_pairings_tuple))
else:
    final_pairings = new_pairings_df  # finalise the pairings

print(final_pairings)  # print the pairings
print(f'{counter} iteration(s) to generate 0 duplicates')
final_pairings.to_csv(f'{OUTPUT_DATAFILE}')  # outputs to csv
if OVERWRITE_OLD:
    final_pairings.to_csv(f'{OLD_PAIRINGS}')  # update old pairings if 'True' above

