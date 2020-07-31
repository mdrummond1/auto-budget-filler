#module for functions
from calendar import monthlen
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass

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

    if start_month == 0:
        start_month = '12'
        start_yr = str(today.tm_year - 1)

    last_day = monthlen(int(start_yr), int(start_month))

    #take care of months that have different number of days
    if int(start_day) > last_day:
            start_day = str(last_day)

    end_day = start_day
    end_month = str(today.tm_mon)
    end_yr = start_yr
    
    start_date = "arguments[0].setAttribute('value', '" + start_month + '/' + start_day + '/' + start_yr + "')"
    end_date = "arguments[0].setAttribute('value', '" + end_month + '/' + end_day + '/' + end_yr + "')"

    date = {
        'start_date': start_date,
        'end_date' : end_date
    }
    return date

def get_log_info():
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
    driver.execute_script(date['start_date'], start)
    end = driver.find_element_by_id("Parameters_EndDate")
    driver.execute_script(date['end_date'], end)

#use dictionary or tuple to tell function what we want to do
'''switch(choice){

    case wait_id:
    case wait_class
    case wait_id_click
    case wait_class_click
}
'''