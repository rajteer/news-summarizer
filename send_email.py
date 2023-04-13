import os
import ssl
import getpass
import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Dict
from dotenv import load_dotenv
from secrets import compare_digest
import keyring

def read_config()-> Tuple[str, str, int]:
    """ Function meant to read the config file and return the recipients' email addresses, 
        stmp server and port.

    Returns:
        Tuple[str, str, int]: Returned tuple contains the recipients' email addresses, stmp 
        server and port read from the config file.
    """
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
        # get the recipients' email addresses from the config file
        recipients_email = config["recipients"]["emails"]
        if not recipients_email:
            print("Recipients' email addresses not set")
            raise ValueError("Recipients' email addresses not set")
        # get the stmp server from the config file
        stmp_server = config["sender"]["smtp_server"]
        if not stmp_server:
            print("Stmp server not set")
            raise ValueError("Stmp server not set")
        # get the port from the config file and convert it to int
        port = int(config["sender"]["port"])
        if not port:
            print("Port not set")
            raise ValueError("Port not set")
    except Exception as exception:
        print("Eror while reading config file")
        raise exception
    return recipients_email, stmp_server, port

def send_email(email_body:str, email_subject:str)-> None:
    """ Function meant to send an email with the specified body and subject.
        Sender email is read from the environment variables.
        The password is stored in the Windows Credential Manager, so the
        user is prompted to enter it.
        User's passoword is NOT stored in the environment variables.
        Password is meant to be set with use of function insert_sender_email_password.
        Password can be changed with use of function change_sender_email_password.
        Recipients' email addresses, stmp server and port are read from the config file.
        The connection is secured with SSL.

    Args:
        email_body (str): text of the email 
        email_subject (str): _description_
    """
    sender_data = get_login_password()
    sender_email, sender_email_password = sender_data["login"], sender_data["password"]
    recipients_email, stmp_server, port = read_config()
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipients_email # can be a str with multiple emails separated by commas
    msg["Subject"] = email_subject
    msg.attach(MIMEText(email_body, "html"))
    # convert the MIMEMultipart object to a string to send it
    message = msg.as_string()
    # create a secure SSL context
    # SSL is a protocol that provides security for data sent over the internet
    ssl_context = ssl.create_default_context()
    with smtplib.SMTP(stmp_server, port) as server:
        server.starttls(context=ssl_context)
        try:
            server.login(user=sender_email, password=sender_email_password)
        except smtplib.SMTPAuthenticationError:
            print("Password or login incorrect")
            answer = ''
            counter = 0 # prevent infinite loop
            while answer not in ["n", "y"]:
                answer = input("Do you want to change the password for the sender email? ([y]/n)\n")
                counter += 1
                if counter == 3:
                    print("Too many attempts")
                    break
            if answer == "y":
                change_sender_email_password()
            else:
                print("Password not changed")
            raise ValueError("Password or login incorrect")
        server.sendmail(sender_email, recipients_email, message)

def insert_sender_email_password()-> None:
    """ Function meant to insert the password for the sender email which is read from the
        environment variables. The password is stored in the Windows Credential Manager.
    """
    # read sender email from environment variable
    load_dotenv()
    sender_email = os.environ.get("SENDER_EMAIL")
    # check if sender email is set in environment variable
    if not sender_email:
        print("Sender email not set")
        raise ValueError("Sender email not set")
    # read sender email password from keyring
    if keyring.get_password(service_name= 'e-mail service', username= sender_email):
        print("Password is already set")
    else:
        counter = 0 # prevent infinite loop
        while True:
            password = getpass.getpass("Enter password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            # compare_digest is used to prevent timing attacks
            if compare_digest(password, confirm_password) and password:
                keyring.set_password('e-mail service', sender_email, password)
                print("Password set")
                break
            if not password:
                print("Password is empty")
            elif not compare_digest(password, confirm_password):
                print("Passwords do not match")
            counter += 1
            if counter == 3:
                print("Too many attempts")
                break

def change_sender_email_password()-> None:
    """ Function meant to change the password for the sender email which was previously
        inserted with use of function insert_sender_email_password.
    """
    # read sender email from environment variable
    load_dotenv()
    sender_email = os.environ.get("SENDER_EMAIL")
    answer = input("Do you want to change the password for the sender email? ([y]/n)\n")
    if answer == "y":
        # check if sender email is set in environment variable
        if not sender_email:
            print("Sender email not set")
            raise ValueError("Sender email not set")
        counter = 0 # prevent infinite loop
        while True:
            new_password = getpass.getpass("Enter new password: ")
            confirm_password = getpass.getpass("Confirm new password: ")
            # compare_digest is used to prevent timing attacks
            if compare_digest(new_password, confirm_password) and new_password:
                keyring.set_password('e-mail service', sender_email, new_password)
                print("Password changed")
                break
            elif not new_password:
                print("Password is empty")
            elif not compare_digest(new_password, confirm_password):
                print("Passwords do not match")
            counter += 1
            if counter == 3:
                print("Too many attempts")
                break
    else:
        print("Password not changed")

# get login and password for sender email
def get_login_password() -> Dict[str, str]:
    """ Function meant to get the login and password for the sender email.

    Returns:
        Dict[str, str]: dictionary with login and password for sender email.
    """
    # read sender email from environment variable
    load_dotenv()
    sender_email = os.environ.get("SENDER_EMAIL")
    if not sender_email:
        print("Sender email not set")
        print("Please set the sender email in the environment variables")
        raise ValueError("Sender email not set")
    # read sender email password from keyring
    password = keyring.get_password(service_name= 'e-mail service', username= sender_email)
    if not password:
        print("Password is not set")
        answer = ''
        counter = 0 # counter to prevent infinite loop
        while answer != "y" and answer != "n" and counter < 3:
            answer = input("Do you want to set the password for the sender email? ([y]/n)\n")
            counter += 1
        if answer == "y":
            insert_sender_email_password()
            password = keyring.get_password(service_name= 'e-mail service', username= sender_email)
        else:
            print("Password not set")
            print("Please set the password for the sender email with use of function \
                  insert_sender_email_password()")
            raise ValueError("Password not set")
        if not password:
            print("Password is an empty string")
            raise ValueError("Password's value is not correct")
    return {"login": sender_email, "password": password}
