import sys
from pdb import set_trace
import os.path,sys
import argparse
import tweepy
from time import sleep, time
from datetime import datetime
import langid
import json

from pythonlib_ys import main as myModule

class listener(tweepy.StreamListener):
    def __init__(self,FSwOrStdOut):
        self.out=FSwOrStdOut
    
    def on_data(self, data):
        self.out.write(data+'\n')
        return(True)

    def on_error(self, status):
        print(status)

def get_keys(FP):
    Keys=open(FP).read().strip().split('\n')
    if len(Keys)!=4:
        sys.exit('there have to be four keys')
    return Keys

def geo_valid_p(Long,Lat):
    return myModule.in_range(Long,(-180,180)) and myModule.in_range(Lat,(-90,90))

def coordpairs_wellformed_p(CoordPairs):
    Cond1=len(CoordPairs)==4
    CoordSW=CoordPairs[:2];CoordCentre=CoordPairs[2:]
    Cond2=geo_valid_p(CoordSW[0],CoordSW[1]) and geo_valid_p(CoordCentre[0],CoordCentre[1])
    Cond3=CoordSW[0]<CoordCentre[0] and CoordSW[1]<CoordCentre[1]
    Conds=[Cond1,Cond2,Cond3]
    if all(Conds):
        return True
    else:
        return False

def get_locations(FP,TgtPlaces=[]):
    Locs=[]
    TgtPlacesL=[ TgtPlace.lower() for TgtPlace in TgtPlaces ]
    with open(FP) as FSr:
        for LiNe in FSr:
            if LiNe.strip():
                NameCoordStrs=LiNe.strip().split('\t')
                CoordStrs=NameCoordStrs[1].split(',')

                if not TgtPlacesL:
                    DoIt=True
                else:
                    CandNameL=NameCoordStrs[0].lower()
                    if CandNameL in TgtPlacesL:
                        DoIt=True
                    else:
                        DoIt=False
                if not DoIt:
                    continue
                else:
                    CoordPairs=[float(CoordStr) for CoordStr in CoordStrs ]
                    if not coordpairs_wellformed_p(CoordPairs):
                        sys.stderr.write('\n[warning get_locations] this coordinates skipped, not well formed: '+repr(CoordPairs)+'\n')
                    Locs.extend(CoordPairs)
    if not Locs:
        sys.exit('\n[Error get_locations] no locations extracted\n')
                    
    return Locs


def get_tweets_stream(Lang,AuthkeyFile,GeocodeFile,TgtPlaces=[],OutputFP=None):
    if not OutputFP:
        Out=sys.stdout
    else:
        Out=open(OutputFP,'wt')
        sys.stderr.write('\n dest file name: '+OutputFP+'\n')
                                         
    if TgtPlaces:
        sys.stderr.write('\nwe only do these places :'+repr(TgtPlaces)+'\n')
    (ckey,csecret,atoken,asecret)=get_keys(AuthkeyFile)
    auth = tweepy.OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)

    twitterStream = tweepy.Stream(auth, listener(Out))
    Locs=get_locations(GeocodeFile,TgtPlaces=TgtPlaces)
    twitterStream.filter(locations=Locs)

    if OutputFP:
        Out.close()

def get_tweets_rest(language, file_words=None, file_geocodes=None, fileout=None, verbose=False):

    if fileout:
        try:
            fileout_obj = open(os.path.abspath(fileout), 'w')
        except IOError as e:
            msg = "[ERROR] %s: %s\n" % (os.path.basename(__file__), str(e))
            sys.exit(msg)
    else:
        fileout_obj = sys.stdout

    seed_words = []
    if file_words is not None:
        with open(os.path.abspath(file_words), 'r') as file_words_obj:
            seed_words = [e.strip() for e in file_words_obj]
        if len(seed_words) != len(set(seed_words)):
            msg = "[WARNING] %s: file %s contains duplicate lines\n" % (os.path.basename(__file__), file_words)
            sys.stderr.write(msg)

    geocodes = []
    if file_geocodes is not None:
        with open(os.path.abspath(file_geocodes), 'r') as file_geocodes_obj:
            for line in file_geocodes_obj:
                if not line.startswith('#'):
                    # each line is made of 5 fields separated by ';' but the geocode format 
                    # needed for twitter is only the 3 first fields, separated by ','
                    geocodes.append(','.join(line.strip().split(';')[:3]))
        if len(geocodes) != len(set(geocodes)):
            msg = "[WARNING] %s: file %s contains duplicate lines\n" % (os.path.basename(__file__), file_geocodes)
            sys.stderr.write(msg)


    (CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)=get_keys('keys.txt')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    def langid_guess_language(timeline):
        # gather all the text of the tweets and normalize it to lowercase
        tweets_text = ' '.join([e.text.lower() for e in timeline])
        guessed_language, confidence_score = langid.classify(tweets_text.strip())
        return guessed_language

    def followers(user):
        global last_followers
        if time() < last_followers+wait_followers:
            sleep(last_followers+wait_followers - time()+1)
        last_followers = time()
        try:
            result = user.followers()
        except tweepy.error.TweepError as e:
            msg = "[WARNING] %s: an error occured during call to followers() function : %s\n" % (os.path.basename(__file__), str(e))
            sys.stderr.write(msg)
            return []
        return result

    def friends(user):
        global last_friends
        if time() < last_friends+wait_friends:
            sleep(last_friends+wait_friends - time()+1)
        last_friends = time()
        try:
            result = user.friends()
        except tweepy.error.TweepError as e:
            msg = "[WARNING] %s: an error occured during call to friends() function : %s\n" % (os.path.basename(__file__), str(e))
            sys.stderr.write(msg)
            return []
        return result

    def write_timeline(timeline):
        for tweet in timeline:
            fileout_obj.write(json.dumps(tweet._json, ensure_ascii=False))
            fileout_obj.write("\n")

    def process_timeline(screen_name, since_id=None, retrieval_method="undefined"):
        global last_timeline
        if verbose:
            sys.stderr.write('LAST_TIMELINE: ' + str(last_timeline) + '\n')
            
        if time() < last_timeline+wait_timeline:
            sleep(last_timeline+wait_timeline - time()+1)
        last_timeline = time()
        
        if since_id is None:
            # process_timeline is called with since_id==None only when we try to retrieve a user's timeline for the first time
            try:
                timeline = api.user_timeline(screen_name, count=NUMBER_OF_TWEETS_TO_RETRIEVE)
            except tweepy.error.TweepError as e:
                sys.stderr.write(datetime.now().isoformat() + '\tUser ' + screen_name + ' found by ' + retrieval_method + ' function could not be retrieved (protected account).\n')
                user_dict[screen_name] = None
                return True
        else:
            # if since_id is not None it means we have already seen the user and already processed part of its timeline
            # if CRAWL_NEW_TWEETS_FROM_SEEN_USERS == True then we will try to get user's timeline several times (in order to have more tweets)
            try:
                timeline = api.user_timeline(screen_name, since_id=since_id)
            except tweepy.error.TweepError as e:
                msg = "[WARNING] %s: an error occured during call to tweepy user_timeline() function : %s\n" % (os.path.basename(__file__), str(e))
                sys.stderr.write(msg)
                sys.stderr.write(datetime.now().isoformat() + '\tKnown user ' + screen_name + ' timeline not fetched. Will continue on trying.\n')
                return True

        if since_id is None:
            # to do the language guessing we need a certain amount of tweets in the timeline
            # otherwise result of the language guesser are not reliable
            if len(timeline) < MINIMAL_NUM_OF_TWEETS:
                sys.stderr.write(datetime.now().isoformat() + '\tNew user ' + screen_name + ' [' + retrieval_method + '] timeline did not pass the size threshold (only ' + str(len(timeline)) + ' tweets).\n')
                user_dict[screen_name] = None
                return True
            # for new users, we check if they do post in the desired language
            #if langid_guess_language(timeline) != language:
            #    sys.stderr.write(datetime.now().isoformat() + '\tNew user ' + screen_name + ' [' + retrieval_method + '] timeline did not pass the language filter\n')
                # None value for a user in the user_dict indicates an already seen user filtered out (here, by language guessing)
                user_dict[screen_name] = None
                return True
            else:
                sys.stderr.write(datetime.now().isoformat() + '\tNew user ' + screen_name + ' [' + retrieval_method + '] timeline successfully retrieved\n')
                user_dict[screen_name] = timeline[0].id
                write_timeline(timeline)
                return True
        else:
            if len(timeline) > 0:
                sys.stderr.write(datetime.now().isoformat() + '\tKnown user ' + screen_name + ' timeline fetched with ' + str(len(timeline)) + ' new tweets.\n')
                user_dict[screen_name] = timeline[0].id
                write_timeline(timeline)
                return True
            else:
                sys.stderr.write(datetime.now().isoformat() + '\tKnown user ' + screen_name + ' timeline fetched with no new tweets.\n')
                return True

    user_dict = {}
    iterations = 0
    global last_search
    index_geocode = 0

    while True:
        if seed_words:
            sys.stderr.write('USE OF A SEEDWORDS LIST\n')
            # start iterating through seed words and searching for users
            for seed in seed_words:
                sys.stderr.write('SEED: ' + seed + "\n")
                # if geocodes are provided, use them to restrict the search
                if geocodes:
                    sys.stderr.write('USE OF A GEOLOC LIST\n')
                    try:
                        coords = geocodes[index_geocode]
                        sys.stderr.write('COORDS [' + str(index_geocode) + ']: ' + str(coords) + "\n")
                        index_geocode = index_geocode + 1
                    except IndexError as e:
                        # if an IndexError has been raised, we reinitialized the index_geocode value to 0
                        # in order to get back to the beginning of the geocodes list
                        index_geocode = 0
                        coords = geocodes[index_geocode]
                        sys.stderr.write('COORDS [' + str(index_geocode) + ']: ' + str(coords) + "\n")
                else:
                    coords = ''

                if time() < last_search+wait_search:
                    sleep(last_search+wait_search - time()+1)
                last_search = time()
                
                try:
                    # TODO: stripping of potential ZWJ/ZWNJ on seed
                    #hits = api.search(q=seed.strip(), geocode=coords, count=100, result_type="recent")
                    hits = api.search(q=seed.strip(), geocode=coords)
                except tweepy.error.TweepError as e:
                    msg = "[WARNING] %s: an error occured during call to tweepy search() function : %s\n" % (os.path.basename(__file__), str(e))
                    sys.stderr.write(msg)
                    hits = []

                for hit in hits:
                    if hit.author.screen_name in user_dict:
                        sys.stderr.write(datetime.now().isoformat() + '\tUser ' + hit.author.screen_name + ' [search()] already in the user_dict.\n')                        
                    else:
                        process_timeline(hit.author.screen_name, None, 'search()')
                        # we search for followers and friends only is the user has passed language filtering (== value or user_dict[user] is not None)
                        if user_dict[hit.author.screen_name] is not None:
                            for follower in followers(hit.author):
                                if follower.screen_name not in user_dict:
                                    process_timeline(follower.screen_name, None, 'followers()')
                                else:
                                    sys.stderr.write(datetime.now().isoformat() + '\tUser ' + follower.screen_name + ' [followers()] already in the user_dict.\n')
                            for friend in friends(hit.author):
                                if friend.screen_name not in user_dict:
                                    process_timeline(friend.screen_name, None, 'friends()')
                                else:
                                    sys.stderr.write(datetime.now().isoformat() + '\tUser ' + friend.screen_name + ' [friends()] already in the user_dict.\n')
                sys.stderr.write(datetime.now().isoformat() + '\tNumber of users in the user_dict: ' + str(len(user_dict)) + '\n')

        # no seed words, but list of geocodes is given
        elif geocodes:
            sys.stderr.write('USE OF A GEOLOC LIST\n')
            for coords in geocodes:
                sys.stderr.write('COORDS: ' + str(coords) + "\n")

                if time() < last_search+wait_search:
                    sleep(last_search+wait_search - time()+1)
                last_search = time()
                
                try:
                    hits = api.search(q='', geocode=coords)
                except tweepy.error.TweepError as e:
                    msg = "[WARNING] %s: an error occured during call to tweepy search() function : %s\n" % (os.path.basename(__file__), str(e))
                    sys.stderr.write(msg)
                    hits = []

                for hit in hits:
                    if hit.author.screen_name in user_dict:
                        sys.stderr.write(datetime.now().isoformat() + '\tUser ' + hit.author.screen_name + ' [search()] already in the user_dict.\n')                        
                    else:
                        process_timeline(hit.author.screen_name, None, 'search()')
                        # we search for followers and friends only is the user has passed language filtering (== value or user_dict[user] is not None)
                        if user_dict[hit.author.screen_name] is not None:
                            for follower in followers(hit.author):
                                if follower.screen_name not in user_dict:
                                    process_timeline(follower.screen_name, None, 'followers()')
                                else:
                                    sys.stderr.write(datetime.now().isoformat() + '\tUser ' + follower.screen_name + ' [followers()] already in the user_dict.\n')
                            for friend in friends(hit.author):
                                if friend.screen_name not in user_dict:
                                    process_timeline(friend.screen_name, None, 'friends()')
                                else:
                                    sys.stderr.write(datetime.now().isoformat() + '\tUser ' + friend.screen_name + ' [friends()] already in the user_dict.\n')
                sys.stderr.write(datetime.now().isoformat() + '\tNumber of users in the user_dict: ' + str(len(user_dict)) + '\n')


        if CRAWL_NEW_TWEETS_FROM_SEEN_USERS:
            # iterating through all users for whom we have already retrieved their timeline, in order
            # to get their new tweets
            for screen_name, since_id in list(user_dict.items()):
                # the None value indicated the user has been discarded (insufficient number of tweets, or language filtered user, or protected account)
                if since_id is None:
                    continue
                process_timeline(screen_name, since_id, 'iterate_through_users')

        iterations += 1
        sys.stderr.write('Finished ' + str(iterations) + ' iteration(s) out of ' + str(ITERATION_COUNT) + '. Number of seen users is ' + str(len(user_dict)) + '.\n')

        if iterations == ITERATION_COUNT:
            break
        sys.stderr.write('Sleeping ' + str(SLEEP_BETWEEN_ITERATIONS) + ' seconds...\n')
        sleep(SLEEP_BETWEEN_ITERATIONS)

    if fileout_obj.name != "<stdout>":
        fileout_obj.close()

def main():
    msg = "PYTHON VERSION: %s\n" % sys.version
    sys.stderr.write(msg)
    sys.stderr.flush()
    msg = "TWEEPY VERSION: %s\n" % tweepy.__version__
    sys.stderr.write(msg)
    sys.stderr.flush()

    # SANITY_CHECK
    if NUMBER_OF_TWEETS_TO_RETRIEVE < MINIMAL_NUM_OF_TWEETS:
        sys.stderr.write("[ERROR] NUMBER_OF_TWEETS_TO_RETRIEVE is smaller than MINIMAL_NUM_OF_TWEETS\n")
        sys.stderr.write("Please, set proper values.\n")
        sys.exit(2)

    ArgParser=argparse.ArgumentParser()
    ArgParser.add_argument('-l','--lang',required=True)
    ArgParser.add_argument('-g','--geocode-file',required=True)
    ArgParser.add_argument('-k','--authkey-file',required=True)
    ArgParser.add_argument('-p','--target-places',nargs='+',type=str,default=[])
    ArgParser.add_argument('-o','--output-fpstem',default=None)
    #ArgParser.add_argument('--timeout',default='2h')
    Args=ArgParser.parse_args()

    #TOInSecs=myModule.timestr2seconds(Args.timeout)

    Now=datetime.now()
    NowStr=Now.strftime('%y%m%d-%H%M')
    OutputFP=(None if not Args.output_fpstem else Args.output_fpstem+'_'+NowStr+'.json')
    
    get_tweets_stream(Lang=Args.lang, AuthkeyFile=Args.authkey_file,GeocodeFile=Args.geocode_file,TgtPlaces=Args.target_places,OutputFP=OutputFP)
    #TimeOut=TOInSecs)
        
if __name__ == "__main__":
    SLEEP_BETWEEN_ITERATIONS = 30             # number of seconds
    ITERATION_COUNT = 0                       # 0 for unlimited number of iterations
    CRAWL_NEW_TWEETS_FROM_SEEN_USERS = False   # if set to True, will iterate on all kept users in order to crawl their new tweets
    MINIMAL_NUM_OF_TWEETS = 10               # minimal num of tweets to decide to keep a user
    NUMBER_OF_TWEETS_TO_RETRIEVE = 100        # max num of tweets to be returned the first time we retrieve one user's timeline

    wait_timeline = 5
    wait_search = 5
    wait_friends = 60
    wait_followers = 60

    last_timeline = 0
    last_search = 0
    last_friends = 0
    last_followers = 0

    # list of languages supported by langid
    LIST_OF_SUPPORTED_LANGUAGES = ['af', 'am', 'an', 'ar', 'as', 'az', 'be', 'bg', 'bn', 'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'dz', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fo', 'fr', 'ga', 'gl', 'gu', 'he', 'hi', 'hr', 'ht', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jv', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'la', 'lb', 'lo', 'lt', 'lv', 'mg', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'nb', 'ne', 'nl', 'nn', 'no', 'oc', 'or', 'pa', 'pl', 'ps', 'pt', 'qu', 'ro', 'ru', 'rw', 'se', 'si', 'sk', 'sl', 'sq', 'sr', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'ug', 'uk', 'ur', 'vi', 'vo', 'wa', 'xh', 'zh', 'zu']


    
    main()


#    main(language=Args.lang, file_words=None, file_geocodes=Args.geocode_file, fileout=None, verbose=False)
