import os
import time
import re
from slackclient import SlackClient
import logging
import smtplib
import smtpd
from email.mime.text import MIMEText

# instantiate Slack client
SLACK_BOT_TOKEN = 'xoxb-618747692885-607526628418-iZbyB5nCbgawQuVNZMx4Z3RR'
# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient(SLACK_BOT_TOKEN)

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def send_email(user, msg):
    gmail_user = 'kishorepython90@gmail.com'
    gmail_password = 'Kishore1571991'
    sent_from = gmail_user
    # add emails if needed
    to = ['kishorepython90@gmail.com']
    taskname, priority, hours = msg.split(':')
    message = """Subject: Daily Status from Slackbot

    Hi {name}, For the task {taskname} priority assigned is {priority} with {hours} hours assigned by {user} """

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to,
                        message.format(name='admin', taskname=taskname, priority=priority, hours=hours, user=user))
        server.close()

        print('Email sent!')
    except Exception as e:
        print(e)


def post_slack_msg(channel, task_name):
    email_str = 'email is sent out to admin regarding task' + task_name
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=email_str
    )


def process_slack_events(events):
    for event in events:
        if 'content' in event and 'title' in event:
            try:
                user, msg = event['content'].split(': @Starter bot ')
                channel = event['channel']
                count_colon = len(msg.split(':'))
                if count_colon == 3:
                    send_email(user, msg)
                    post_slack_msg(channel, msg.split(':')[0])
            except Exception as e:
                print(e)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            slack_cl = slack_client.rtm_read()
            if slack_cl:
                #                print('slack cl:',slack_cl)
                process_slack_events(slack_cl)

            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
