import os
import json
import math, re, jieba
import requests
import jieba.posseg as pseg
from fractions import Fraction
from collections import defaultdict, Counter
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER

# ckip-Tagger installation
# Put data in Backend first~
ws = WS("./data")
pos = POS("./data")
ner = NER("./data")

os.chdir(os.getcwd())

stopwords = []
all_words_dict = {}
forum_dict = {}
D_dict = {}

with open('stopwords.txt', 'r') as f:
    stopwords = f.read().split('\n')
with open('all_words_dict.json', 'r') as f:
    all_words_dict = json.loads(f.read())
with open('forum_dict.json', 'r') as f:
    forum_dict = json.loads(f.read())
with open('D_dict.json', 'r') as f:
    D_dict = json.loads(f.read())
stopwords.extend(['.', '/', ':', '-', ' ', '(', ')', '⋯', '=', '～', '妳', '會', '裡', '說', '沒'])
totalD = 16810539

jieba.case_sensitive = False
jieba.set_dictionary("dict.txt")
jieba.load_userdict("user_dict.txt")


def tfidf(comments, forum, type):
    tfidf_list = []
    ready_input = []
    word_sentence_list = []

    # In some cases, we will encounter blank line, so we need to check whether length of a sentence > 0
    ready_input = [ sentence for comment in comments for sentence in comment.split('\n') if len(sentence) > 0 ]
    
    word_sentence_list = ws(ready_input)

    # comments_tok = [[list(jieba.cut(sentence, HMM=False)) for sentence in comment.split('\n')] for comment in comments]
    comments_tok = word_sentence_list
    
    comments_words = Counter([w for sentence in comments_tok for w in sentence if w not in stopwords])
    comments_words = {key: item for key, item in sorted(comments_words.items(), key=lambda x: x[1], reverse=True)}

    N = len([w for sentence in comments_tok for w in sentence])

    for word, count in comments_words.items():
        if word not in all_words_dict.keys() or word not in D_dict.keys() or word in stopwords:   continue
        tf = count / N
        idf = math.log((totalD / D_dict[word])) # **
        if forum_dict.get(forum):
            if forum_dict[forum].get(word): pf = forum_dict[forum][word] / all_words_dict[word]
            else: pf = 1
        else: pf = 1
        tfidf_list.append([word, tf*idf, tf*idf*pf, tf, idf, pf])
    tfidf_list.sort(key = lambda s: s[type], reverse=True)

    for word in tfidf_list:
        bi_list = []
        # for comment in comments_tok:
        for sentence in comments_tok:
            if word[0] in sentence:
                idx = sentence.index(word[0])
                if idx+1 < len(sentence) and sentence[idx+1] not in stopwords:
                    bi_list.append(sentence[idx] + sentence[idx+1])
                if idx > 0 and sentence[idx-1] not in stopwords:
                    bi_list.append(sentence[idx-1] + sentence[idx])
                if idx-2 >= 0 and sentence[idx-2] not in stopwords and sentence[idx-1] not in stopwords:
                    bi_list.append(sentence[idx-2] + sentence[idx-1] + sentence[idx])
                if idx+2 < len(sentence) and sentence[idx+1] not in stopwords and sentence[idx+2] not in stopwords:
                    bi_list.append(sentence[idx] + sentence[idx+1] + sentence[idx+2])
                if idx > 0 and idx+1 < len(sentence) and sentence[idx-1] not in stopwords and sentence[idx+1] not in stopwords:
                    bi_list.append(sentence[idx-1] + sentence[idx] + sentence[idx+1])
        bi_count = Counter(bi_list).most_common(5)
        bi_count = [word[0] for word in bi_count]
        word.append(bi_count)
    return tfidf_list

requests.packages.urllib3.disable_warnings()
cookie = '__auc=6dc9ccdd17143b13780f7882a84; __gads=ID=4a1a6db174d6b764:T=1585978677:S=ALNI_MYhw2OFmwPMXG1d6oDGLtOSaoaUBw; _gid=GA1.2.1722273152.1586581391; dcard=eyJ0b2tlbiI6bnVsbCwiX2V4cGlyZSI6MTU4OTE3NTA2NjgzNCwiX21heEFnZSI6MjU5MjAwMDAwMH0=; dcard.sig=V23CgwwWlQwERJ_4oClxCfx3eJo; dcsrd=u5srf5XIcfZBSFOWoTUlB9A1; dcsrd.sig=ILdWwvOz55JmB6jAgNThu9LMRwA; __asc=7bc8218c171681f2a3a6d824441; _gat=1; amplitude_id_bfb03c251442ee56c07f655053aba20fdcard.tw=eyJkZXZpY2VJZCI6ImU0Njc2NzQ5LTQyZWUtNDFhNS04ZWE4LTA5N2JkMzhhOWZkMlIiLCJ1c2VySWQiOiI1OTk2MDgxIiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNTg2NTg5ODA1ODU3LCJsYXN0RXZlbnRUaW1lIjoxNTg2NTg5ODIxMTk2LCJldmVudElkIjozNiwiaWRlbnRpZnlJZCI6MjIsInNlcXVlbmNlTnVtYmVyIjo1OH0=; __cfduid=d9fff663f1a6dd3065426909f15752fcb1586589920; _ga=GA1.1.2128013235.1585978618; _ga_C3J49QFLW7=GS1.1.1586589804.10.1.1586589846.0'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    # 'cookie': cookie,
    # 'X-CSRF-Token': token,
    'Connection':'close'
}
tfidf_post_keys = ['title']
tfidf_comment_keys = ['content']
dcard_api = 'https://www.dcard.tw/service/api/v2/'
retries = 3

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                        #    u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def clean(string):
    string = re.sub(r'^https?:\/\/.*[\r\n]*', '', string, flags=re.MULTILINE)
    # string = re.sub('\W+',' ', string)
    string = remove_emoji(string)
    return string

def url_to_json(url):
    for i in range(retries):
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == requests.codes.ok:
            json_file = response.json()
            response.close()
            return json_file
        elif response.status_code == 404:
            return None
        else:
            print('status error:',  response.status_code)
            continue
            # response.raise_for_status()
        response.close()
    print('EXCEED RETRIES: ', url)

def get_comment_json(post_id, total):
    url = dcard_api + 'posts/' + str(post_id) + '/comments'
    count = 0
    comments = []
    while(count < total):
        _comments = url_to_json(url + '?after=' + str(count))  # a list of dict
        if _comments is None: break
        for _comment in _comments:
            if 'content' in _comment.keys():    comments.append(clean(_comment['content']))
        count += len(_comments)
    return comments

def get_post_json(post_id):
    url = dcard_api + 'posts/' + str(post_id)
    _post = url_to_json(url) # dict
    if _post is None:
        return None
    post = {}
    if _post.get('title'):  post['title'] = _post['title']
    if _post.get('excerpt'):  post['excerpt'] = _post['excerpt']
    if _post.get('content'): post['content'] = clean(_post['content'])
    if _post.get('forumAlias'): post['forumAlias'] = _post['forumAlias']
    post['url'] = 'https://www.dcard.tw/f/' + post['forumAlias'] + '/p/' + str(post_id)
    post['comments'] = get_comment_json(post_id, _post['commentCount'])
    return post

def keywords_byID(ids):
    data_list = []
    for id in ids:
        data = get_post_json(id)
        if data == []:  return data_list
        if data == None: continue
        print(f"Searching for: {data['title']}")
        data['keyword_content'] = tfidf([data['content']], data['forumAlias'], 1)[:10]
        data['keyword_content_pf'] = tfidf([data['content']], data['forumAlias'], 2)[:10]
        data['keyword_comments'] = tfidf(data['comments'], data['forumAlias'], 1)[:30]
        data['keyword_comments_pf'] = tfidf(data['comments'], data['forumAlias'], 2)[:30]
        data_list.append(data)
    return data_list


def tfidf_byURL(urls):
    posts = []
    for url in urls:  posts.append(url.split('/')[-1])
    return keywords_byID(posts)