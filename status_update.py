import os
from datetime import datetime
from slackclient import SlackClient
from xlwt import Workbook, XFStyle
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='status.log',
                    level=logging.DEBUG)


class SlackProjectStatusAPI:
    def __init__(self, channel_name, slack_token=None):
        if not slack_token:
            raise Exception('Slack token required to run the app')
        self.sc = SlackClient(slack_token)
        self.channel_name = channel_name

        # print(self.sc)
        # print(self.channel_name)

    def get_users(self):
        '''
        Get the list of users
        :return:
        '''
        users_list = self.sc.api_call("users.list")
        print(users_list)

        users = {}
        for user in users_list['members']:
            # print(user.get('profile').get('real_name'))
            users[user['id']] = user['profile']['real_name']

        return users

    def get_channel_id(self):
        '''
        Get the channel id
        :return:
        '''
        channels = self.sc.api_call("channels.list")
        # print(channels)
        channel_id = None
        for channel in channels['channels']:
            if channel['name'] == self.channel_name:
                return channel['id']
        if channel_id == None:
            raise Exception("cannot find channel " + channel_name)

    def get_history_messages(self):
        '''
        Get history of messages by users and project
        :return:
        '''
        channel_id = self.get_channel_id()
        history = self.sc.api_call("channels.history", channel=channel_id)
        # print(history)

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

                if not get_level:
                    status_messages[user][task_name]['level'] = level
                    status_messages[user][task_name]['percent_complete'] = percent_complete
                else:
                    get_existing_level_val = levels.get(get_level)
                    current_level_val = levels.get(level)
                    if current_level_val > get_existing_level_val:
                        status_messages[user][task_name]['level'] = level
                        status_messages[user][task_name]['percent_complete'] = percent_complete
        return status_messages

    def get_activity_messages(self):
        '''
        Get activity log for all users
        :return:

        '''
        activity_messages = {}
        channel_id = self.get_channel_id()
        history = self.sc.api_call("channels.history", channel=channel_id)
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

        return activity_messages

    def create_work_book(self, users, status_messages, activity_messages):
        '''
        Will create a work book.
        :param users: list of users in the channel
        :param status_messages: messages by user and project
        :param activity_messages: activity log of messages by user
        :return:
        '''
        wb = Workbook()
        sheet1 = wb.add_sheet('Sheet 1')
        style = XFStyle()
        style.alignment.wrap = 1
        headers = ['sno', 'User', 'Task Name','Task Description','Task Priority', 'Task Percent Completed', 'Activity Log']

        for ind, header in enumerate(headers):
            sheet1.write(0, ind, header)

        serial_number = 1
        serial_number1 = 0
        for user in status_messages:
            print('User: '+user)
            serial_number1 += 1
            sheet1.write(serial_number, 0, serial_number1)
            sheet1.write(serial_number, 1, users.get(user))
            tasks = status_messages.get(user)
            for task in tasks:
                print('task : '+task)
                percent_complete, level = tasks.get(task).get('percent_complete'), tasks.get(task).get('level')

                activity = [e[0] + '-' + e[1] for e in activity_messages.get(user).get(task)]
                activity = '\n'.join(activity)
                # print(activity)
                # sheet1.write(serial_number, 0, serial_number)
                # sheet1.write(serial_number, 1, users.get(user))
                sheet1.write(serial_number, 2, task)
                # sheet1.write(serial_number, 3, 'xxx')
                sheet1.write(serial_number, 4, level)
                sheet1.write(serial_number, 5, percent_complete)
                sheet1.write(serial_number, 6, activity, style)
                serial_number += 1
                # print('user: ', users.get(user), 'task name: ', task, 'percent_complete: ', percent_complete, 'level: ',
                #       level, 'activity', activity)

        wb.save('status_update.xls')

    def send_email(self):
        '''
        Send email to admin
        :return:
        '''
        email = 'kishorepython90@gmail.com'
        password = 'Kishore1571991'
        send_to_email = 'kishorepython90@gmail.com'
        subject = 'Status Update'
        message = '''
        Dear Admin,\n
        Please look at the status update for more information in the attachement for all projects and tasks associated. \n
        Thanks, \n
        Slack\n
        '''
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

    def process_messages(self):
        '''
        process status messages and activity messages
        Creating work book
        Send email to the admin
        :return: None
        '''
        try:
            users = self.get_users()
            status_messages = self.get_history_messages()
            activity_messages = self.get_activity_messages()
            self.create_work_book(users, status_messages, activity_messages)
            self.send_email()
            logging.info('Processed status messages')
        except Exception as e:
            logging.error('e')


slack_token = "xoxp-624588002999-624922980694-622225453108-16927ef3eb502a617d7bee2636b90151"
channel_name = "status-test"

projectstatus = SlackProjectStatusAPI(channel_name, slack_token)
projectstatus.process_messages()


