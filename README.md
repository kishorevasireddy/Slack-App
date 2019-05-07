# slackbot
A Slack bot to send status reports.

In a software development project, tasks and activities my be tracked for project reporting with formal tools (such as JIRA, BugZilla, Apache Bloodhound, Trac, and many others). These tools may in fact cover other use cases: bug tracking, issue tracking, ticket management, etc.

However, some more informal tasks, either self-initiated or quickly discussed without formal inclusion in a project plan, may be defined ad-hoc during the course of a project. Team members may spend time and effort on those tasks, and it is worth capturing that "outside" activity, so as to acknowledge such work and results (for example in weekly team reports), and possibly to adapt subsequent phases of the project.

Informal team collaboration and communication tools (with functions such as Instant Messaging, chat, audio, video, file sharing, wikis, etc.) can be leveraged to perform this informal task activity and progress tracking.

slackbot is a tool that automates the reporting for these tasks, using the API of Slack ("Searchable Log of All Conversation and Knowledge"), a "freemium" team collaboration product.

Slack has the notion of "channels" (multi-user persistent chats). Team members can join and leave channels, and see the whole channel history of messages.

This feature is exploited by slackbot in the following way:
- assume team members join a certain channel (which can be used for other purposes)
- team members can post messages to indicate informal task activity, with the format <task_name>:<priority_level>:<progress_percentage>, where <priority_level> is between 0 and 2 (0:low, 1: medium, 2: high)
(for example: "try alternative GUI solution":1:40, which means the team member is saying that he/she is at 40% completion on the medium-priority task "try alternative GUI solution")
- slackbot periodically monitors a given channel, parses posted messages, and compiles all messages in this format (with user ID) to create automatically a report (in spreadsheet format) which can then be used by project managers

slackbot can be very useful when team are geographically distributed, in different time zones, to support the tracking of informal project tasks.

slackbot will initially be tried for the BluePlanet project, on the Slack instance blueplanet.slack.com

## 
