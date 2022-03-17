import datetime
from flask import current_app
from src.extensions import cache
from sheetfu import SpreadsheetApp

def parser(spreadsheet_id = None, worksheet_names = [""], worksheet_keys = [""]):
    data = {}
    if spreadsheet_id is not None:
        if worksheet_names == [""]:
            sheets = get_spreadsheet_sheets(spreadsheet_id)
            if worksheet_keys != [""]:
                worksheet_names = []
                for worksheet_key in worksheet_keys:
                    worksheet_name = sheets[int(worksheet_key)].name
                    if worksheet_name:
                        worksheet_names.append(worksheet_name)
            else:
                first_worksheet_name = sheets[0].name
                worksheet_names = first_worksheet_name.split(current_app.config["WORKSHEET_NAME_SEPARATOR"])
        for worksheet_name in worksheet_names:
            data[worksheet_name] = read_spreadsheet(spreadsheet_id, worksheet_name)
        data["generated"] = datetime.datetime.now()
    return data


@cache.memoize(10)
def get_spreadsheet_sheets(spreadsheet_id):
    """
    Connect to Google spreadsheet and return the list of sheets
    """
    # list that will be returned
    data = []
    current_app.log.info("Connect directly to the spreadsheet %s." % (spreadsheet_id))
    try:
        # connect to and load the spreadsheet data
        client = SpreadsheetApp(from_env=True)
        spreadsheet = client.open_by_id(spreadsheet_id)
        sheets = spreadsheet.get_sheets()
        data = sheets
    except Exception as err:
        current_app.log.error("[%s] Unable to connect to spreadsheet source: %s to read its list of worksheets. The error was %s" % ('spreadsheet', spreadsheet_id, err))
    
    return data


@cache.memoize(10)
def read_spreadsheet(spreadsheet_id, worksheet_name = None, sheet = None):
    """
    Connect to Google spreadsheet and return the data as a list of dicts with the header values as the keys.
    """
    # list that will be returned
    data = []
    current_app.log.info("Connect directly to the spreadsheet %s and the worksheet %s." % (spreadsheet_id, worksheet_name))
    try:
        # connect to and load the spreadsheet data
        client = SpreadsheetApp(from_env=True)
        spreadsheet = client.open_by_id(spreadsheet_id)
        if worksheet_name != None:
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
        current_app.log.error("[%s] Unable to connect to spreadsheet source: %s. The error was %s" % ('spreadsheet', spreadsheet_id, err))
    return data

# todo: if there are any universally applicable formatting methods we can trust, add them here
