
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import email
from email.header import decode_header
from pydantic import BaseModel
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
import re

from toolserve.sdk import Param, tool, get_secret
from toolserve.sdk.dataframe import get_df, save_df


@tool
async def send_email(
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
async def read_email(
    output_name: Param(str, "Name of the output data"),
    n_emails: Param(int, "Number of emails to read") = 5,
    ):
    """Read emails from a Gmail account and extract plain text content, removing any HTML."""

    email_address = get_secret("gmail_email")
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
            "date": msg["Date"]
        }

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                    email_details["body"] = clean_email_body(body)
        else:
            body = msg.get_payload(decode=True).decode('utf-8')
            email_details["body"] = clean_email_body(body)

        emails.append(email_details)

    mail.close()
    mail.logout()
    df = pd.DataFrame(emails)
    await save_df(df, output_name)



def clean_email_body(body: str) -> str:
    """Remove HTML tags and non-sentence elements from email body text."""


    # Remove HTML tags using BeautifulSoup
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(separator=' ')

    # Remove any non-sentence elements (e.g., URLs, email addresses, etc.)
    text = re.sub(r'\S*@\S*\s?', '', text)  # Remove emails
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^.!?a-zA-Z0-9\s]', '', text)  # Remove non-sentence characters
    text = ' '.join(text.split())  # Remove extra whitespace

    return text


@tool
async def plot_dataframe(
    data_id: Param(int, "Data ID of the dataframe"),
    x: Param(str, "Column to use as x-axis"),
    y: Param(str, "Column to use as y-axis"),
    kind: Param(str, "Type of plot") = "line",
    title: Param(str, "Title of the plot") = "Plot",
    xlabel: Param(str, "Label for x-axis") = "X",
    ylabel: Param(str, "Label for y-axis") = "Y",
    ) -> Param(str, "JSON representation of the plot"):
    """
    Asynchronously generates a plot from a dataframe using Plotly and returns the plot as a JSON string.

    Args:
        data_id (int): The ID of the dataframe to plot.
        x (str): The column name to use as the x-axis.
        y (str): The column name to use as the y-axis.
        kind (str): The type of plot to generate (e.g., 'line', 'scatter', 'bar').
        title (str): The title of the plot.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis.

    Returns:
        str: The JSON representation of the plot.
    """
    import plotly.express as px
    df = await get_df(data_id)

    if kind == 'line':
        fig = px.line(df, x=x, y=y, title=title)
    elif kind == 'scatter':
        fig = px.scatter(df, x=x, y=y, title=title)
    elif kind == 'bar':
        fig = px.bar(df, x=x, y=y, title=title)
    else:
        raise ValueError(f"Unsupported plot type: {kind}")

    fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)

    return fig.to_json()

