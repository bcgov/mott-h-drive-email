from unittest import TestCase
from email_generator import EmailGenerator
from utils.constants import TEST_RECORD


class TestEmailGenerator(TestCase):
    def test_initializes_successfully(self):
        try:
            gen = EmailGenerator('../data/2024-11_SFP TRAN Usage.xlsx')
            self.assertTrue(True)
        except Exception as e:
            self.fail(e)

    def test_send_idir_email(self):
        gen = EmailGenerator('../data/2024-11_SFP TRAN Usage.xlsx')
        try:
            gen.send_idir_email(TEST_RECORD)
            self.assertTrue(True)
        except Exception as e:
            self.fail()

    def test_send_multiple_idir_email(self):
        gen = EmailGenerator('../data/2024-11_SFP TRAN Usage.xlsx')
        gen.data = gen.data[gen.data['User ID'].isin([
            'LGODFREY',
            'MBRUNESK',
            'NAYUZIK',
            'AMACKINN',
            'MACOLE',
            'NGINOUX',
            'ATEPPER',
            'AMABELL',
            'SHCHIN',
            'CSCHETTE',
            'TRNELSON',
            'EHOUCHEN',
            'AMCKINNO',
            'DIAROBIN',
            'KBROOKER',
            'APOMPONI',
            'HDUBASOV',
            'DCATON',
            'STHIBAUL'
        ])]
        try:
            gen.send_all_emails()
        except Exception as e:
            self.fail(e)

