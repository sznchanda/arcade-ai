
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import email
from email.header import decode_header
from pydantic import BaseModel
import pandas as pd


from toolserve.sdk import Param, tool, get_secret


@tool
def send_email(
    sender_email: Param(str, "Email address of the sender"),
    recipient_email: Param(str, "Email address of the recipient"),
    subject: Param(str, "Subject of the email"),
    body: Param(str, "Body of the email"),
    ):
    """Send an email via gmail SMTP server"""

    sender_password = get_secret("gmail_password")
    server = get_secret("gmail_stmp_server", "smtp.gmail.com")
    port = get_secret("gmail_smtp_port", 587)

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(server, port)
    server.starttls()
    server.login(sender_email, sender_password)
    print("Logged in to SMTP server")

    server.send_message(message)
    server.quit()

    print(f"Email sent to {recipient_email}")



@tool
def read_email(
    email_address: Param(str, "Email address of the recipient"),
    n_emails: Param(int, "Number of emails to read") = 5,
    ) -> Param(str, "JSON dataframe of List of emails"):
    """Read emails from a Gmail account"""

    password = get_secret("gmail_password")
    server = get_secret("gmail_stmp_server", "smtp.gmail.com")
    port = get_secret("gmail_smtp_port", 587)

    # Connect to the Gmail IMAP server
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email_address, password)
    mail.select("inbox")  # connect to inbox.

    result, data = mail.search(None, "ALL")
    email_ids = data[0].split()
    email_ids.reverse()  # Reverse to get the most recent emails first

    emails = []

    for email_id in email_ids[:n_emails]:
        result, data = mail.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        email_details = {
            "from": msg["From"],
            "to": msg["To"],
            #"subject": decode_header(msg["Subject"])[0][0],
            "date": msg["Date"]
        }

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_details["body"] = part.get_payload(decode=True)
        else:
            email_details["body"] = msg.get_payload(decode=True)

        emails.append(email_details)

    mail.close()
    mail.logout()

    return pd.DataFrame(emails).to_json()



