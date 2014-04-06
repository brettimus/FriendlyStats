"""
/****************************************************/
 **  friendlyStats.py  **
 ************************
 *  :: VERSION     :: v0.1
 *  :: AUTHOR      :: Brett Beutell (@brettimus, @rudeboojay)
 *  :: DATE        :: 4/5/2014
 *  :: DESCRIPTION :: Writes a comma-delimited CSV file, 
 *                     with basic data on all friends of 
 *                     the ACCESS_TOKEN's corresponding user.
 *  :: TODO        :: 
 *                    [ ] Take command line args
 *                    [ ] Throw CustomErrors
 *                    [-] Parse language, favorite_athletes lists
 *                        ==> HALF-DONE: See safe_append()
 *                    [ ] Scrape link corresponding to each friend's page
 *  ----------------------------------------
 *  | Before starting, here's a checklist! |
 *  ---------------------------------------
 *  [ ] Make sure you are a registered FB developer (https://developers.facebook.com/)
 *  [ ] Get your ACCESS_TOKEN from Heroku (https://getmyaccess.heroku.com/)
 *  [ ] Check that DEBUG = False (below)
 *
 *  --------------------------------
 *  | From The Python Facebook SDK |
 *  --------------------------------
 *  Descriptions of the facebook library functions used herein
 *
 *  -----------------------------------
 *  g = facebook.GraphAPI(ACCESS_TOKEN)
 *  -----------------------------------
 *  [x] Establishes connection to facebook's GraphAPI
 *  [x] g can perform queries (see next)
 *
 *  ------------------------------------
 *  friends = g.get_object("me/friends")
 *  ------------------------------------
 *  [x] Returns JSON containing friends' names + id numbers
 *  [x] This data can be accessed through the 'data' key of
 *      the resulting JSON dict object (friends).
 *      E.g.,
              > friends['data']
 *  [x] The id is useful for looking up additional data about
 *      one's friends. 
 *  [x] I promise this is not creepy.
 *
 *  
 *
/****************************************************/
"""

import facebook
import csv
from pprint import pprint
from datetime import date
from random import randrange  # Used in DEBUG mode

### * DEBUGGING SWITCH * ###
DEBUG = False
### * OTHER SETTINGS   * ###

ACCESS_TOKEN = '' # Expires often
KEYS = ['id', 
          'name', 
          'first_name', 
          'middle_name',
          'last_name',
          'username',
          'bio',
          'locale',
          'gender',
          'birthday',
          'about',
          'quotes',
          #'favorite_athletes',  # list
          #'languages',          # list
          'updated_time']

### * CLASS * ###
class FriendlyRetriever(object):
    TO_WRITE = []
    def __init__(self, QUALITIES_OF_INT, ACCESS_TOKEN='',DEBUG=False):
        self.q_of_i = QUALITIES_OF_INT
        self.ACCESS_TOKEN = ACCESS_TOKEN
        try:
            self.g = facebook.GraphAPI(ACCESS_TOKEN)
        except facebook.GraphAPIError:
            # TODO write custom error for this
            print("WARNING! Connection failed. Check your token. \n")
            pass 
        self.friends = self.g.get_object('me/friends')['data']  # 'node/connection' syntax, and 
                                                                # 'data' key returns list of dicts with friend names & ids
        self.DEBUG = DEBUG
        self.output_filename = "facebook-friends-%s.csv" % str(date.today())

    ### * Helper Methods * ###
    def get_friend(self,friend):
        """ Query friend's public data with their stringified id number """
        return self.g.get_object(str(friend['id']))

    def safe_append(self, friend, key, row_data):
        """ 
           Error handling for trying to access nonexistent key  
           Assigns 'NA' if field is missing from user's data
           E.g., not everyone lists their middle name,
           so we often don't find the "middle_name"
           key in our dict 
        """
        try:
            row_data.append(friend[key].encode('ascii','replace')) # 'replace' keeps character len. of orig
        except KeyError:
            # Datum is missing
            row_data.append('NA')
        except AttributeError:
            # We might have a list
            if isinstance(friend[key],list):
                # Unpack and delimit with special character (not ',')
                pass
            else:
                pass
            
    ### * The Big Kahuna * ###
    def friendlyStats(self):
        """
           open a file and write to it row by row
           where each row is a facebook friend
           --- NOTE ---
           with() closes file buffer automagically
        """
        of = self.output_filename
        keys = self.q_of_i
        TO_WRITE = []

        with open(of, 'w+') as csvf:
            wrt = csv.writer(csvf, delimiter=',')  # Comma delimits values
            wrt.writerow(keys)
            for fr in self.friends:
                friend = self.get_friend(fr)
                for key in keys:
                    self.safe_append(friend, key, TO_WRITE)
                wrt.writerow(TO_WRITE)
                TO_WRITE = []

    ### * The Test Procedure * ###
    def fs_test(self):
        """ When DEBUG is on (=True), we simply pprint the quantities of interest
        for 3 of our friends. """
        keys = self.q_of_i
        TO_WRITE = []   # What we *would* write in prod
        pprint(keys)  # Header        
        # Select three friends at random from sample of 100
        rFriends = [randrange(1,101), randrange(1,101), randrange(1,101)]
        # Loop through each quality of interest
        for r in rFriends:
            for key in keys:
                self.safe_append(self.get_friend(self.friends[r]), key, TO_WRITE)
        pprint(TO_WRITE)  # pretty-prints our row data
        TO_WRITE = []     # clears the row data for next iteration

    ### * The main procedure * ###
    def main(self):
        """ Debugging condition pardon me  """
        return self.fs_test() if self.DEBUG else self.friendlyStats()


### * Run the program * ###
fr = FriendlyRetriever(KEYS, ACCESS_TOKEN, DEBUG=False)
fr.main()
