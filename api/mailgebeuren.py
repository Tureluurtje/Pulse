from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jinja2 import Template
from typing import Optional

def send_verify_email(token: str, url: Optional[str]="https://kwako.nl/verify?token="):
    # Create the email container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your Kwako account"
    msg["From"] = "Kwako Team <no-reply@kwako.nl>"
    msg["To"] = "arthur@kwako.nl"
    msg["Reply-To"] = "support@kwako.nl"

    # Plain text version (fallback for email clients that don't support HTML)
    text = f"""Hi there,

    Please click the link below to verify your Kwako account:

    {url}{token}

    Thank you,
    The Kwako Team
    """

    # HTML version with a centered flex box
    template = Template("""
    <html style="background-color:#f4f4f4;">
    <head>
        <meta charset="UTF-8">
        <title>Verify Your Kwako Account</title>
        <style>
        /* General reset */
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
        }

        /* Flex container with padding instead of 100vh */
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px 20px;
        }

        /* Card style */
        .card {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 600px;
            width: 100%;
        }

        /* Button style */
        .button {
            background-color: #4CAF50;
            color: #ffffff !important;
            padding: 15px 30px;
            text-decoration: none;
            font-weight: bold;
            border-radius: 5px;
            display: inline-block;
        }

        /* Dark mode support for macOS Mail and iOS Mail */
        @media (prefers-color-scheme: dark) {
            body, html {
            background-color: #f4f4f4 !important;
            color: #000000 !important;
            }
            .card {
            background-color: #ffffff !important;
            }
            .button {
            background-color: #4CAF50 !important;
            }
        }
        </style>
    </head>
    <body>
        <div class="container">
        <div class="card">
            <h1 style="text-align: center; color: #333;">Welcome to Kwako!</h1>
            <p style="font-size: 16px; color: #555;">Hi there,</p>
            <p style="font-size: 16px; color: #555;">
            Please click the button below to verify your email address and activate your Kwako account.
            </p>
            <div style="text-align: center; margin: 30px 0;">
            <a href="{{ url }}{{ token }}" class="button">
                Verify Your Account
            </a>
            </div>
            <p style="font-size: 14px; color: #999; text-align: center;">
            If you didn't request this email, you can safely ignore it.
            </p>
            <p style="font-size: 14px; color: #999; text-align: center;">
            © 2025 Kwako Team
            </p>
        </div>
        </div>
    </body>
    </html>
    """)

    html = template.render(url=url, token=token)

    # Attach both parts
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.kwako.nl", 587) as server:
        server.starttls()
        server.login("no-reply@kwako.nl", "cydriv-gIqjen-quqxa5")
        server.send_message(msg)
        print("message send")

send_verify_email(token="testtoken")
