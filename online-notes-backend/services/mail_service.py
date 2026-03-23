import smtplib as smtp
from config import settings

async def send_mail(send_to: str, activation_link: str):
    login = 'vckrick@gmail.com'
    password = 'ozjx bjzd mtnk fjjm '

    server = smtp.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(login, password)

    msg = f'''Subject: Follow the link below to verify your account.
    From: online-notes

    Verification Link: {activation_link}'''  


    return server.sendmail(login, send_to, msg=msg)
