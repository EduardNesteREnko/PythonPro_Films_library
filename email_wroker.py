from celery import Celery
import models
import database
import email_sender

app = Celery('tasks', broker='amqp://guest@localhost//')

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(hours=7, minute=30, day_of_week=1),
        build_daily_messages.s(),
    )

@app.task
def send_email(subject, body, recipient):
    print(f"Sending email to {recipient}")

    #email_sender.send_email(subject, body, recipient)

@app.task
def build_daily_messages():
        newest_films = execute(select(models.Film).order_by(models.Film.created_at.desc()).limit(10)).all()
        email_body = build_daily_email_body(newest_films)
        email_recepients = database.da_session.query(models.User.email != None).all()
        for client in email_recepients:
            send_email.delay("Newest Films", email_body, client.email)