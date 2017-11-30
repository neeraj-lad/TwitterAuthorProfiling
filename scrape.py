# https://docs.python.org/2/library/xml.etree.elementtree.html
import xml.etree.ElementTree as ET
import selenium.webdriver as webdriver
from ttp import ttp
import json

class Tweet_Corpus:
    #user_id = None
    # tweet_id
    tweet_id = None
    # tweet_text
    tweet_text = None
    # 0 for female / 1 for male
    tweet_gender = None
    # encoding 18-24 = 0, 25-34 = 1, 35-49 = 2, 50-64 = 3, >64 = 4 
    tweet_age = None
    # get number of hashtags
    tweet_tags = None
    # is url mentioned 0 for False / 1 for True
    is_url_present = False
    
    def __init__(self, user, id, tweet, gender, age, tags, is_url):
        # get user id
        self.user_id = user
        # get tweet id
        self.tweet_id = id
        # get tweet text
        self.tweet_text = tweet
        # gender encoding
        self.tweet_gender = 0 if gender == 'FEMALE' else 1
        # age encoding
        if(age == '18-24'): self.tweet_age = 0
        elif(age == '25-34'): self.tweet_age = 1
        elif(age == '35-49'): self.tweet_age = 2
        elif(age == '50-64'): self.tweet_age = 3
        elif(age == '65-xx'): self.tweet_age = 4
        # of tags
        self.tweet_tags = tags
        # is url mentioned
        self.is_url_present = is_url

    def __repr__(self):
        return str(self.user_id) + '|' + str(self.tweet_id) + '|' + str(self.tweet_text) + '|' + str(self.tweet_gender) + '|' + str(self.tweet_age) + '|' + str(self.tweet_tags) + '|' + str(self.is_url_present)

    
class Scrape_tweets:
    
    def __init__(self):
        self.ttp_parser = ttp.Parser()
    
    def config_selenium(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=options, executable_path='../../chrome_driver/chromedriver.exe')
        return driver
    
    def process_tweet_data(self, tweet_text):
        parse_result = self.ttp_parser.parse(tweet_text)
        return len(parse_result.tags), True if len(parse_result.urls) > 0 else False 
    
    def read_truth_file(self):
        truth_file = open('../dataset/english_corp/truth.txt', 'r')
        # get selenium driver
        sel_driver = self.config_selenium()
        all_tweets_corpus = []
        user_cnt = 1
        for line in truth_file:
            file_id, gender, age = line.strip().split(":::")
            print('User: %d | Start: %s' % (user_cnt, file_id))
            # read each user file and all tweets from each of the file
            filename = '../dataset/english_corp/' + file_id + '.xml'
            user_file = open(filename, 'r')
            tree = ET.parse(user_file)
            root = tree.getroot()
            tweet_cnt = 0
            for all_docs in root.findall('documents'):
                for sub_doc in all_docs:
                    tweet_cnt += 1
                    if tweet_cnt > 50:
                        break
                    tweet_id = sub_doc.get('id')
                    tweet_url = sub_doc.get('url')
                    #print(tweet_id + ":" + file_id)
                    sel_driver.get(tweet_url)
                    element = sel_driver.find_elements_by_css_selector('div.tweet')
                    if(len(element) == 0): continue
                    tweet_text = element[0].find_element_by_css_selector('p.tweet-text').text
                    tags, is_url = self.process_tweet_data(tweet_text)
                    tc = Tweet_Corpus(file_id, tweet_id, tweet_text, gender, age, tags, is_url)
                    all_tweets_corpus.append(tc)
                    with open('tweets_fifty_per_user.txt', 'a') as f:
                        f.write(json.dumps(tc.__dict__) + '\n')

                if tweet_cnt > 50:
                    break
            user_cnt += 1
        '''
        all_tweets_corpus_json_str = ''
        for tweet in all_tweets_corpus:
            all_tweets_corpus_json_str += json.dumps(tweet.__dict__) + '\n'
        '''
       
if __name__ == '__main__':
    # get ground truth
    scr = Scrape_tweets()
    scr.read_truth_file()
