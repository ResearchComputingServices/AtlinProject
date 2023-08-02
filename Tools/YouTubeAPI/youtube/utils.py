from dateutil import parser
import sys
import traceback
import pandas as pd
import pathlib
import os
from werkzeug.utils import secure_filename
from datetime import datetime




#***********************************************************************************************************************
#***********************************************************************************************************************
def is_api_key_valid(error):
    try:
        msg = get_HTTP_error_msg(error)
        if "api" in msg.lower() and "valid" in msg.lower():
            return False
        else:
            return True
    except:
        #We couldn't check
        return True




#***********************************************************************************************************************
#***********************************************************************************************************************
def is_quota_exceeded(error):
    try:
        details = error.error_details
        reason = details[0]["reason"]
        if "quota" in reason.lower() and "exceeded" in reason.lower():
            return True
        else:
            return False
    except:
        #We couldn't check
        return False

#***********************************************************************************************************************
#***********************************************************************************************************************
def get_HTTP_error_msg(error):
    try:
        details = error.error_details
        reason = details[0]["message"]
        return reason
    except:
        return details



'API key not valid. Please pass a valid API key.'


#***********************************************************************************************************************
#***********************************************************************************************************************
def preprocess_string(string):
    string = " " + string
    return string



#*****************************************************************************************************
#This functions converts a UTC date to the local zone
#Returns date as a string
#*****************************************************************************************************
def convert_to_local_zone(datestring):
    try:
        utc_dt = parser.parse(datestring)
        local_dt = utc_dt.astimezone(None)
        date_time = local_dt.strftime("%Y-%m-%d, %H:%M:%S")
        return date_time
    except:
        return datestring

#***********************************************************************************************************************
#***********************************************************************************************************************
def get_ids_from_file(filename, id_column):
    try:
        ids = None
        #Load file
        df, success = read_excel_file_to_data_frame(filename,[id_column])
        if success:
            #Convert to list
            dfT = df.T
            idsl = dfT.values.tolist()
            #ids = list(set(idsl[0]))
            ids = idsl[0]
    except:
        print("Error on get_ids_from_file. Verify input file and header id")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return ids


#*****************************************************************************************************
#Read a excel file given as a parameter and if specific columns are provided those are extracted from
#the file.
#The file is returned as a data frame
#*****************************************************************************************************
def read_excel_file_to_data_frame(filename, columns=None):
    # Load file
    df = None
    success = False
    try:
        if filename:
            # filename = os.path.join(directory, filename)
            abs_path = pathlib.Path().resolve()
            filename_fullpath = os.path.join(abs_path, filename)
            data = pd.read_excel(filename_fullpath)
            if columns:
                try:
                    df = pd.DataFrame(data, columns=columns)
                except:
                    df = pd.DataFrame(data)
            else:
                df = pd.DataFrame(data)
            success = True
    except:
        print ("Error reading file: " + filename)
        print ("Please, verify if file exists.")
        df = None
        traceback.print_exc()

    return df, success




#*****************************************************************************************************
#This functions exports a dictionary to a excel file with filename given as a parameter
#*****************************************************************************************************
def export_dict_to_excel(records, directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)
    df = pd.DataFrame(records).T
    df.to_excel(filename_path, engine='xlsxwriter')
    df.to_excel(filename_path)
    return filename_path


# ***********************************************************************************************************************
# ***********************************************************************************************************************
def save_file(records, directory, filename):
    # Export info to excel
    if records and len(records)>0:
        filename_path = export_dict_to_excel(records, directory, filename)
        print("Output: " + filename_path)


#***********************************************************************************************************************
#***********************************************************************************************************************
def preprocess_string(string):
    #Apparently all strings that stats with "=" and other possible characteres are bothering excel.
    #We will add an empty space to avoid problems
    string = " " + string

    return string



#***********************************************************************************************************************
#***********************************************************************************************************************
def remove_prefix_url(url):
    #Attempt to remove https from url
    only_link = url
    try:
        prefix = 'https://'
        if url.startswith(prefix):
            only_link = url.split(prefix)[1];
        else:
            prefix = 'http://'
            if url.startswith(prefix):
                only_link = url.split(prefix)[1];
    except:
        only_link = url

    return only_link

#***********************************************************************************************************************
#***********************************************************************************************************************
def log_format(function, msg):
    dt = datetime.now()
    #log_string = "{time} : {type} : {function} : {msg}".format(time = dt, type = type, function = function, msg = msg)
    log_string = "{time} : {function} : {msg}".format(time=dt, type=type, function=function, msg=msg)

    return log_string


#*****************************************************************************************************
#This functions exports a dictionary to a csv file with filename given as a parameter
#*****************************************************************************************************
def get_fullpath(directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)
    return filename_path


#*****************************************************************************************************
#*****************************************************************************************************
def get_filename(name, extension):
    scrap_date = get_today_datetime()
    filename =  name + '__' + scrap_date + '_' + '.' + extension
    return filename


def get_today_datetime():
    now = datetime.now()
    dt_string = now.strftime("%Y_%m_%d")
    return dt_string
