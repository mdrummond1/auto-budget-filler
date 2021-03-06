#module for functions
from calendar import monthrange
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from winreg import QueryValueEx, OpenKey, HKEY_CURRENT_USER
import getpass
import transaction
from json import dump, load
from os.path import exists, getsize

def get_date_parameters():
    '''get_date_parameters()-> dict
        return a dictionary of strings representing dates.
        format : mm/dd/yyyy
        start_date is one month from end date.
        end_date is todays date
        dates are the date value in the string "arguments[0].setAttribute('value', '06/21/2020')"
        for use in the calling program
    '''

    today = time.localtime()
    start_day = str(today.tm_mday)
    start_month = str(today.tm_mon - 1)
    start_yr = str(today.tm_year)

    wrapped = None
    
    if start_month == '0':
        start_month = '12'
        start_yr = str(today.tm_year - 1)
        wrapped = True

    last_day = monthrange(int(start_yr), int(start_month))[1]

    #take care of months that have different number of days
    if int(start_day) > last_day:
            start_day = str(last_day)

    end_day = start_day
    end_month = str(today.tm_mon)
    end_yr = start_yr

    if wrapped:
        end_yr = str(int(start_yr) + 1)
    
    start_date = "arguments[0].setAttribute('value', '" + start_month + '/' + start_day + '/' + start_yr + "')"
    end_date = "arguments[0].setAttribute('value', '" + end_month + '/' + end_day + '/' + end_yr + "')"

    date = {
        'start_date': start_date,
        'end_date' : end_date
    }
    return date

def get_log_info():
    '''() -> void
    collect username and password
    '''

    log = []
    log.append(input("Enter User Name: "))
    log.append(getpass.getpass("Enter password: "))
    return log

def login(user, password, driver):
    '''login(user, password, driver) -> void
        takes a username/password combo and driver
        finds login element and insert login info
    '''
    username = WebDriverWait(driver, 5).until(lambda d:d.find_element_by_id("UserName"))
    username.send_keys(user)
    passwd = driver.find_element_by_id("Password")
    passwd.send_keys(password + Keys.RETURN)    

def wait_and_click(id, driver, tm):
    '''wait_and_click(id, driver, time) -> void
        Takes an id, driver and time.
        User driver to search page for id with timeout of tm
    '''
    elem = WebDriverWait(driver, tm).until(EC.element_to_be_clickable((By.ID, id)))
    time.sleep(.5)
    elem.click()
    return elem

def input_dates(date, driver):
    '''input_dates(date, driver) -> void
    takes in a dictionary of start and end date
    and inputs them into the value of the correct elements
    end date is todays date
    '''
    start = driver.find_element_by_id("Parameters_StartDate")
    #start.text = date['start_date']
    driver.execute_script(date['start_date'], start)
    end = driver.find_element_by_id("Parameters_EndDate")
    #end.value = date['end_dated']
    driver.execute_script(date['end_date'], end)

def get_downloads():
    '''() -> string
    returns the location of the Downloads folder as a string
    '''
    with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
        return QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0] + '\\'

def clean_rows(readers, cats):
    '''(readers) -> [Transactions]
    Takes in a readers object (list of lists), and returns an array of Transactions
    Runs through 3 for loops
    '''
    #TODO: Optimize this function to not use 3 for loops
    done = False
    t = []
    for row in readers:
        for cat in cats.values():
            for sub in cat:
                if sub.lower() in row[csv_fields['desc']].lower() or sub.lower() in row[csv_fields['ext_desc']]:#clean the descriptions
                    row[csv_fields['desc']] = sub
                    break
                    done = True
            if done:
                break
        if done:
            break
                    
        t.append(transaction.Transaction(row))

    
    return t
    
def get_accounts():
    '''() -> void
    takes no parameters.
    opens a file containing the order of the account transactions
    and returns that order in a list.
    Now we can track where the transactions happened.'''
    with open("./accounts.fin", 'r') as f:
        a = f.readlines()
        for i in range(len(a)):
            if a[i][-1] == '\n':#strip out the \n at the end
                a[i] = a[i][:-1]
        f.close()
    
    return a

def save_configs(filename, cats):
    """(filename, cats) -> void
    saves categories into a json with the name filename
    """
    with open(filename, 'w') as f:
        dump(cats, f, indent=4, sort_keys=True)#use indent to pretty print

#Dictionary to access correct column of transaction
csv_fields = {
    'trans_id' : 0,
    'post' : 1,
    'effective' : 2,
    'trans_type' : 3,
    'amt' : 4,
    'chk_num' : 5,
    'ref_num' : 6,
    'desc' : 7,
    'trans_cat' : 8,
    'type' : 9,
    'balance' : 10,
    'memo' : 11,
    'ext_desc' : 12
}

def filter_transaction(trans, cat):
    """(trans, cat) -> void
    Searches through cats dictionary 
    for the description in trans.
    replaces the category with the one 
    that was found in cat from the 
    transactions description"""
    for key in cat.keys():
        done = False
        for desc in [x.lower() for x in cat[key]]:
            if desc.lower() in trans.desc.lower() or desc.lower() in trans.ext.lower():
                trans.cat = key
                done = True
                break
            else:
                trans.cat = 'uncategorized'
        if done:
            break

def filter_all_transactions(t, cats, file):
    '''(t, cats) -> [str, int]
    Accepts a Transaction as input and returns a list 
    showing which category the transaction belongs in
    and the amount of the transaction'''
    uncat = []
    if not file:#we're not going to sort at all
        return uncat, t
    
    #otherwise try to put it into the right category
    for trans in t:
        filter_transaction(trans, cats)
        if trans.cat == 'uncategorized':
            uncat.append(trans)

    for trans in uncat:#remove all the uncategorized transactions from t
        t.remove(trans)
        
    return t, uncat

def show_by_category(s, t):
    '''(s, t) -> void
    prints all transactions in t with the category s
    '''
    
    print("Showing all {0} transactions".format(s))
    print("==============================================================================")
    
    for trans in t:
        if trans.cat == s:
            trans.display()

    print("==============================================================================")


def show_by_date(s, t):
    '''(s, t) -> void
    prints all transactions in t with post date of s
    '''
    
    print("showing all transactions from {0}".format(s))
    for trans in t:
        if trans.post == s:
            trans.display()
    
    print("==============================================================================")


def update_category(new_cat, new_sub_cat, new_desc, sub_cats, cats):
    '''(new_cat, new_sub_cat, new_desc, sub_cats, cats) -> void
    checks cats for new_cat key, and adds it if not found.
    If it is found check sub_cats for new_sub_cat.
    If new_sub_cat is not found in sub_cats, then add it
    '''
    if new_cat not in cats.keys():
        cats[new_cat] = [new_sub_cat]
        sub_cats[new_sub_cat] = [new_desc]
    else:
        if new_sub_cat not in sub_cats.keys():
            sub_cats[new_sub_cat] = [new_desc]
        else:
            sub_cats[new_sub_cat].append(new_desc)

#TODO: add in a function that will add up the amount using the given filter
