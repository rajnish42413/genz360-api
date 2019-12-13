#!/usr/bin/python

import Checksum
import requests
import base64
import json
print("Content-type: text/html\n")
 

MERCHANT_KEY = 'ZxW2xIGSt7NK5Zmb';
data_dict = {
            'MID':'Studen81446331199922',
            'ORDER_ID':'genz_order_5',
            'TXN_AMOUNT':'1',
            'CUST_ID':'manish.1610086@kiet.edu',
            'INDUSTRY_TYPE_ID':'Retail',
            # 'WEBSITE':'worldpressplg',
            'CHANNEL_ID':'WEB',
	    'CALLBACK_URL':'https://studentingera.com/paytm-status.php',
        }
# headers = {
# 	'Content-Type': 'application/json',
# 	'mid': 'Studen81446331199922',
# 	'checksumhash': checksum
# 	}

param_dict = data_dict  
param_dict['CHECKSUMHASH'] =Checksum.generate_checksum(data_dict, MERCHANT_KEY)
# def exe():
#     r2 = requests.post('https://securegw.paytm.in/order/process', data=param_dict, headers=headers)
#     return r2

for key in param_dict:
    print(key.strip()+param_dict[key].strip())

print('<h1>Merchant Check Out Page</h1></br>')
print('<form method="post" action="https://securegw.paytm.in/order/process" name="f1">')
for key in param_dict:
    print('<input type="hidden" name="'+key.strip()+'"value="'+param_dict[key].strip()+'">')
print('<script type="text/javascript">')
print('document.f1.submit();')
print('</script>')
print('</form>')