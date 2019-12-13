from flask import Flask,render_template
from models import *
from init import *


#84,
#454,121
#gzb,gurugram,

def get_locationid():
    alll=Location.query.all()
    l2=[]
    for i in alll:
        l2.append(i.location_id)
    l2.remove(454)
    l2.remove(121)
    l2.remove(84)
    print(l2)
    return l2
    

def abc1():
    all=Influencer_details.query.all()
    l1=[84,454,121]
    l2=get_locationid()
    # for i in range(int(len(all)*0.6)):
    #     x=random.randint(0,len(all)-1)
    #     y=random.randint(0,2)
    #     # all[x].location=l1[y]
    #     l=Location.query.filter_by(location_id=l1[y]).first()
    #     l.influencers.append(all[x])

    # for i in range(len(all)):
    #     x=random.randint(0,len(all)-1)
    #     y=random.randint(0,len(l2)-1) 
    #     if all[i].location==None:
    #         # all[i].location=l2[y]
    #         l=Location.query.filter_by(location_id=l2[y]).first()
    #         l.influencers.append(all[x])
            
    for i in range(int(len(all)*0.3)):
        x=random.randint(0,len(all)-1)
        y=random.randint(0,len(l2)-1) 
        # all[i].location=l2[y]
        l=Location.query.filter_by(location_id=l2[y]).first()
        l.influencers.append(all[x])
    return "DONE"

x=abc1()
print(x)