import os
from flask import render_template

import database


def queue_filter(email_queue):
    while True:
        data = database.db_session.execute(stmt).fetchall()
        for itm in data:
            email_queue.put(itm)
        # delete data in the db that was put in queue



def send_email_confirmation(email_queue):
    while True:
        one_email = email_queue.get()
        send_email(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PWD'), one_email[0], one_email[1])


def send_email(user, pwd, recipient, new_films):
    import smtplib

    FROM = os.environ.get('EMAIL_USER')
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = 'New films list'
    TEXT = render_template('email_template', new_films)

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print ('successfully sent the mail')
    except:
        print ("failed to send mail")
