# -*- coding: utf-8 -*-

from tqdm import tqdm


podcast_urls = ['https://feeds.pacific-content.com/commandlineheroes',
                'http://feeds.codenewbie.org/cnpodcast.xml',
                'http://feeds.codenewbie.org/basecs_podcast.xml',
                'https://cppcast.com/episode/index.xml',
                'https://feeds.simplecast.com/gvtxUiIf',
                'https://lexfridman.com/category/ai/feed']


# Now we write a function to get the feed information for the links. We use a handy Python library called `feedparser` which reads a link and returns a giant `dict` of all the information contained in the xml file.

# In[7]:


#import sys
#get_ipython().system('conda install --yes --prefix {sys.prefix} feedparser wget')


# In[22]:


def get_feed_info(url):
    import feedparser
    
    feed_info = feedparser.parse(url)
    title = feed_info['feed']['title_detail']['value']
    entries = feed_info['entries']
    feed_episodes = [dict(title=f['title'], url=f['links'][1]['href']) for f in entries]
    return dict(feed_title=title, feed_episodes=feed_episodes)


# Lets test this function.

# In[23]:


#print(get_feed_info(podcast_urls[0]))


# That seems to be right. Lets move on and create a global data structure for all such feed. Now we need to iterate over the urls and collect them in a single `dict`.

# In[24]:


def get_all_podcasts(urls):
    feeds = []
    for u in tqdm(urls):
        feeds.append(get_feed_info(u))

    return feeds



# Now we create a few functions to search in podcast titles and episode titles

# In[58]:


def search_podcast(podcasts, term=None):
    import re
    
    if not term:
        # Match everything if searching for nothing specific
        return podcasts
   
    term = re.escape(term)

    return [p for p in podcasts if re.match('''.*{}.*'''.format(str(term)), p['feed_title'], re.IGNORECASE)]

def search_episode_in_feed(feeds, term=None):
    import re
    
    if not term:
        # Match everything if searching for nothing specific
        return feeds
   
    term = re.escape(term)

    return [f for f in feeds if re.match('''.*{}.*'''.format(str(term)), f['title'], re.IGNORECASE)]

def search_episode_in_podcast(p, term=None):
    return search_episode_in_feed(p['feed_episodes'], term)

def search_episode_in_all_podcasts(ps, term=None):
    feeds = [search_episode_in_podcast(p, term) for p in ps]
    all_feeds = []
    for fs in feeds:
        for f in fs:
            all_feeds.append(f)
    return all_feeds


# Ok so time for testing. We will first search for "command line" and if we get a podcast then search for "war" in it.

# In[60]:


#pl = search_podcast(podcasts, "command line")
#feeds = search_episode_in_all_podcasts(pl, "war")
#print(feeds)


# Ok! Now lets make a function to get the podcast and play it. We will use `open` command for a OSX for now. Later we shall customize it for other OSs. 

# In[64]:


def wget_episode(ep):
    import wget
    import os.path
    
    file_name = wget.detect_filename(ep['url'])
    
    if os.path.exists(file_name):
        print('... file already downloaded')
        return file_name
    
    file_name = wget.download(ep['url'], bar=wget.bar_adaptive)
    return file_name

def open_episode(path):
    import os
    import platform
    import subprocess

    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# Testing time. We will now play war part1.

# In[67]:


#feeds = search_episode_in_all_podcasts(search_podcast(podcasts, "command line"), "wars_part 2")
#
#if len(feeds) == 1:
#    print("getting file")
#    file = wget_episode(feeds[0])
#    print(file)
#    print("now playing")
#    open_episode(file)
#else:
#    print('Bad number of fields, need only one!')


# In[ ]:

def repl(urls):
    import re
    import pydoc
    
    def pager_print(options):
        text = ''
        i = 1
        
        for o in options:
            text += ' {}.\t{}\n'.format(i, str(o))
            i += 1
            
        pydoc.pager(text)
    
    podcasts = get_all_podcasts(urls)
    
    print('''
       Commands
       sp [string] -> search a podcast by name
       selp <num> -> select a podcast
       se [string] -> search an episode in selected podcast by name
       sele <num> -> select episode (and play)
       q -> quit
    ''')
    
    selected_podcasts = podcasts
    selected_episodes = search_episode_in_all_podcasts(selected_podcasts)
    podcast_num = None
    
    while True:
        if podcast_num and (podcast_num - 1 >= 0 and podcast_num - 1 < len(selected_podcasts)):
            pod_message = selected_podcasts[podcast_num - 1]['feed_title']
        else:
            pod_message = 'No podcase selected'

        command = input('[{}] >> '.format(pod_message))
        
        if command == 'q':
            break
        
        command_parts = re.compile('''\s+''').split(command)
        
        if len(command_parts) == 0:
            print('Sorry, try again!')
            continue
        
        command_head = command_parts[0]
        command_arg = ' '.join(command_parts[1:])
        
        if command_head == 'sp':
            selected_podcasts = search_podcast(podcasts, command_arg)
            pager_print([p['feed_title'] for p in selected_podcasts])
        elif command_head == 'se':
            if podcast_num is None:
                selected_episodes = search_episode_in_all_podcasts(podcasts, command_arg)
            else:
                if podcast_num - 1 >= 0 and podcast_num - 1 < len(selected_podcasts):
                    selected_episodes = search_episode_in_podcast(selected_podcasts[podcast_num - 1], command_arg)
            pager_print([e['title'] for e in selected_episodes])
        elif command_head == 'selp':
            try:
                podcast_num = int(command_arg)
            except:
                print('Could not set podcast number')
        elif command_head == 'sele':
            if selected_episodes:
                try:
                    episode_num = int(command_arg)
                except:
                    print('Unable to determine episode number, selecting latest one')
                    episode_num = 1
            else:
                print('Select an episode first')
                continue
            
            if episode_num - 1 >= 0 and episode_num - 1 < len(selected_episodes):
                episode = selected_episodes[episode_num - 1]
                print('Playing...{}'.format(episode['title']))
                file = wget_episode(episode)
                open_episode(file)
        print()


if __name__ == '__main__':
    repl(podcast_urls)

                
                
                
                
                
