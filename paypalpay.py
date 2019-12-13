import paypalrestsdk
import logging

paypalrestsdk.configure({
  "mode": "live", # sandbox or live
  "client_id": "AZ6WnnntHRz9r4O9VFBVV2jvk1x5CWkotOF3WKGL1HIFyeDjNq57H-BMoZECcc63oeJh1VTMpSSghAnj",
  "client_secret": "EBp-kZsfSpz6at9KC-6zM0wiWV4Jby-f8b3dllj3uYmgEDZSdawIh1_MQe_d8RGRTWw9GVHxNCwL8RmV" })


def Createpaypalpayment(item="item",amount=0.0,desc=''):
	payment = paypalrestsdk.Payment({
		"intent": "sale",
		"payer": {
			"payment_method": "paypal"},
		"redirect_urls": {
			"return_url": "http://www.genz360.com:81/payment/paypal/success",
			"cancel_url": "http://www.genz360.com:81/payment/paypal/failed"},
		"transactions": [{
			"item_list": {
				"items": [{
					"name": "item",
					"sku": "item",
					"price": str(amount),
					"currency": "INR",
					"quantity": 1}]},
			"amount": {
				"total": amount,
				"currency": "INR"},
			"description": desc}]})
	if payment.create():
		print(payment)
		for link in payment.links:
			if link.rel == "approval_url":
				approval_url = str(link.href)
				return approval_url,payment
	else:
		return str(payment.error)

def Executepayment(pid,payid):
	payment = paypalrestsdk.Payment.find(payid)
	if payment.execute({"payer_id": pid}):
		return "Payment execute successfully"
	else:
		return payment.error