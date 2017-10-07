import os
import requests
import json
import re
import datetime
import time

# the local path to where your osf-data should be stored
LOCAL_DATA_PATH = '/Users/maxfowler/Desktop/osf-data'

# the name of the output_bin you are using in s3
S3_BIN = 'mfowler'

# make sure your local environment variables are set, or replace the following with hard-coded strings
fb_username = os.environ.get('FB_USERNAME')
fb_password = os.environ.get('FB_PASSWORD')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# set which users you want to scrape
users = [
    'maxhfowler',
    'hxrts'
]

# the api domain that requests will be made to
API_DOMAIN = 'http://api.opensourcefeeds.com'


if __name__ == '__main__':

    # sync data from s3 bin to your local folder
    print '++ syncing data from {} to {}'.format(S3_BIN, LOCAL_DATA_PATH)
    cmd = 'AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY} ' \
          'aws s3 sync s3://opensourcefeeds/output/{S3_BIN} {LOCAL_DATA_PATH}'.format(
        AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY,
        S3_BIN=S3_BIN,
        LOCAL_DATA_PATH=LOCAL_DATA_PATH
    )
    os.system(cmd)

    # search through the files in local folder to find the time of the most recent scraping
    timestamps = []
    f_names = os.listdir(LOCAL_DATA_PATH)
    for f_name in f_names:
        match = re.match('(\d+)\.json', f_name)
        if match:
            tstamp = int(match.group(1))
            timestamps.append(tstamp)

    # if there are timestamps, then this isn't the first scrape, and let's find the time of last scrape
    if timestamps:
        # sort timestamps from latest to earliest
        timestamps.sort(reverse=True)
        after_timestamp = timestamps[0]
        print '++ setting after_timestamp to time of latest scrape: {}'.format(after_timestamp)
    # otherwise, this is the first scrape, lets just get posts from 1 month ago
    else:
        now = datetime.datetime.now()
        one_month_ago = now - datetime.timedelta(days=30)
        after_timestamp = time.mktime(one_month_ago.timetuple())
        print '++ no prior data found, setting after_timestamp to 1 month ago'

    print '++ making new request to scrape fb posts'
    job_params = {
        'fb_username': fb_username,
        'fb_password': fb_password,
        'users': users,
        'after_timestamp': after_timestamp,
        'output_bin': S3_BIN
    }
    url = '{API_DOMAIN}/api/fb_posts/'.format(API_DOMAIN=API_DOMAIN)
    headers = {'content-type': 'application/json'}
    requests.post(url, data=json.dumps(job_params), headers=headers)
