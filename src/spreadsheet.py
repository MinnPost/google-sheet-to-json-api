import json
import datetime
from datetime import timedelta
from flask import current_app
from src.extensions import cache
from sheetfu import SpreadsheetApp

def parser(spreadsheet_id = None, worksheet_names = {}, cache_timeout = None):
    output = {}
    data = {}
    if spreadsheet_id is not None:
        for idx, worksheet_name in enumerate(worksheet_names):
            data[worksheet_name] = read_spreadsheet(spreadsheet_id, worksheet_name)
        data["generated"] = datetime.datetime.now()
        if cache_timeout is not None and cache_timeout != 0:
            data["cache_timeout"] = data["generated"] + timedelta(seconds=int(cache_timeout))
        elif cache_timeout == 0:
            data["cache_timeout"] = 0
        output = json.dumps(data, default=str)
    return output


@cache.memoize(60)
def read_spreadsheet(spreadsheet_id, worksheet_name):
    """
    Connect to Google spreadsheet and return the data as a list of dicts with the header values as the keys.
    """
    # list that will be returned
    data = []
    current_app.log.info('Connect directly to the spreadsheet %s and the worksheet %s.' % (spreadsheet_id, worksheet_name))
    try:
        # connect to and load the spreadsheet data
        client = SpreadsheetApp(from_env=True)
        spreadsheet = client.open_by_id(spreadsheet_id)
        sheet = spreadsheet.get_sheet_by_name(worksheet_name)
        data_range = sheet.get_data_range()
        rows = data_range.get_values()

        if rows is not None:
            
            # populate a list to parse
            csv_data = []
            for row in rows:
                csv_data.append(row)
            headings = []
            for cell in csv_data[0]:
                headings.append(cell)
            
            # parse each row in the list and set it up for returning
            for row in csv_data[1:]:
                this_row = {}
                for i in range(0, len(row)):
                    if row[i] == "":
                        row[i] = None
                    if isinstance(row[i], datetime.datetime):
                        row[i] = row[i].isoformat()
                    this_row[headings[i]] = row[i]
                data.append(this_row)

    except Exception as err:
        current_app.log.error('[%s] Unable to connect to spreadsheet source: %s. The error was %s' % ('spreadsheet', spreadsheet_id, err))
    return data

# do we need this?
def convert_xls_boolean(string):
    if string == None:
        value = False
    else:
        string = string.lower()
        if string == "yes" or string == "true":
            value = True
        elif string == "no" or string == "false":
            value = False
        else:
            value = bool(string)
    return value
