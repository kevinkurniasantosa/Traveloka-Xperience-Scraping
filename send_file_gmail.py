import os
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def send_gmail():
    # Email Credentials
    sender = 'Kevin Kurnia Santosa'
    personal_email = 'kevin.kurnia@shopee.com'
    login_email = '' ## erased for confidentiality
    login_password = '' ## erased for confidentiality
    recipient = ['kevin.kurnia@shopee.com']
    cc_recipient = ['kevin.kurnia@shopee.com', 'riza.pratama@shopee.com']
    current_month = datetime.now().strftime('%B')
    all_recipient = recipient + cc_recipient

    print('Current month:', current_month)

    email_subject = "Traveloka Scraping - " + current_month
    email_message = '''  
            Hi Elvina, <br><br>
            Please find the attached Traveloka Scraping below for %s. <br><br>
            Thank you.
            ''' % (current_month)

    # Alias
    # from_alias = sender + ' ' + personal_email
    from_alias = sender

    # Create mime message
    msg_mime = MIMEMultipart()
    msg_mime['Subject'] = email_subject
    msg_mime['From'] = from_alias
    msg_mime['To'] = ", ".join(recipient)
    if len(cc_recipient) > 0:
        msg_mime['CC'] = ", ".join(cc_recipient)
    # msg_text = MIMEText(email_message, 'plain') # kalo formatnya bukan html
    msg_text = MIMEText(email_message, 'html')
    msg_mime.attach(msg_text)

    # Attachment list (kalo lbh dri satu)
    attachments = ['C:/Users/kevin.kurnia/Desktop/Project-Scraping/traveloka_scraping_attraction/Traveloka Scraping.csv']

    # Add attachment
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg) 
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            msg_mime.attach(msg)
        except Exception as err:
            print("Error while loading attachments:", err)
            raise

    composed_email = msg_mime.as_string()

    # Send email
    try:
        print('\nStart sending..')
        time.sleep(2)

        # with smtplib.SMTP('smtp.gmail.com', 587) as smtp_obj:
        smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.ehlo()
        smtp_obj.login(login_email, login_password)
        smtp_obj.sendmail(from_alias, all_recipient, composed_email)
        smtp_obj.close()

        print("Email successfully sent!")
        time.sleep(1)
    except Exception as err:
        print('Error while sending the email:', err)
        # pass

send_gmail()

