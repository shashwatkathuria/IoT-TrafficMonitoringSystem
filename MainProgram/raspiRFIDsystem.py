# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 14:15:23 2020
@author: Shashwat Kathuria
"""

# Traffic Penalty Raspberry Pi 3B RFID System
# RFID-MFRC522

# Importing required libraries
import requests, json, datetime
from getpass import getpass
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()

# Cleaning up GPIO previous settings
GPIO.cleanup()
GPIO.setwarnings(False)

# Initializing urls
baseUrl = "https://traffic-penalty-system-sk17.herokuapp.com/"
getPenaltiesUrl = "getpenalties"
submitPenaltyUrl = "submitpenalty"
payPenaltyUrl = "paypenalty"
loginUrl = "login"

# Initializing penalty types
penaltyTypes = {
    1: ["Red Light Skip", 2000],
    2: ["Accident", 1500],
    3: ["Seat Belt Violation", 500],
    4: ["Helmet Violation", 500],
}

# Initializing payment types
paymentTypes = {
    1: "Unpaid",
    2: "Paid",
}


def main():

    isUserLoggedIn = False

    while not isUserLoggedIn:
        # Initializing a session object
        requestSession = requests.session()

        # Taking username and password of traffic police
        username = input("Enter traffic police username: ")
        password = getpass("Enter traffic police password: ")

        # Get request to extract csrf token
        requestSession.get(baseUrl + loginUrl)
        csrfToken = requestSession.cookies['csrftoken']

        # Logging in with required data
        loginResponse = requestSession.post(
            baseUrl + loginUrl,
            data = {
                "userName": username,
                "userPassword": password,
                "csrfmiddlewaretoken": csrfToken
            },
            headers = dict(Referer = baseUrl + loginUrl)
        )

        # Checking if successfully logged in, stopping while loop
        if "Invalid credentials." not in str(loginResponse.content):
            isUserLoggedIn = True
        # Else try again
        else:
            print("------------------------")
            print("Invalid credentials. Please try again.")
            print("------------------------")

    # Looping the menu till the user wants to exit
    while True:
        print("--------------------------------------")
        print(" RASPI RFID TRAFFIC PENALTY SYSTEM")
        print("--------------------------------------")
        print("1. Get all penalties of a user RFID")
        print("2. New penalty for a user RFID")
        print("3. Existing penalty payment by user")
        print("4. Exit")
        print("--------------------------------------")
        choice = int(input("Enter choice : "))
        print("--------------------------------------")

        # Getting all penalties of a RFID
        if choice == 1:
            
            # Getting all penalties and storing last updated date inside RFID
            getAllPenaltiesAndStoreDataInsideRFID(requestSession)

        # Submitting a new penalty for user RFID
        elif choice == 2:

            # Scanning RFID
            RFID, data = readRFID()

            # Printing the penalty types (menu)
            print("--------------")
            for key in penaltyTypes:
                penalty = penaltyTypes[key]
                print(f"{key}: {penalty[0]} Rs.{penalty[1]}")
            print("--------------")
            # Taking input from user
            type = int(input("Enter penalty type number : "))
            print("--------------")

            # Printing the payment status (menu)
            for key in paymentTypes:
                payment = paymentTypes[key]
                print(f"{key}: {payment}")
            print("--------------")
            # Taking input from user
            status = int(input("Enter payment type number : "))
            print("--------------")

            # Getting csrf token from GET route of submitPenaltyUrl
            submitPenaltyResult = requestSession.get(baseUrl + submitPenaltyUrl)
            data = json.loads(submitPenaltyResult.content)
            csrfToken = data["csrfmiddlewaretoken"]

            # Submitting penalty with the appropriate data
            submitPenaltyResult = requestSession.post(
                baseUrl + submitPenaltyUrl,
                data = {
                    "RFID": RFID,
                    "status": paymentTypes[status],
                    "type": penaltyTypes[type][0],
                    "amount": penaltyTypes[type][1],
                    "csrfmiddlewaretoken": csrfToken
                },
                headers = dict(Referer = baseUrl + submitPenaltyUrl)
            )
            data = json.loads(submitPenaltyResult.content)

            # Printing response
            try:
                print(data["Success"])
                # Getting all penalties and storing last updated date inside RFID
                getAllPenaltiesAndStoreDataInsideRFID(requestSession)
            except:
                print(data["Failure"])

        # Existing payment penalty by user
        elif choice == 3:

            # Taking input from user
            print("--------------")
            penaltyID = int(input("Enter penalty ID : "))
            print("--------------")

            # Getting csrf token from GET route of payPenaltyUrl
            payPenaltyResult = requestSession.get(baseUrl + payPenaltyUrl)
            data = json.loads(payPenaltyResult.content)
            csrfToken = data["csrfmiddlewaretoken"]

            # Update penalty with the appropriate data (Changing status to 'Paid')
            payPenaltyResult = requestSession.post(
                baseUrl + payPenaltyUrl,
                data = {
                    "penaltyID": penaltyID,
                    "csrfmiddlewaretoken": csrfToken
                },
                headers = dict(Referer = baseUrl + payPenaltyUrl)
            )
            data = json.loads(payPenaltyResult.content)

            # Printing response
            try:
                print(data["Success"])
                # Getting all penalties and storing last updated date inside RFID
                getAllPenaltiesAndStoreDataInsideRFID(requestSession)
            except:
                print(data["Failure"])
        # Else exiting
        elif choice == 4:
            break

    print("--------------------------------------")
    print("BYE")
    print("--------------------------------------")

def getAllPenaltiesAndStoreDataInsideRFID(requestSession):
    """Function to get all penalties and store last updated date inside RFID.
       All data is stored inside server and not RFID as RFID has limited space."""
    
    # Scanning RFID
    RFID, data = readRFID()
    print("--------------")
    print("User Data")
    print("--------------")

    # Getting the penalties linked to above RFID through API
    getPenaltiesResult = requestSession.get(baseUrl + getPenaltiesUrl + f"/{RFID}")
    data = json.loads(getPenaltiesResult.content)
    penaltiesArray = data["Penalties"]

    # Printing the penalties of user RFID received
    for penalty in penaltiesArray:
        for key in penalty:
            print(key, ":", penalty[key])
        print()
    
    # Writing last updated date inside RFID
    try:
        print("Hold RFID tag near sensor to write...")
        reader.write(f"Last updated : {datetime.datetime.now()}")
        print("Written")
    finally:
        # Cleaning up GPIO previous settings
        GPIO.cleanup()

def readRFID():
    """Function to read RFID tag and return RFID and data inside it."""
    
    # Reading and returning as required
    try:
        # Reading and printing information inside card
        print("Hold RFID tag near sensor for reading data...")
        RFID, text = reader.read()
        print("RFID : ", RFID)
        print("Previous data inside RFID: ", text)
    
        # Returning data
        return RFID, text
    except KeyboardInterrupt:
        
        # Cleaning up GPIO previous settings
        GPIO.cleanup()
        raise

# Calling main function
if __name__ == "__main__":
    main()
