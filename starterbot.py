import os
from datetime import datetime
from slackclient import SlackClient
import time
from xlwt import Workbook, XFStyle
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

slack_token = "xoxp-624588002999-624922980694-622225453108-16927ef3eb502a617d7bee2636b90151"
channel_name = "status-test"
# date_from = os.environ["SLACK_SEARCH_FROM"]
# date_from = os.environ["SLACK_SEARCH_FROM"]
# date_from = os.environ["SLACK_SEARCH_FROM"]
# date_to = os.environ["SLACK_SEARCH_TO"]
#
# oldest = (datetime.strptime(date_from, "%Y-%m-%d") - datetime(1970, 1, 1)).total_seconds()
# latest = (datetime.strptime(date_to, "%Y-%m-%d") - datetime(1970, 1, 1)).total_seconds()

sc = SlackClient(slack_token)

users_list = sc.api_call("users.list")
print(users_list)

users = {}
for user in users_list['members']:
    # print(user.get('profile').get('real_name'))
    users[user['id']] = user['profile']['real_name']

# print(users_list['members'])
# for user in users_list['members']:
#     print(user)
#     print(type(user))
#     print(user.keys())
#     print(user['id'])

# for user in users_list['members']:
#     # print(user.get('profile').get('real_name'))
#     print(user.keys())
#     print(user.get('id'),user.get('real_name'))
# print(user.get('real_name'))
# print(user.get('profile').keys())

# users[user['id']] = user['profile']['first_name'] + ' ' + user['profile']['last_name']

channels = sc.api_call("channels.list")
# print(channels)
channel_id = None
for channel in channels['channels']:
    if channel['name'] == channel_name:
        channel_id = channel['id']
if channel_id == None:
    raise Exception("cannot find channel " + channel_name)

history = sc.api_call("channels.history", channel=channel_id)
# print(history)
posts_by_user = {}

levels = {
    'low': 0,
    'mid': 1,
    'high': 2
}

status_messages = {}
for message in history['messages']:
    txt, user = message.get('text'), message.get('user')
    count_colon = len(txt.split(':'))
    if count_colon == 3:
        # print('txt',txt)
        task_name, level, percent_complete = txt.split(':')
        # print(user,task_name,level,percent_complete)
        if user not in status_messages:
            status_messages[user] = {}

        if task_name not in status_messages.get(user):
            status_messages[user][task_name] = {}

        get_level = status_messages.get(user).get(task_name).get('level', None)
        get_percent_complete = status_messages.get(user).get(task_name).get('percent_complete', None)

        if not get_level:
            status_messages[user][task_name]['level'] = level
            status_messages[user][task_name]['percent_complete'] = percent_complete
        else:
            get_existing_level_val = levels.get(get_level)
            current_level_val = levels.get(level)
            if current_level_val > get_existing_level_val:
                status_messages[user][task_name]['level'] = level
                status_messages[user][task_name]['percent_complete'] = percent_complete

# print(status_messages)
#
activity_messages = {}
for message in history['messages']:
    # print(message)
    txt, user = message.get('text'), message.get('user')
    count_colon = len(txt.split(':'))
    if count_colon == 3:
        # print('txt',txt)
        task_name, level, percent_complete = txt.split(':')
        time_stamp = datetime.fromtimestamp(float(message.get('ts'))).strftime('%m-%d-%Y %H:%M')

        # print(user,task_name,level,percent_complete)
        if user not in activity_messages:
            activity_messages[user] = {}

        if task_name not in activity_messages.get(user):
            activity_messages[user][task_name] = []
        # print('type ts',time_stamp)
        activity_messages[user][task_name].append(
            (
                time_stamp,
                percent_complete
            )
        )

print(activity_messages)

# creating work book

wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1')
style = XFStyle()
style.alignment.wrap = 1
headers = ['sno', 'User', 'Task name', 'Priority', 'Percent Completed', 'Activity log']

for ind, header in enumerate(headers):
    sheet1.write(0, ind, header)

serial_number = 1
for user in status_messages:
    tasks = status_messages.get(user)
    for task in tasks:
        percent_complete, level = tasks.get(task).get('percent_complete'), tasks.get(task).get('level')

        activity = [e[0] + '-' + e[1] for e in activity_messages.get(user).get(task)]
        activity = '\n'.join(activity)
        print(activity)
        sheet1.write(serial_number, 0, serial_number)
        sheet1.write(serial_number, 1, users.get(user))
        sheet1.write(serial_number, 2, task)
        sheet1.write(serial_number, 3, level)
        sheet1.write(serial_number, 4, percent_complete)
        sheet1.write(serial_number, 5, activity, style)
        serial_number += 1
        print('user: ', users.get(user), 'task name: ', task, 'percent_complete: ', percent_complete, 'level: ', level,
              'activity', activity)

wb.save('status_update.xls')


## send email

def send_email():
    email = 'kishorepython90@gmail.com'
    password = 'Kishore1571991'
    send_to_email = 'kishorepython90@gmail.com'
    subject = 'Status Update'
    message = '''
    Dear Admin,\n  
    Please look at the status update for more information in the attachement for all projects and tasks associated.
    \nThanks,\nSlack\n'''

    file_location = 'status_update.xls'

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    # Setup the attachment
    filename = os.path.basename(file_location)
    attachment = open(file_location, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # Attach the attachment to the MIMEMultipart object
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()
    server.sendmail(email, send_to_email, text)
    server.quit()


send_email()
