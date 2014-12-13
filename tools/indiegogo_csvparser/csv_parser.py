from unidecode import unidecode
import smtplib
import math
import time
import csv
import re

INDEX_EMAIL_ADDR	= 0
INDEX_NAME			= 1
INDEX_ADDR			= 2
INDEX_ADDR2			= 3
INDEX_CITY			= 4
INDEX_ZIP			= 5
INDEX_COUNTY		= 6
INDEX_COUNTRY		= 7
INDEX_ABS			= 8
INDEX_AL			= 9
INDEX_CARD			= 10
INDEX_CUSTOM_CARD	= 11
INDEX_COMMMORATIVE	= 12


def findEmailIn7cardsList(list, email):
	i = 0
	s = len(list)
	while i < s:
		if list[i] == email:
			return i;
		i += 1
	return -1
	
def findEmailInOrdersList(list, email, name, city):
	i = 0
	s = len(list)
	while i < s:
		if list[i][INDEX_EMAIL_ADDR] == email and list[i][INDEX_NAME] == name and list[i][INDEX_CITY] == city:
			return i;
		i += 1
	return -1

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	for row in csv_reader:
		yield [unidecode(unicode(cell, 'utf-8')) for cell in row]
		
if __name__ == '__main__':
	# Main function
	print ""
	print "Mooltipass backers csv parser"
	print ""
	
	# Totals
	debug_number_normal_cards = 0
	debug_number_custom_card = 0
	debug_number_com_card = 0
	debug_number_abs = 0
	debug_number_al = 0
	number_normal_cards = 0
	number_custom_card = 0
	number_com_card = 0
	number_abs = 0
	number_al = 0
	
	# Email defs	
	perk_email_sending = True
	
	# Prints defs
	raw_printout = False
	perk_printout = True
	addr_printout = True
	anomaly_printout = False
	
	# 7 more cards list
	morecards_list = []
	
	# final order list
	orders_list = list()
	
	# login mooltipass gmail account
	if perk_email_sending:
		session = smtplib.SMTP('smtp.gmail.com', 587)
		session.ehlo()
		session.starttls()
		session.login("themooltipass@gmail.com", "x")
	
	# Csv reader, 7 more cards detection loop
	reader = unicode_csv_reader(open('mooltipass.txt'))
	for contributionID, giftID, shippingstatus, backingdate, payingmean, displaystatus, name, email, amount, chosenperk, backername, backeraddress, backeraddress2, backercity, backercounty, backercitycode, backercountry in reader:
		if chosenperk == "7 more cards":
			morecards_list.append(email)

	# Csv reader, orders list
	reader = unicode_csv_reader(open('mooltipass.txt'))
	for contributionID, giftID, shippingstatus, backingdate, payingmean, displaystatus, name, email, amount, chosenperk, backername, backeraddress, backeraddress2, backercity, backercounty, backercitycode, backercountry in reader:
		# Strip the ="" in the postal code
		backercitycode = re.sub('[="]', '', backercitycode)
		numamount = re.sub('[$]', '', amount)
		# Printing the fields as is		
		if raw_printout :
			print "-------------------------------------------------"
			if chosenperk: 
				print "Chosen perk:     ", chosenperk, "-", amount
			else:
				print amount, "donation"
			print "Backer email:    ", email
			if backername:
				print "Backer name:     ", backername
			if backeraddress:
				print "Backer address:  ", backeraddress
			if backeraddress2:
				print "Backer address2: ", backeraddress2
			if backercity:
				print "Backer city:     ", backercity
			if backercounty:
				print "Backer county:   ", backercounty
			if backercitycode:
				print "Backer city code:", backercitycode
			if backercountry:
				print "Backer country:  ", backercountry
			print ""
		
		#  Do some processing and suggest the address
		if chosenperk != "" and chosenperk != "Thank you!" and chosenperk != "7 more cards":
			# chosen perk
			user_commemorative_card = 0
			user_custom_card = 0
			user_cards = 0
			user_abs = 0
			user_al = 0
			if chosenperk == "ABS Mooltipass":
				user_cards = int(math.floor((float(numamount)-100)/1.5))+2
				user_abs = 1
			elif chosenperk == "Aluminum Mooltipass":
				user_cards = int(math.floor((float(numamount)-140)/1.5))+2
				user_al = 1
			elif chosenperk == "EARLY ADOPTERS #1":
				user_cards = int(math.floor((float(numamount)-80)/1.5))+2
				user_abs = 1
			elif chosenperk == "EARLY ADOPTERS #2":
				user_cards = int(math.floor((float(numamount)-90)/1.5))+2
				user_abs = 1
			elif chosenperk == "Two ABS Mooltipass sets":
				user_cards = int(math.floor((float(numamount)-190)/1.5))+5
				user_abs = 2
			elif chosenperk == "Two Aluminum Mooltipass sets":
				user_cards = int(math.floor((float(numamount)-270)/1.5))+5
				user_al = 2
			elif chosenperk == "ABS  + Aluminum Mooltipass":
				user_cards = int(math.floor((float(numamount)-230)/1.5))+5
				user_abs = 1
				user_al = 1
			elif chosenperk == "Your very own smartcard - Al":
				user_custom_card = 1
				user_al = 1
			elif chosenperk == "Your very own smartcard - ABS":
				user_custom_card = 1
				user_abs = 1
			elif chosenperk == "Commemorative smartcard":
				user_commemorative_card = 1
			else:
				print "ERROR"
				time.sleep(1000)
							
			# Add the fields in our orders list, check if we already added the user with his address
			user_index_in_order_list = findEmailInOrdersList(orders_list, email, backername, backercity)
			if user_index_in_order_list == -1:
				# we didn't find the user in our orders list, add it
				# first, see if the user opted for the 7 more cards perk
				if findEmailIn7cardsList(morecards_list, email) != -1:
					morecards_list.pop(findEmailIn7cardsList(morecards_list, email))
					if raw_printout:
						print "user took the 7 more cards perk"
					user_cards += 7		
				orders_list.append([email, backername, backeraddress.strip(), backeraddress2.strip(), backercity, backercitycode, backercounty, backercountry, user_abs, user_al, user_cards, user_custom_card, user_commemorative_card])
			else:
				if raw_printout:
					print "user already found, adding to old order"
				orders_list[user_index_in_order_list][INDEX_ABS] += user_abs
				orders_list[user_index_in_order_list][INDEX_AL] += user_al
				orders_list[user_index_in_order_list][INDEX_CARD] += user_cards
				orders_list[user_index_in_order_list][INDEX_CUSTOM_CARD] += user_custom_card
				orders_list[user_index_in_order_list][INDEX_COMMMORATIVE] += user_commemorative_card
			
			# add the cards
			number_com_card += user_commemorative_card
			number_custom_card += user_custom_card
			number_normal_cards += user_cards
			number_abs += user_abs
			number_al += user_al
			
		else:
			# Thank you, no chosen perk...
			if int(numamount) > 10 and anomaly_printout:
				print "Atypical amount:", amount, "from", email, "-", chosenperk
				time.sleep(1)
		#time.sleep(5)
	
	# Traverse our orders list
	for order_item in orders_list:	
		# check totals
		debug_number_custom_card += order_item[INDEX_CUSTOM_CARD]
		debug_number_com_card += order_item[INDEX_COMMMORATIVE]
		debug_number_normal_cards += order_item[INDEX_CARD]
		debug_number_abs += order_item[INDEX_ABS]
		debug_number_al += order_item[INDEX_AL]
		
		# backer's perk
		printout_perk_text = ""
		if order_item[INDEX_ABS] > 0:
			printout_perk_text += repr(order_item[INDEX_ABS]) + "x ABS Mooltipass, "
		if order_item[INDEX_AL] > 0:
			printout_perk_text += repr(order_item[INDEX_AL]) + "x Aluminum Mooltipass, "
		if order_item[INDEX_CARD] > 0:
			printout_perk_text += repr(order_item[INDEX_CARD]) + " smartcards, "
		if order_item[INDEX_CUSTOM_CARD] > 0:
			printout_perk_text += repr(order_item[INDEX_CUSTOM_CARD]) + " custom cards, "
		if order_item[INDEX_COMMMORATIVE] > 0:
			printout_perk_text += repr(order_item[INDEX_COMMMORATIVE]) + " commemorative cards, "
		# remove last 2 chars
		printout_perk_text = printout_perk_text[:-2]		
		
		# chosen perk
		if perk_printout:
			print printout_perk_text
		
		# backer's address
		if addr_printout:
			temp_bool = False
			print "To:"
			print order_item[INDEX_NAME]
			# if the user just provided a street number
			if order_item[INDEX_ADDR].isdigit() or order_item[INDEX_ADDR2].isdigit():
				print order_item[INDEX_ADDR], order_item[INDEX_ADDR2]
				# address checking
				if len(order_item[INDEX_ADDR] + order_item[INDEX_ADDR2]) < 3:
					temp_bool = True
			elif order_item[INDEX_ADDR] == "-":
				print order_item[INDEX_ADDR2]
				# address checking
				if len(order_item[INDEX_ADDR2]) < 3:
					temp_bool = True
			else:
				print order_item[INDEX_ADDR]
				# address checking
				if len(order_item[INDEX_ADDR]) < 3:
					temp_bool = True
				if order_item[INDEX_ADDR2] != "" and order_item[INDEX_ADDR] != order_item[INDEX_ADDR2] and order_item[INDEX_ADDR2] != " ." and order_item[INDEX_ADDR2] != "-" and order_item[INDEX_ADDR2] != "/" and order_item[INDEX_ADDR2] != "_" and order_item[INDEX_ADDR2] != "." and order_item[INDEX_ADDR2] != "X": 
					print order_item[INDEX_ADDR2]
					# address checking
					if len(order_item[INDEX_ADDR2]) < 3:
						temp_bool = True
			print order_item[INDEX_CITY], order_item[INDEX_COUNTY], order_item[INDEX_ZIP]
			print order_item[INDEX_COUNTRY]
			print ""
			if temp_bool and False:
				time.sleep(2)
			
		# email sending
		if perk_email_sending:
			email_recipient = order_item[INDEX_EMAIL_ADDR]
			email_recipient = "x"
			email_subject = "[Mooltipass Campaign] Your Selected Perk - Do You Want To Make Any Change?"
			body_of_email = "Dear " + order_item[INDEX_NAME] + ",<br><br><br>"
			body_of_email += "The Mooltipass team would like to <b>thank you</b> for backing its campaign and making the Mooltipass a reality.<br>"
			body_of_email += "We're sending you this email so you can check that we <b>correctly registered your pledge</b> and give you the opportunity to <b>make an addition to it</b>.<br><br>"
			body_of_email += "You have selected: <u>" + printout_perk_text + "</u><br><br>"
			body_of_email += "If this isn't correct or if you want to add anything to your order (another Mooltipass, smartcard, etc...), please <b>reply to this email</b> to let us know.<br>"
			body_of_email += "Thanks again for your support,<br>"
			body_of_email += "The Mooltipass development team"
			headers = "\r\n".join(["from: " + "themooltipass@gmail.com",
					   "subject: " + email_subject,
					   "to: " + email_recipient,
					   "mime-version: 1.0",
					   "content-type: text/html"])

			# body_of_email can be plaintext or html!                    
			content = headers + "\r\n\r\n" + body_of_email
			session.sendmail("themooltipass@gmail.com", email_recipient, content)
			time.sleep(2)
	
	print "-------------------------------------------------"
	print "Total number of ABS:", number_abs, "- check: ", debug_number_abs
	print "Total number of Al:", number_al, "- check: ", debug_number_al
	print "Total number of custom cards:", number_custom_card, "- check: ", debug_number_custom_card
	print "Total number of normal cards:", number_normal_cards, "- check: ", debug_number_normal_cards
	print "Total number of commemorative cards:", number_com_card, "- check: ", debug_number_com_card