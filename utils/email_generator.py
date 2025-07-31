import math
import calendar
import openpyxl
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
        wb = openpyxl.load_workbook(fileName)
        sheet = wb['Summary']
        self.total_drives = sheet['B4'].value
        self.raw = data
        self.data = self.finetune_data(data)
        self.ministry_summary = {
            'HomeDrives': self.total_drives,
            'BaseAllocation': self.total_drives * 1.5,
            'TotalHomeDriveUsage': self.raw['Used (GB)'].sum()

        }
        month_number = int(fileName.name.split('_')[0].split('-')[1])
        self.year = int(fileName.name.split('_')[0].split('-')[0])
        self.month_name = calendar.month_name[month_number]
        # fp = open('../images/EmptyRecycleBin.png', "rb")
        # self.empty_recycle_bin = fp.read()
        # fp.close()


    @staticmethod
    def finetune_data(data: pd.DataFrame) -> pd.DataFrame:
        finetuned = data[(data['Used (GB)'] >= 0.1) & (~data['Email'].isna())]

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

        year = self.year
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

            After one year of data reduction our move from HDrive to OneDrive is almost complete. MOTT has a new HDrive policy, effective August 31, 2025
            <br>
"""

        # Inform user of personal metrics
        html_personal_metrics = f"""<br>
        <p class='indent' style="font-size: 14pt; font-weight: bold; color: red;">
        HDrives must not be used to store data. All HDrives must be empty by August 31st in preparation for the impending retirement of HDrives.
        </p>
        <br>

        Your HDrive currently stores {last_month_gb}GB of data.
        """

        # Provide solutions to the user to help with H Drive faqs/issues
        html_why_important = """
        <p>If you are receiving this message you need to move any needed files to your OneDrive and delete the data from your HDrive. No one can delete data from your Hdrive except you.</p>
        <p>See the <a href="https://intranet.gov.bc.ca/trannet/initiatives/data-storage-reduction">TRANnet</a> page on data storage reduction and follow directions under Phase 1 – Adopt OneDrive and How to Move Files from H:Drive to OneDrive.</p>

<p>Two very common reasons for data in your HDrive (when you thought it was empty) are:</p>

<ol>
    <li>Items on your desktop
        <ol type="a">
            <li>If you store items on your desktop you must go to desktop properties and change the location of backups from H to OneDrive.
                <ol type="i">
                    <li>use File Explorer to find your desktop under This PC</li>
                    <li>use the right mouse click on Desktop, scroll to the bottom and choose Properties</li>
                    <li>Desktop Properties will open with 5 tabs – choose Location</li>
                    <li>in this tab you will choose Move… which will allow you to navigate to choose your OneDrive as the new location for desktop backup</li>
                    <li>click Apply and ensure you say ‘yes’ when asked if you want to delete the files from previous backup location</li>
                </ol>
            </li>
            <li>This will complete the change of backup location. All the items on your desktop should remain unchanged.</li>
            <li>Your desktop and the ‘desktop’ icon in OneDrive will synchronize. The OneDrive desktop will be an identical copy of items on your desktop.</li>
        </ol>
    </li>
    <br>
    <li>The recycle bin is full!
        <ol type="a">
            <li>Many folks will hit ‘delete’ on a file or folder (which puts the file in the recycle bin) and think they are done.</li>
            <li>You need to empty the recycle bin! Please empty the recycle bin once Weekly</li>
            <li>If the recycle bin is not emptied the data will stay in your HDrive and MOTT will continue to pay for that storage.</li>
        </ol>
    </li>
</ol>
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