# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 20:49:47 2019
@author: Volition
"""
#The psaw scraps comments from the latest to the earliest. Therefore save all the dates of the comments as it scraps through, then 
#if it finds a comment that is earlier (number is less than) than the latest comment, break the loop.
#find a comment that is the latest in the last time it is scrapped

'''Fixed comment tracking bug
Fixed flair system
Fixed flair system when there is no editable flairs
'''
'''
Note that flairs take some time to appear(around 10 minutes)
Note that flairs can only have a maximum of 64 characters.
'''
import praw, re, html
from psaw import PushshiftAPI
from praw.exceptions import APIException

number_of_comments = 200
time_before = '120d'
#number of already posted comments detected before it stops searching
comment_threshold = 30

def prawapi():
    REDDIT_USERNAME = 'USERNAME'
    REDDIT_PASSWORD = 'PASSWORD'
    CLIENT_ID = 'CLIENTID'
    CLIENT_SECRET = 'CLIENTSECRET'
    username = REDDIT_USERNAME
    password = REDDIT_PASSWORD
    reddit = praw.Reddit(client_id=CLIENT_ID,
                             client_secret=CLIENT_SECRET,
                             user_agent='blizz',
                             username=username,
                             password=password)
    return reddit
class ThreadToSubmit:
    def __init__(self, subreddit_out, submit_string, title, flair):
        self.subreddit_out = subreddit_out
        self.submit_string = submit_string
        self.title = title
        self.flair = flair
        
def get_title(comment):
    comment_id = re.search(r'/....../', comment.permalink).group()
    submission1 = reddit.submission(comment_id[1:7])    
    return (submission1.title)
def insert_quote(string):
    new=''
    for line in string.splitlines():
        new+= '\n>'+line
    return new

def pushshiftapi(authors_list,subreddit_in, time_before, limit):
    '''input a list of authors to search through and returns a generator object of comments'''
    api = PushshiftAPI()
    a=api.search_comments(after=time_before,
                          author=authors_list,
                            subreddit=subreddit_in,
                          filter=['permalink','author','parent_id','body','id','url'],
                            limit=limit,
                            date='desc')
    return a

def insert_flair(flair, submission_out_id):
    #Ensure that the flair length is below 64
    while len(flair) >64:
        comma_index = flair.rfind(',')
        flair = flair[:comma_index]    
    submission_out = reddit.submission(submission_out_id)
    #select the first editable flair text
    flair_choices = submission_out.flair.choices()
    print(flair_choices)
    flair_id = ''
    for i in flair_choices:
        if i['flair_text_editable'] == True:
            flair_id = i['flair_template_id']
            break
    #if flair exists then add it
    if flair_id != '':
        submission_out.flair.select(flair_id, flair)
    else:
        print("\nFlairs are not editable in this subreddit, remember to tick the box next to the (link flair templates  user can edit?) column")
    #if all not true, raise an error saying that since flairs are not editable, they are not added
    
    
def scrape_and_post_blizz(subreddit_in, subreddit_out, blizz_dict):
    blizz_list = [*blizz_dict]
    comments = pushshiftapi(blizz_list, subreddit_in, time_before , number_of_comments)
    threadToSubmit_dict={}
    comments_posted=0
    commentid_list = []
    for comment in comments:
        # if there are more than 20 of the comments already posted, break the loop.
        comment_body = html.unescape(comment.body)
        f=open ('repliedto.txt','r', encoding='UTF-8')
        if not hasattr(comment, 'body'):
            continue
        if comment.author in blizz_list:
            if comment.id in f.read():
                f.close()
                comments_posted +=1
                if comments_posted == comment_threshold:
                    break
                continue
            f.close()            
            submit_list=[]
            parent_id = comment.parent_id
            commentid_list.append(comment.id)
            print(comment.author)
            if parent_id[:3] == 't3_':
                #if parent is a submission
                parent_id = parent_id[3:]
                parent = reddit.submission(parent_id)
                if parent.is_self:
                    parent_selftext = insert_quote(parent.selftext)
                    #print("#" + parent.title)
                    #submit_list.append("#" + parent.title)
                    print(parent_selftext)
                    submit_list.append(parent_selftext)
                    print(comment_body)
                    submit_list.append(comment_body)
                    print("#"+blizz_dict[comment.author]+"([" + " link to comment"+"]("+comment.permalink+"))")
                    submit_list.append("#"+blizz_dict[comment.author]+"[" + " (link to comment)"+"]("+comment.permalink+")")
                else:
                    print("#[" + parent.title+"]("+parent.url+")")
                    submit_list.append("#[" + parent.title+"]("+parent.url+")")
                    print(comment_body)
                    submit_list.append(comment_body)
                    print("#"+blizz_dict[comment.author]+"([" + " link to comment"+"]("+comment.permalink+"))")
                    submit_list.append("#"+blizz_dict[comment.author]+"[" + " (link to comment)"+"]("+comment.permalink+")")
            else:
                #if parent is comment
                if parent_id[:3] == 't1_':
                    parent_id = parent_id[3:]
                parent = reddit.comment(parent_id)
                try:
                    parent_body = html.unescape(parent.body)
                    parent_body = insert_quote(parent_body)
                    print(parent_body)
                    submit_list.append(parent_body)
                    print(comment_body)
                    submit_list.append(comment_body)
                    print("#"+blizz_dict[comment.author]+"([" + " link to comment"+"]("+comment.permalink+"?context=2"+"))")
                    submit_list.append("#"+blizz_dict[comment.author]+"[" + " (link to comment)"+"]("+comment.permalink+")")
                except:
                    print(comment_body)
                    submit_list.append(comment_body)
                    print("#"+blizz_dict[comment.author]+"([" + " link to comment"+"]("+comment.permalink+"?context=2"+"))")
                    submit_list.append("#"+blizz_dict[comment.author]+"[" + " (link to comment)"+"]("+comment.permalink+")")
            title=get_title(comment)
            submit_string= '\n\n'.join(submit_list)
            if title in threadToSubmit_dict:
                threadToSubmit_dict[title].submit_string = threadToSubmit_dict[title].submit_string +'\n-----------\n'+ submit_string
                if blizz_dict[comment.author] not in threadToSubmit_dict[title].flair:
                    threadToSubmit_dict[title].flair += ", " + blizz_dict[comment.author]
                    
                    
                    
                
            else:
                threadToSubmit_dict[title]=ThreadToSubmit(subreddit_out=subreddit_out,submit_string=submit_string,title=title, flair=blizz_dict[comment.author])
        

                

        
    for i in threadToSubmit_dict:
        try:
            subreddit_outobject = reddit.subreddit(threadToSubmit_dict[i].subreddit_out)
            submission_out_id = subreddit_outobject.submit(title=threadToSubmit_dict[i].title,selftext=threadToSubmit_dict[i].submit_string)
            print(threadToSubmit_dict[i].submit_string)
            print(threadToSubmit_dict[i].flair,submission_out_id)
            insert_flair(threadToSubmit_dict[i].flair, submission_out_id)

        except APIException:
            #creates an error file when the body exceeds 40 000 characters for bugfixing
            print("Body exceeds 40000 characters")
            print("Body:")
            print(threadToSubmit_dict[i].submit_string)
            with open ('warning.txt','w', encoding='UTF-8') as f:
                f.write(threadToSubmit_dict[i].submit_string)
            input()
            
            
    #writes all the comments which have been posted 
    with open('repliedto.txt', 'a', encoding='UTF-8') as f: 
        f.write(" ".join(commentid_list) + " ") 
        
        
reddit = prawapi()
blizz_hs_dict={'HS_Liv': 'HS_Liv (Initial Designer)', 'jdurica': 'jdurica (Gameplay Engineer)', 'TroldenHS': 'TroldenHS (Community Manager, Russia)', 'puffinplays': 'puffinplays (Associate Game Designer)', 'LegendaryFerret': 'LegendaryFerret (Designer)', 'IksarHS': 'IksarHS (Game Designer)', 'Araxom': 'Araxom (Customer Support)', 'CM_Daxxarri': 'CM_Daxxarri (Community Manager)', 'TheFargo': 'TheFargo (Game Designer)', 'Kalviery': 'Kalviery (Customer Support)', 'Hadidjahb': 'Hadidjahb (FX Artist)', 'mdonais': 'mdonais (Principal Game Designer)', 'Dalthrox': 'Dalthrox (Customer Support)', 'Realz-': 'Realz- (Game Designer)', 'CS_Scout': 'CS_Scout (Customer Support)'}
blizztracker_wow_dict={'Araxom': 'Araxom (Customer Support)', 'CM_Ythisens': 'CM_Ythisens', 'Dmachine_Blizz': 'Dmachine_Blizz (Esports Coordinator)', 'Kalviery': 'Kalviery', 'Dromogaz': 'Dromogaz (Customer Support)', 'World': 'World of Warcraft | AMA', 'Kaivax': 'Kaivax (Randy Jordan (Community Manager))', 'CS_Scout': 'CS_Scout'}
blizztracker_sc_dict={'Araxom': 'Araxom', 'Arkitas': 'Arkitas', 'Traysent': 'Traysent ', 'Khalmanac': 'Khalmanac ', 'psione': 'psione (Axiom)', 'Savirrux': 'Savirrux', 'CS_Scout': 'CS_Scout', 'cloaken': 'cloaken (Axiom)', 'Starcraft': 'Starcraft | Araxom'}
blizztracker_ow_dict={'Araxom': 'Araxom (Customer Support)', 'BillWarnecke': 'BillWarnecke (Lead Software Engineer)', 'HowieYoo': 'HowieYoo (Senior Software Engineer)', 'Blizz_JeffKaplan': 'Blizz_JeffKaplan (Game Director)', 'CS_Scout': 'CS_Scout (Customer Support)', 'Blizz_MichaelChu': 'Blizz_MichaelChu (Lead Writer)', 'Blizz_Andreas': 'Blizz_Andreas (Customer Support)', 'Blizz_Josh': 'Blizz_Josh (Community Manager)'}
blizztracker_heroes_dict={'Blizz_AKlontzas': 'Blizz_AKlontzas', 'Blizz_Daybringer': 'Blizz_Daybringer (Live Game Designer)', 'cloaken': 'cloaken', 'Ustovar': 'Ustovar', 'Araxom': 'Araxom', 'Blizz_KinaBREW': 'Blizz_KinaBREW (3D Artist)', 'Blizz_Joe': 'Blizz_Joe ( - Lead Systems Designer)', 'Heroes': 'Heroes of the Storm | AMA', 'BlizzAZJackson': 'BlizzAZJackson (Live Game Designer)', 'Blizz_LanaB': 'Blizz_LanaB ( - Animator)', 'BlizzMattVi': 'BlizzMattVi (Lead Hero Designer)', 'Ravinix': 'Ravinix', 'BlizzNeyman': 'BlizzNeyman (Live Game Designer)', 'BlizzJohnny': 'BlizzJohnny'}
scrape_and_post_blizz('hearthstone', 'hsblizztracker', blizz_hs_dict)
scrape_and_post_blizz('overwatch', 'owblizztracker', blizztracker_ow_dict)
scrape_and_post_blizz('starcraft', 'scblizztracker', blizztracker_sc_dict)
scrape_and_post_blizz('wow', 'wowblizztracker', blizztracker_wow_dict)
scrape_and_post_blizz('heroesofthestorm', 'heroesblizztracker', blizztracker_heroes_dict)
