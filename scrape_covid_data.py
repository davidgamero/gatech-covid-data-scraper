from bs4 import BeautifulSoup
import requests
import re
import os
from os import path
import csv

COVID_DATA_URL = 'https://health.gatech.edu/coronavirus/health-alerts'

COVID_DATA_CSV = 'gatech_covid_data.csv'

# The number of child elements that valid data rows have (4 columns)
VALID_ROW_NUM_CHILDREN = 4

VALID_POSITIONS = ['Student', 'Students', 'Staff', 'Various']

ROW_INDEX_DATE = 0
ROW_INDEX_POSITION = 1
ROW_INDEX_LAST_ON_CAMPUS = 2
ROW_INDEX_CAMPUS_IMPACT = 3

RE_POSITION_PAREN = re.compile('\(([0-9]+)\)')
RE_INTEGERS = re.compile('([0-9]+)')

RE_YEAR = re.compile(',[ ]+([0-9]{2,5})')
MIN_ROW_YEAR = 2020


def write_covid_data_csv(csv_path):
    data_reponse = requests.get(COVID_DATA_URL)

    covid_soup = BeautifulSoup(data_reponse.content, 'html.parser')

    # Find table rows
    rows = covid_soup.find_all('tr')
    print('{} rows scraped from {}'.format(len(rows), COVID_DATA_URL))

    # Filter by number of child elements
    rows = list(filter(lambda row: len(row.findChildren())
                       == VALID_ROW_NUM_CHILDREN, rows))
    print('{} rows passed filter limiting to rows with {} child elements'.format(
        len(rows), VALID_ROW_NUM_CHILDREN))

    # Filter by containing a valid position

    def filter_valid_position(row):
        position_text = row.findChildren()[ROW_INDEX_POSITION].text
        return any(map(lambda p: p in position_text, VALID_POSITIONS))

    rows = list(filter(filter_valid_position, rows))
    print('{} rows passed filter with valid positions'.format(len(rows)))

    # Extract text from html elements

    def row2text(row):
        row_text = list(map(lambda child: child.text, row.findChildren()))
        return row_text

    text_rows = list(map(row2text, rows))

    dates = []  # List of dates captured ordered descending
    date_2_num_cases = {}

    extractions = []  # List of rows where a number of cases was extracted from the text
    failed_rows = []  # List of rows that failed to be processed

    def add_extraction(row_date, num_cases, extraction_type, source_text):
        extractions.append({
            'date': row_date,
            'numCases': num_cases,
            'extractionType': extraction_type,
            'sourceText': source_text
        })

    def getYearInt(dateString):
        re_year_result = RE_YEAR.search(dateString)
        if re_year_result is not None and re_year_result.group(1) is not None:
            return int(RE_YEAR.search(dateString).group(1))
        return -1

    def cleanText(text):
        text = text.strip()

        # Replace multiple spaces with a single space
        text = re.sub(' +', ' ', text)

        # Strip non-ascii characters
        # https://stackoverflow.com/questions/8689795/how-can-i-remove-non-ascii-characters-but-leave-periods-and-spaces-using-python
        text = re.sub(r'[^\x00-\x7f]', r'', text)

        return text

    # Parse the number of covid cases from a given row

    def parse_num_cases(row):
        # Student singular
        row_date = cleanText(row[ROW_INDEX_DATE])
        row_position = cleanText(row[ROW_INDEX_POSITION])
        row_campus_impact = cleanText(row[ROW_INDEX_CAMPUS_IMPACT])

        # Verify valid date years
        if(getYearInt(row_date) < MIN_ROW_YEAR):
            print('INVALID DATE ROW IGNORED')
            print('|'.join(row))
            return -1

        # Have we seen this date before? If not, initialize
        if row_date not in date_2_num_cases:
            date_2_num_cases[row_date] = 0
            dates.append(row_date)

        # Verify year doesn't go backwards in the rows
        if(getYearInt(row_date) > getYearInt(dates[-1])):
            row_date = dates[-1]  # Use last valid year
            print('Replacing date for {}'.format(row))

        if(row_position == 'Student'):
            return 1

        # Staff singular
        if(row_position in ['Staff', 'Staff member']):
            return 1

        # POSITION '(N)' format
        re_position_paren = RE_POSITION_PAREN.search(
            row_position)
        if(re_position_paren != None and re_position_paren.group(1) != None):
            # Extract the number between the parentheses
            num_cases = int(re_position_paren.group(1))

            add_extraction(row_date, num_cases, 'POSITION N', row_position)
            print('{} Extracted {} cases from Position="{}"'.format(
                row_date, num_cases, row_position))
            return num_cases

        # 'Students' with number in 'campus impact' column
        if(row_position in ['Students', 'Various']):
            re_integers = RE_INTEGERS.search(row_campus_impact)
            # Use regex to match first integer
            num_cases = int(re_integers.group(1))

            # Alert warning for possibly lossy extraction
            add_extraction(row_date, num_cases, 'IMPACT', row_campus_impact)
            print('{} Extracted {} cases from text:  \n "{}"\n'.format(
                row_date, num_cases, row_campus_impact))

            return num_cases

        # Alert unhandled rows to add cases
        print('UNHANDLED ROW IGNORED')
        print('|'.join(row))
        return -1

    # Parse case numbers and collapse on each date
    for row in text_rows:
        date = cleanText(row[ROW_INDEX_DATE])  # TODO extract date cleanly

        # If the row was processed successfully
        if(parse_num_cases(row) != -1):
            # Add the number of new cases from this row
            date_2_num_cases[date] += parse_num_cases(row)
        else:
            failed_rows.append(row)

    # Write to csv
    # Delete existing csv before writing a new one
    if(path.exists(csv_path)):
        os.remove(csv_path)

    with open(csv_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)

        csvwriter.writerow(('date', 'cases'))

        for date in dates:
            csvwriter.writerow((date, date_2_num_cases[date]))

    print('Success! Scraped data for {} dates from {} to {}'.format(
        len(dates), dates[-1], dates[0]))

    response = {
        'failedRows': len(failed_rows),
        'rows': len(rows),
        'dates': len(dates),
        'dateStart': dates[0],
        'dateEnd': dates[-1],
        'extractions': extractions
    }

    return response


if __name__ == "__main__":
    write_covid_data_csv(COVID_DATA_CSV)
