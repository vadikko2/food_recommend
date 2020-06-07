# Slack Alert Bot

The slack alert bot module read messages about different events from configured RabbitMQ queues and push them to 
appropriate slack channels.

There are some steps for deploy alert bot.

1. Create Workplace and Application for notifying Bot.
2. Create ```api.token ``` file in  ```slackbot/``` directory with TOKEN for your Slack Application simply as text.
3. Create necessary Channels in your Workplace and add Application to it.
4. Configure ```config.py``` file:
    - set ```RABBIT_LOGIN``` and ```RABBIT_PASSWORD```
    - add to the ```ALERT_FLOWS``` pairs ```QUEUE_NAME``` and ```SLACK_CHANNEL```.
5. Run ```runner.py``` script.