#service=type of service (1 to 6)
#n = number of influencers
#f = number of followers
#ttype 1 = PAN INDIA   (contains 6 services)
#ttype 2 = REGIONAL    (contains 2 services)

imf=0       #store impression multiplying factor for 1 influencer
cmf=0       #store cost multiplying factor for 1 influencer
pmf=0       #store payout multiplying factor for 1 influencer
estimp=0
netcost=0
netpayout=0
def calc_price(ttype,service, n, f):
#----------PAN INDIA START HERE----------
    if ttype==1:
        if service==1:   #BRAND AWARENESS
            if(f>=100 and f<=500):
                imf=200
                cmf=75
                pmf=20
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=100
                pmf=40
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost

        if service==2:      #EVENT PROMOTION
            if(f>=100 and f<=500):
                imf=200
                cmf=85
                pmf=20
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=120
                pmf=40
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost

        if service==3:      # UGC TEXT
            if(f>=100 and f<=500):
                imf=200
                cmf=150
                pmf=50
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=200
                pmf=70
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost

        if service==4:      # VIRAL MARKETING
            if(f>=100 and f<=500):
                imf=200
                cmf=100
                pmf=35
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=150
                pmf=60
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost

        if service==5:      # PERFORMANCE BASED PRODUCTION
            if(f>=100 and f<=500):
                imf=200
                cmf=30
                pmf=15
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=45
                pmf=20
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost

        if service==6:      # UGC VIDEO
            if(f>=100 and f<=500):
                imf=200
                cmf=600
                pmf=200
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=700
                pmf=275
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost

#--------------REGIONAL START HERE--------------
    elif ttype==2:
        if service==1:          # BRAND AWARENESS
            if(f>=100 and f<=500):
                imf=200
                cmf=100
                pmf=20
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=150
                pmf=40
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost

        if service==2:          # EVENT PROMOTION
            if(f>=100 and f<=500):
                imf=200
                cmf=100
                pmf=20
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            elif(f>=501):
                imf=375
                cmf=150
                pmf=40
                estimp=n*imf
                netcost=n*cmf
                netpayout=n*pmf
            gross_margin=netcost-netpayout
            gross_percent=gross_margin*100/netcost
    return {'estimp':estimp,"netcost":netcost,'netpayout':netpayout,'gross_margin':gross_margin,'gross_percent':gross_percent}
