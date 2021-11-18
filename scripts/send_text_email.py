"""
  ___        _          _____                _ _
 / _ \      | |        |  ___|              (_) |
/ /_\ \_   _| |_ ___   | |__ _ __ ___   __ _ _| | ___ _ __
|  _  | | | | __/ _ \  |  __| '_ ` _ \ / _` | | |/ _ \ '__|
| | | | |_| | || (_) | | |__| | | | | | (_| | | |  __/ |
\_| |_/\__,_|\__\___/  \____/_| |_| |_|\__,_|_|_|\___|_|


V1.0.0: Simple script to send automatic text emails via smtp.  We'll eventually want to increase the complexity of the sent emails and add options for scheduling
"""

# import libraries
import os
import sys
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib


def generate_message_text(default_message=True, add_trademark=True, add_signature=None):
    # TODO: implement this more completely. For now this will return only a default message
    message = None
    if default_message:
        # message = u"""EAT IT! EAT IT GOOD!"""
        message = u"""YOU ARE OVERDUE FOR NIPPLE INSPECTION"""
    if add_trademark and message is not None:
        message = message + u"""\n\n\nemail auto-generated using latest inspector-tech\u2122 application"""
    if add_signature and message is not None:
        message = message + u"""\n\n\nkransekake -- director of nipple inspection"""

    return message


def get_smtp_str(addrs):
    """

    :param addrs:
    :return:
    """
    if 'gmail' in addrs:
        return 'smtp.gmail.com'
    elif 'outlook' in addrs:
        return 'smtp-mail.outlook.com'
    elif 'yahoo' in addrs:
        return 'smtp.mail.yahoo.com'
    else:
        raise ValueError('Email provider not support. Currently support providers are: gmail, outlook, yahoo')


def run(from_addrs: str, to_addrs: str, from_password: str, port: str, subject: str):
    """

    :param from_addrs:
    :param to_addrs:
    :param from_password:
    :param port:
    :return:
    """
    # TODO: We need to implement this to auto-generate messages and helpful hints.
    # We can create an inspector class and give each one an instance.
    message = generate_message_text(default_message=True, add_trademark=True, add_signature='director_of_nipple_inspection')
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = to_addrs
    msg['From'] = from_addrs
    msg.attach(MIMEText(message))

    # setup smtp
    smtp_str = get_smtp_str(from_addrs)
    smtp = smtplib.SMTP(smtp_str, port=port)
    # Say hello
    hello_ = smtp.ehlo()
    if hello_[0] != 250:
        raise ConnectionError('Could not contact smtp server: {0}'.format(smtp_str))
    else:
        print("{0} at address: {1}".format(str(hello_[1]).split(',')[0].strip("""b'"""), str(hello_[1]).split(',')[1].strip().strip('[').split(']')[0]))

    # Communicate with server using TLS encryption
    tls_ = smtp.starttls()
    if tls_[0] != 220:
        raise ConnectionError('Unable to initiate TLS encryption on: {0}'.format(smtp_str))
    else:
        print(str(tls_[1]).strip("""b'"""))

    # Login
    login_ = smtp.login(user=from_addrs, password=from_password)

    # send message
    smtp.sendmail(from_addr=from_addrs, to_addrs=to_addrs, msg=msg.as_string())

    # Close the connection
    closed_ = smtp.quit()
    if closed_[0] != 221:
        raise ConnectionError('Unable to close connection to: {0}'.format(smtp_str))

    return True


if __name__ == '__main__':
    send_to = 'mary.vanakin@gmail.com'
    subject = 'CORRECTION: ATTENTION: INSPECTION OVERDUE'
    config_path = "../../data/config.ini"
    parser = ConfigParser()
    parser.read(config_path)
    email_address = parser.get('inspector', 'email_address')
    password = parser.get('inspector', 'password')
    port = parser.get('inspector', 'port')
    # TODO: add support for other email attachment types, including audio, images, docs, etc. gifs :)
    result_ = run(from_addrs=email_address, to_addrs=send_to, from_password=password, port=port, subject=subject)
    if result_:
        print('Process complete')

    sys.exit()
