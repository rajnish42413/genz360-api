import time
import Checksum
import base64
import requests
import json
from collections import OrderedDict

currentTime = str(int(round(time.time() * 1000)))
MERCHANT_KEY = 'lfcHd@32T3UFN7%F'
def Payme(amount,number,order_id):
	requestData1 = '{"request":{"requestType": null,"merchantGuid":"eb88a61c-2fce-48f1-91df-89fd002694bb","merchantOrderId":'+order_id+',"salesWalletName":"PayTM","salesWalletGuid":"cefc9ead-1f79-4ba1-a308-423d1fe04264","payeeEmailId":null,"payeePhoneNumber":'+number+',"payeeSsoId":null,"appliedToNewUsers":"N","amount":'+amount+',"currencyCode":"INR","pendingDaysLimit":"0","callbackURL":"https://paytm.com/market/salesToUserCredit","cashbackPPIType":"0"},"metadata":"TestingData","ipAddress":"127.0.0.0:81","platformName":"PayTM","operationType":"SALES_TO_USER_CREDIT"}'
	
	checksum = Checksum.generate_checksum_by_str(requestData1, MERCHANT_KEY)
	
	headers = {
	'Content-Type': 'application/json',
	'mid': 'eb88a61c-2fce-48f1-91df-89fd002694bb',
	'checksumhash': checksum
	}
	
	r2 = requests.post('https://trust.paytm.in/wallet-web/asyncSalesToUserCredit', data=requestData1, headers=headers)
	return r2


def CheckStatus(order_id):
	requestData1 = '{"request":{"requestType": "merchanttxnId","txnType":"SALES_TO_USER_CREDIT","txnId": '+order_id+',"merchantGuid" : "eb88a61c-2fce-48f1-91df-89fd002694bb"},"ipAddress":"127.0.0.0:81","platformName":"PayTM","operationType":"CHECK_TXN_STATUS","channel":"","version":""}'

	checksum = Checksum.generate_checksum_by_str(requestData1, MERCHANT_KEY)
	
	headers = {
	'Content-Type': 'application/json',
	'mid': 'eb88a61c-2fce-48f1-91df-89fd002694bb',
	'checksumhash': checksum
	}
	
	r2 = requests.post('https://trust.paytm.in/wallet-web/txnStatusList', data=requestData1, headers=headers)
	return r2


def ExecutePaytmPayment(amount,number,order_id):
	res=Payme('\"'+amount+'\"','\"'+number+'\"','\"'+order_id+'\"')
	resJ=json.loads(res.text)
	return resJ

def CheckOrderStatus(order_id):
    status=CheckStatus('\"'+str(order_id)+'\"')
    check=json.loads(status.text)
    if "txnList" not in check.keys():
        return check,False
    else:
        return check["txnList"][0],True



