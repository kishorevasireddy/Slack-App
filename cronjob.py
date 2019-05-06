from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from statustracking.status_update import SlackProjectStatusAPI

slack_token = "xoxp-624588002999-624922980694-622225453108-16927ef3eb502a617d7bee2636b90151"
channel_name = "status-test"


def cron_job():
    projectstatus = SlackProjectStatusAPI(channel_name, slack_token)
    projectstatus.process_messages()
    print('completed processing at')


scheduler = BlockingScheduler()
# scheduler.add_job(cron_job, 'interval', minutes=1)
scheduler.add_job(cron_job, 'cron', day_of_week='sun', hour=23, minute=36)

scheduler.start()
