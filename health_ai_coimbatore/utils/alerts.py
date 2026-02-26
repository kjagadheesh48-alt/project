import smtplib
import ssl
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_alert(current_ward, prediction, df, ward_col, case_col):

    # ================= EMAIL SETTINGS =================
    sender_email = ""
    sender_password = ""

    receiver_emails = [
        ""
    ]

    # ================= FAST2SMS SETTINGS =================
    FAST2SMS_API_KEY = ""
    recipient_number = ""  # Indian number WITHOUT +91

    # ================= FIND OTHER HIGH RISK WARDS =================
    other_high_risk = df[df[case_col] > 8][ward_col].unique()
    other_high_risk = [w for w in other_high_risk if w != current_ward]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ================= EMAIL BODY =================
    body = f"""
SMART COMMUNITY HEALTH ALERT
--------------------------------------

Date: {timestamp}
Current Ward: {current_ward}
Risk Level: {prediction}

Other Wards Showing Rising Risk:
"""

    if len(other_high_risk) > 0:
        for ward in other_high_risk:
            body += f"\n- {ward}"
    else:
        body += "\nNone"

    body += """

Immediate inspection and water testing recommended.

Coimbatore Smart Health Monitoring System
"""

    # ================= SEND EMAIL =================
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(receiver_emails)
        msg["Subject"] = f"🚨 High Risk Alert - {current_ward}"
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_emails, msg.as_string())

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email Error:", e)

    # ================= SEND SMS USING FAST2SMS =================
    try:
        sms_message = f"""
HEALTH ALERT
Ward: {current_ward}
Risk: {prediction}
Time: {timestamp}
Immediate action required.
"""

        url = "https://www.fast2sms.com/dev/bulkV2"

        payload = {
            "sender_id": "FSTSMS",
            "message": sms_message,
            "language": "english",
            "route": "q",
            "numbers": recipient_number,
        }

        headers = {
            "authorization": FAST2SMS_API_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(url, data=payload, headers=headers)

        print("✅ SMS sent successfully")
        print("Fast2SMS Response:", response.text)

    except Exception as e:
        print("❌ SMS Error:", e)