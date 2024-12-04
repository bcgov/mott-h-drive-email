from utils.email_generator import EmailGenerator

if __name__ == '__main__':
    gen = EmailGenerator('data/2024-11_SFP TRAN Usage.xlsx')
    gen.send_all_emails()
