import json
import time
import smtplib
import os
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging
logging.basicConfig(
    filename="email_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load email data
with open("case.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract email details from JSON
employer_emails = [
    {"name": f"{item['emppocFirstname']} {item['emppocLastname']}", "email": item["emppocEmail"], "phone": item["emppocPhone"]}
    for item in data if item.get("emppocEmail") and item["emppocEmail"].lower() != "n/a"
]

# Load sent emails
try:
    with open("sent_emails.json", "r", encoding="utf-8") as sent_file:
        sent_emails = json.load(sent_file)
except FileNotFoundError:
    sent_emails = []

# Environment variables for sender credentials
sender_email = os.environ.get("EMAIL")
sender_password = os.environ.get("PASSWORD")

if not sender_email or not sender_password:
    logging.error("Sender credentials are missing. Set EMAIL and PASSWORD as environment variables.")
    raise EnvironmentError("Sender credentials are not configured.")

# Function to send an email
def send_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        logging.error(f"Error sending email to {recipient_email}: {e}")
        return False

# Retry failed email logic
def send_email_with_retry(sender_email, sender_password, recipient_email, subject, body, retries=3):
    for attempt in range(retries):
        logging.info(f"Attempting to send email to {recipient_email} (Attempt {attempt + 1}/{retries})")
        if send_email(sender_email, sender_password, recipient_email, subject, body):
            logging.info(f"Successfully sent email to {recipient_email}")
            return True
        time.sleep(300)  # Wait 5 minutes before retrying
    logging.error(f"Failed to send email to {recipient_email} after {retries} attempts.")
    return False

# Email sending logic
def send_batch_emails():
    daily_limit = 500
    interval_seconds = 300  # Send one email every 5 minutes
    sent_today = 0

    for employer in employer_emails:
        if sent_today >= daily_limit:
            logging.info("Daily limit of 500 emails reached.")
            break

        if employer["email"] in sent_emails:
            logging.info(f"Email to {employer['email']} already sent, skipping.")
            continue  # Skip already sent emails

        subject = f"Seasonal Job Inquiry {employer['name']}"
        body = f"""Greetings {employer['name']},

I trust this message finds you well.

My name is Ronnie, and I am writing to express my interest in potential seasonal job opportunities with your company. I take pride in honest labor, staying reliable, and putting in the effort to get things done right.

I know how to work efficiently while adapting to different tasks and understand the importance of teamwork, discipline, and delivering quality results, and I’m ready to bring that commitment to your team.

I would love the opportunity to discuss how I can contribute to your business. Please let me know if there’s a chance to connect. Thank you for your time and consideration—I look forward to hearing from you.

Kind regards,
Ronnie Mwesigwa Walusimbi
Email: ronniemwesigwa@icloud.com
Phone: +256788220078
WhatsApp: +256759417217
"""
        success = send_email_with_retry(sender_email, sender_password, employer["email"], subject, body)
        if success:
            sent_emails.append(employer["email"])
            sent_today += 1

            # Save sent emails to file
            with open("sent_emails.json", "w", encoding="utf-8") as sent_file:
                json.dump(sent_emails, sent_file, indent=4)

            logging.info(f"Email successfully sent to {employer['email']}. Waiting before next email...")
            time.sleep(interval_seconds)  # Wait before sending the next email

    logging.info("Batch processing complete.")

# Run the script
send_batch_emails()