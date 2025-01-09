import math
import calendar
import pandas as pd
# import ldap_helper as ldap
from utils.log_helper import LOGGER
import utils.constants as constants
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from typing import Dict
import time


class EmailGenerator:
    def __init__(self, fileName):
        data = pd.read_excel(fileName, sheet_name='Home Drives')
        self.total_drives = data.shape[0]
        self.raw = data
        self.data = self.finetune_data(data)
        self.ministry_summary = {
            'HomeDrives': self.total_drives,
            'BaseAllocation': self.total_drives * 1.5,
            'TotalHomeDriveUsage': self.raw['Used (GB)'].sum()

        }
        month_number = int(fileName.name.split('_')[0].split('-')[1])
        self.month_name = calendar.month_name[month_number]
        # fp = open('../images/EmptyRecycleBin.png', "rb")
        # self.empty_recycle_bin = fp.read()
        # fp.close()


    @staticmethod
    def finetune_data(data: pd.DataFrame) -> pd.DataFrame:
        finetuned = data[data['Used (GB)'] > 1.5]

        return finetuned

    def send_idir_email(self, idir_info: Dict):
        # Variable Definitions:
        # idir_info         Dictionary of info for a user
        # h_drive_count     H drives for the users ministry
        # total_gb          Total gb for the users ministry
        # biggest_drop      Biggest single user reduction last month
        # last_month        The most recent reporting month
        # month_before_last The reporting month before last_month
        ministry_name = "Transportation and Transit"

        name = idir_info["First Name"]
        recipient = idir_info["Email"]
        last_month_gb = idir_info['Used (GB)']
        last_month_cost = (last_month_gb - 1.5) * 2.7 if last_month_gb > 1.5 else 0.00
        msg = MIMEMultipart("related")

        year = '2024'
        last_month_name = self.month_name

        total_gb = float(self.ministry_summary['TotalHomeDriveUsage'])
        h_drive_count = float(self.ministry_summary['HomeDrives'])
        # Get the cost of ministry H Drives and biggest drops
        total_h_drive_cost = (total_gb - (h_drive_count * 1.5)) * 2.7

        # Round down to nearest thousand for legibility
        total_gb = int(math.floor(total_gb / 10) * 10)
        total_h_drive_cost = int(round((math.floor(total_h_drive_cost / 10) * 10) * 12, -4)/1000)
        h_drive_count = int(math.floor(h_drive_count / 10) * 10)

        # Build email content and metadata
        msg["Subject"] = (
            f"For your action: Personal Storage Report (PSR) for {last_month_name} {year}"
        )
        msg["From"] = "DataStorageReduction@gov.bc.ca"
        msg["To"] = recipient

        # Greet the user and provide introduction
        html_intro = f"""
        <html><head>
            <style>
                .indent {{
                  margin-left: 20px; /* Adjust the value as needed */
                }}
              </style>
        </head><body><p>
            Hi {name},<br><br>

            This report from the MOTT Data Storage Reduction Team (DSR) shows the costs of your "home" or H: drive <i>as it appeared on {last_month_name} 15th.</i><br>
            As of September 13, 2024, we have adopted OneDrive as our personal data storage location. H: drives are no longer used at MOTT for data storage.

"""

        # Remind user why storage costs are important as a ministry
        html_why_data_important = f"""          
            <p>The continued use of our H: drives costs MOTT approximately ${total_h_drive_cost}K annually, as opposed to OneDrive, which is no cost.</p>
                """

        # Inform user of personal metrics
        html_personal_metrics = f"""<br>
        <p class='indent' style="font-size: 14pt; font-weight: bold;">Your H: drive size in {last_month_name} was {last_month_gb:,} GB, billed to Ministry of {ministry_name} at ${last_month_cost:,.2f} per month. </p>
        <p class='indent' style="font-size: 14pt; font-weight: bold; color: red;">For your Action: Your data must be moved to OneDrive to avoid future costs.</p>
        """

        # Provide solutions to the user to help with H Drive faqs/issues
        html_why_important = """
        <p>Follow these steps on  <a href='https://intranet.gov.bc.ca/trannet/initiatives/data-storage-reduction#phase1'>TRANnet</a>; please <a href='mailto:datastoragereduction@gov.bc.ca'>connect with the DSR team </a> if you need further assistance</p>
        <br>
            """  # noqa


        # Email sign-off
        html_footer = """
            This email is transitory and can be deleted when no longer needed. Thank you for taking the time to manage your digital storage!<br>
            <br>
            Regards,
            <br>
            MOTT Data Storage Reduction Team
            <br>
            Ministry of Transportation and Transit
            <br>
            DataStorageReduction@gov.bc.ca

            </p>
            </html>
            """

        # Merge html parts and attach to email

        html = (
                html_intro
                + html_why_data_important
                + html_personal_metrics
                + html_why_important
                + html_footer
        )
        msg.attach(MIMEText(html, "html"))

        # Add header which suppresses out of office requests
        msg.add_header("X-Auto-Response-Suppress", "OOF, DR, RN, NRN")

        # Send email to recipient
        s = smtplib.SMTP(constants.SMTP_SERVER)
        # s.sendmail(msg["From"], recipient, msg.as_string())
        s.sendmail(msg["From"], recipient, msg.as_string())
        # Log the email sent
        LOGGER.info(f"Email sent to {recipient}.")
        s.quit()

        # Following smtp server guidelines of max 30 emails/minute
        time.sleep(2)


    def send_all_emails(self):
        records_to_send = self.data.to_dict(orient='records')
        for record in records_to_send:
            self.send_idir_email(record)