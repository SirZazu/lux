import re
import json
import pycurl

from logging import Handler, Formatter


# Default message format
MSG_FORMAT = '[%(levelname)s](%(asctime)s %(name)s): %(message)s'


class SlackHandler(Handler):

    """Handler that will emit every event to slack channel using pycurl
    """

    def __init__(self, webhook_url, channel, username, icon=None,
                 formating=MSG_FORMAT):
        super().__init__()
        self.formatter = Formatter(formating)
        self.curl = pycurl.Curl()
        self.curl.setopt(self.curl.URL, webhook_url)
        self.channel = channel
        self.username = username
        self.icon = icon

    def format_traceback(self, record):
        """Add markdown to traceback part of a message"""
        if record.find('Traceback') != -1:
            record = re.sub('\nTraceback', '\n```Traceback', record)
            record += '```'
        return record

    def emit(self, record):
        """Emit record to slack channel using pycurl to avoid recurrence
        event logging (log logged record)
        """
        data = {
            'channel': self.channel,
            'username': self.username,
            'icon_emoji': self.icon,
        }
        msg = self.format(record)
        msg = self.format_traceback(msg)
        data.update({'text': msg})
        self.curl.setopt(self.curl.POSTFIELDS, json.dumps(data))
        self.curl.perform()
