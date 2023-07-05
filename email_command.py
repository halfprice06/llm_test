import os
import ssl
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

def send_email_report(user_email, collected_messages):

    email_sender = 'lexmagicreport@gmail.com'
    email_password = os.getenv("LEXMAGIC_GMAIL_PASS")
    email_receiver = user_email

    # Create the email message
    subject = 'LLM Output'
    body = f"""
    
    Here's your search results

    {collected_messages}

    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # with open(docx_file_path, 'rb') as f:
    #     file_data = f.read()
    
    # em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=os.path.basename(docx_file_path))

    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


