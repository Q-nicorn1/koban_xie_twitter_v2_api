import requests
import os
import json
import pandas as pd
import math

def get_users(usernames): 
    """Query a user screen name for profile information.

    Args:
        usernames: list of user screen names to query
    Returns:
        Dataframe of profile information (user_id, username, name, description, location, created_at, followers_count, following_count, tweet_count, listed_count).    

    """
    # authenticate with end point
    bearer_token = os.environ.get("BEARER_TOKEN")    
    
    # generate query string
    if type(usernames) != list:
        usernames_qterm = 'usernames=' + usernames
    else:
        usernames_qterm = 'usernames=' + ','.join(usernames)    
    user_fields = "user.fields=description,created_at,entities,id,location,name,public_metrics,url,username,verified"
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames_qterm, user_fields)
    
    # submit GET request - submit a query to the API      
    response = requests.request("GET", url, 
                                headers = {"Authorization": "Bearer {}".format(bearer_token)})   
    
    # parse the json response into a dataframe
    users = pd.DataFrame(response.json()['data'])
    users['followers_count'] = users['public_metrics'].apply(lambda x: x['followers_count'])
    users['following_count'] = users['public_metrics'].apply(lambda x: x['following_count'])
    users['tweet_count'] = users['public_metrics'].apply(lambda x: x['tweet_count'])
    users['listed_count'] = users['public_metrics'].apply(lambda x: x['listed_count'])
    users = users.rename(columns = {'id':'user_id'})
    
    # error handling to prevent failing when columns are missing in the json response
    empty_df = pd.DataFrame({'user_id': [], 'username': [],'name': [],'description': [], 
                             'location': [],'created_at': [],'followers_count': [],'following_count': [],
                             'tweet_count': [],'listed_count': []})
    users = pd.concat([empty_df, users])
    
    users = users[['user_id','username','name','description','location','created_at','followers_count','following_count','tweet_count','listed_count']]    
    return users 

def get_user_activity_simple(username, token = 0):
    # authenticate with end point
    bearer_token = os.environ.get("BEARER_TOKEN")
    
    # query profile info to get a user_id
    user_info = get_users(username)
    user_id = user_info['user_id'][0]
    
    # generate query string
    # https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
    if token == 0: 
        url =  'https://api.twitter.com/2/users/' + user_id + '/tweets?tweet.fields=conversation_id,in_reply_to_user_id,created_at,author_id,entities,public_metrics,geo,lang,referenced_tweets&max_results=5'
    else:
        url =  'https://api.twitter.com/2/users/' + user_id + '/tweets?tweet.fields=conversation_id,in_reply_to_user_id,created_at,author_id,entities,public_metrics,geo,lang,referenced_tweets&max_results=100&pagination_token=' + token    
    
    # submit GET request - submit a query to the API      
    response = requests.request("GET", url, 
                                headers = {"Authorization": "Bearer {}".format(bearer_token)})   
    
    return response.json()

def check_token(response):
    try:
        next_token = response['meta']['next_token']
    except:
        next_token = "complete"
                
def update_status(last_request):
    if check_token(response = last_request) == "complete":
        status = "done"
    else:
        status = "keep_going"   
    return status

def get_user_activity0(username, record_count = 10): 
    """Query a user screen name for timeline activity

    Args:
        usernames: user screen names to query
        record_count: a number specifying how many records to return; maximum of 2500, minimum of 5
        
    Returns:
        Dataframe of user activity.    

    """
    # authenticate with end point
    bearer_token = os.environ.get("BEARER_TOKEN")
    
    user_info = get_users(username)
    user_id = user_info['user_id'][0]
    
    # generate query string
    if record_count <= 100:
        first_request = get_user_activity_simple(username, token = 0)
        print("first record check ")     
    else:
        first_request = get_user_activity_simple(username, token = 0)        
        status = "keep_going"
    
    try: 
        next_token = first_request['meta']['next_token']              
        tweet_dfs = []
        batch_count = math.ceil(record_count/100)
        n = 1  
        
        while (status != "done") & (n <= batch_count):
            status = update_status(last_request = first_request)
            
            while (status != "done") & (n <= batch_count):
                resp = get_user_activity_simple(username, token = next_token)
                print("token: " + next_token) 
                tweet_dfs.append(resp)
                status = update_status(last_request = resp)                  
                n += 1
                try: 
                    next_token = resp['meta']['next_token']
                except:
                    token = "done"
                    status = 'done'         
            
        # combine results into a single dataframe
        activity = []           
        for i in range(0, len(tweet_dfs)):
            activity.append(pd.DataFrame(tweet_dfs[i]['data']))
        activity = pd.concat(activity)
        activity = activity        
    
    except:
        activity = pd.DataFrame(first_request['data'])        
    
    return activity

def get_user_activity(usernames, record_count = 10): 
    activity = [pd.DataFrame()]
    for username in usernames:
        activity.append(get_user_activity0(username, record_count = record_count))
    activity = pd.concat(activity)
    activity.reset_index(inplace = True, drop = True)
    return activity

def extract_el(data):
    hashtag_el = [pd.DataFrame({'author_id':[], 'status_id': [], 'hashtag': []})]
    for k in range(0, len(data)):       
        try: 
            hashtags = pd.json_normalize(data['entities'][k]['hashtags'])['tag'].tolist()
            el = pd.DataFrame({'hashtag': hashtags})
            el['author_id'] = data['author_id'][k]
            el['status_id'] = data['id'][k]
            el = el[['author_id', 'status_id', 'hashtag']]
            hashtag_el.append(el)
        except:
            pass
        
    hashtag_el = pd.concat(hashtag_el)
    hashtag_el.reset_index(drop = True, inplace = True)
    hashtag_el['edge_type'] = 'hashtag'
        
    mention_el = [pd.DataFrame({'author_id':[], 'status_id': [], 'mentioned_user': []})]
    for k in range(0, len(data)):       
        try: 
            mentioned_user = pd.json_normalize(data['entities'][k]['mentions'])['username'].tolist()
            el = pd.DataFrame({'mentioned_user': mentioned_user})
            el['author_id'] = data['author_id'][k]
            el['status_id'] = data['id'][k]
            el = el[['author_id', 'status_id', 'mentioned_user']]
            mention_el.append(el)
        except:
            pass
            
    mention_el = pd.concat(mention_el)
    mention_el.reset_index(drop = True, inplace = True)
    mention_el['edge_type'] = 'mention'

    url_el = [pd.DataFrame({'author_id':[], 'status_id': [], 'url': []})]
    for k in range(0, len(data)):       
        try: 
            mentioned_user = pd.json_normalize(data['entities'][k]['urls'])['url'].tolist()
            el = pd.DataFrame({'url': mentioned_user})
            el['author_id'] = data['author_id'][k]
            el['status_id'] = data['id'][k]
            el = el[['author_id', 'status_id', 'url']]
            url_el.append(el)
        except:
            pass
            
    url_el = pd.concat(url_el)
    url_el.reset_index(drop = True, inplace = True)
    url_el['edge_type'] = 'url'
    
    el = pd.concat([hashtag_el, mention_el, url_el])
    el.reset_index(drop = True, inplace = True)

    return el