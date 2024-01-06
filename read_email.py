# read_email.py
import email
import imaplib
import time
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from db import get_db
from models import Email
from sqlalchemy.orm import Session
from sqlalchemy import select
from email.header import decode_header
from email.message import EmailMessage
from datetime import datetime
import smtplib
import ssl

router = APIRouter(
    prefix="/read_mail"
)

start_time = time.time()

def decode_str(s):
    if s:
        return decode_header(s)[0][0]
    return ""

def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def run_read_and_store(email_address, password, db):
    global emails_sent_today  # Declare as a global variable
    emails_sent_today = 0

    while emails_sent_today < 300:
        sender = read_and_store(email_address, password, db)
        time.sleep(10)

@router.get("/read/emails")
def read_emails(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    email_address = "netsmartzengg2001@hotmail.com"
    password = "Netsmartz@1386"

    # Add background task to run read_and_store every 10 seconds
    background_tasks.add_task(run_read_and_store, email_address, password, db)

    return {"Message": "Reading emails in the background."}

def read_and_store(email_address, password, db: Session):
    global emails_sent_today  # Declare as a global variable
    sender = []
    mail = imaplib.IMAP4_SSL("outlook.office365.com")
    mail.login(email_address, password)
    print("Login successful")

    mail.select("INBOX")

    _, msg_nums = mail.search(None, "ALL")
    print("The messages are ", msg_nums)
    all_msg_id = msg_nums[0].split()

    _, messages = mail.search(None, "UNSEEN")
    message_ids = messages[0].split()

    for msg_id in message_ids:
        _, msg_data = mail.fetch(msg_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_str(msg["Subject"])
                sender_email = decode_str(msg.get("From"))
                sender.append(sender_email)
                body = get_body(msg)
                received_at = datetime.now()

                print(f"Subject: {subject}")
                print(f"From: {sender_email}")
                print(f"Body: {body}")

                # Store email in the database
                email_data = Email(
                    id=msg_id.decode('utf-8'),
                    subject=subject,
                    sender=sender_email,
                    body=body,
                    received_at=received_at
                )
                db.add(email_data)

    # Commit changes after processing all emails
    db.commit()

    mail.close()

    for sender_mails in sender:
        global emails_sent_today  # Declare as a global variable
        emails_sent_today += 1
        send_reply(sender_mails, db)
        if emails_sent_today >= 300:
            print("Daily email limit reached. Exiting.")
            return {"Outlook Exception": "Daily Limit of 300 messages reached."}

    mail.logout()
    return sender

def send_reply(email_id: str, dbase):
    result = dbase.execute(select(Email).filter_by(sender=email_id))
    email_data = result.fetchone()

    parsed_sender = email.utils.parseaddr(email_id)
    email_address = parsed_sender[1]
    print("The email address is ", email_address)

    if email_data and hasattr(email_data, 'subject'):
        print("Subject is ", email_data.subject)
    else:
        print("Subject not found in email_data.")

    print("=" * 30)
    my_email = "netsmartzengg2001@hotmail.com"
    # password = os.getenv('PASSWORD')
    password = "Netsmartz@1386"
    subject = " DO NOT REPLY!!!"
    body = f"We have recieved your mail.We will contact you in few minutes.\n\n Regards Team!"

    em = EmailMessage()
    em['From'] = my_email
    em['To'] = email_address
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    # with smtplib.SMTP_SSL('smtp-mail.outlook.com', 465, context=context) as smtp:
    #     smtp.login(my_email, password)
    #     smtp.sendmail(my_email, email_address, em.as_string())
    #     smtp.quit()
    # print("Reply sent successfully")
    try:
        with smtplib.SMTP('smtp-mail.outlook.com', 587) as smtp:
            smtp.starttls(context=context)
            smtp.login(my_email, password)
            smtp.sendmail(my_email, email_address, em.as_string())
        print("Reply sent successfully")
    except Exception():
        raise HTTPException(status_code=404, detail="Email not found.")
    return 0

