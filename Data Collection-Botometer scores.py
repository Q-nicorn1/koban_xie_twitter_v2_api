#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas as pd
import time


# ### 1. Set the `BEARER_TOKEN` variable to your developer bearer token.

# In[2]:


token = '****'
os.environ["BEARER_TOKEN"] = token


# ### 2. Get 20 samples of screen name 

# In[3]:


seed_accounts =  pd.read_csv('data/seed_accounts.csv')
seed_accounts = seed_accounts['screen_name'].tolist()


# In[9]:


get_ipython().system('pip install botometer')

import botometer


rapidapi_key = "****"
twitter_app_auth = {
    'consumer_key': '****',
    'consumer_secret': '****',
    'access_token': '****',
    'access_token_secret': '****',
    }
bom = botometer.Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)


# In[8]:


#check a single accout to see if it works
result = bom.check_account('@mcfunny')
result


# In[10]:


seed_accounts = seed_accounts[0:5]


# In[14]:


#Query the multiple sample accounts Botometer scores

botometer_full = []
i = 0
for screen_name in seed_accounts :
    i+=1
    try:
        result = bom.check_account(seed_accounts)            
        temp = pd.DataFrame(result)
        temp = pd.DataFrame({'id_str': [temp['user']['user_data']['id_str']],
                             'screen_name': [temp['user']['user_data']['screen_name']],
                             'cap_en': [temp['cap']['english']],
                             'cap_un': [temp['cap']['universal']],

                             'astroturf_raw_en': [temp['raw_scores']['english']['astroturf']],
                             'fake_follower_raw_en': [temp['raw_scores']['english']['fake_follower']],
                             'financial_raw_en': [temp['raw_scores']['english']['financial']],
                             'other_raw_en': [temp['raw_scores']['english']['other']],
                             'overall_raw_en': [temp['raw_scores']['english']['overall']],
                             'self_declared_raw_en': [temp['raw_scores']['english']['self_declared']],
                             'spammer_raw_en': [temp['raw_scores']['english']['spammer']],

                             'astroturf_display_en': [temp['display_scores']['english']['astroturf']],
                             'fake_follower_display_en': [temp['display_scores']['english']['fake_follower']],
                             'financial_display_en': [temp['display_scores']['english']['financial']],
                             'other_display_en': [temp['display_scores']['english']['other']],
                             'overall_display_en': [temp['display_scores']['english']['overall']],
                             'self_declared_display_en': [temp['display_scores']['english']['self_declared']],
                             'spammer_display_en': [temp['display_scores']['english']['spammer']],

                             'astroturf_raw_un': [temp['raw_scores']['universal']['astroturf']],
                             'fake_follower_raw_un': [temp['raw_scores']['universal']['fake_follower']],
                             'financial_raw_un': [temp['raw_scores']['universal']['financial']],
                             'other_raw_un': [temp['raw_scores']['universal']['other']],
                             'overall_raw_un': [temp['raw_scores']['universal']['overall']],
                             'self_declared_raw_un': [temp['raw_scores']['universal']['self_declared']],
                             'spammer_raw_un': [temp['raw_scores']['universal']['spammer']],

                             'astroturf_display_un': [temp['display_scores']['universal']['astroturf']],
                             'fake_follower_display_un': [temp['display_scores']['universal']['fake_follower']],
                             'financial_display_un': [temp['display_scores']['universal']['financial']],
                             'other_display_un': [temp['display_scores']['universal']['other']],
                             'overall_display_un': [temp['display_scores']['universal']['overall']],
                             'self_declared_display_un': [temp['display_scores']['universal']['self_declared']],
                             'spammer_display_un': [temp['display_scores']['universal']['spammer']]
                     })
        print(i)
        timestr = time.strftime("%m%d%Y_%H%M")
        temp.to_csv('/Users/nicole92xie/Documents/' + str(screen_name) + timestr + ".csv")
        botometer_full.append(temp)

    except:
        pass
    
data = pd.concat(botometer_full)

