
from datetime import date, datetime,timedelta
from pytz import timezone

todays_date = date.today()
today = todays_date.strftime("%B %-d, %Y")

# Input
import sys
if 'test' not in sys.argv:
    query = input('Enter a search term: ').replace(' ', '+')
    if query == 'b':
        query = 'bitcoin'
    start_date = input('Enter a start date in Y/M/D (e.g. 2021-02-22): ')
    if start_date == 'y':
        start_date = '2021-01-01'
    elif start_date== 't':
        start_date = datetime.utcnow()
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif start_date== 'yd':
        start_date = datetime.utcnow()
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    elif start_date== 'w':
        start_date = datetime.utcnow()
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
    elif start_date== 'm':
        start_date = datetime.utcnow()
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
    if type(start_date) is str:
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
    start_date = timezone("UTC").localize(start_date)
    print ('Getting articles on: ' + query + '...\n')
else:
    # query = ''
    query = None
    start_date = None
