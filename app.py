import os
import slixmpp
import asyncio
import re
from datetime import datetime, timedelta

class ReminderBot(slixmpp.ClientXMPP):
    def __init__(self):
        # Get the account and password from environment variables
        account = os.getenv('ROBOMINDER_ACCOUNT')
        password = os.getenv('ROBOMINDER_PASSWORD')

        # Check if the environment variables are present
        if not account or not password:
            raise ValueError('ROBOMINDER_ACCOUNT and ROBOMINDER_PASSWORD environment variables must be set')

        super().__init__(account, password)

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)
        self.reminders = {}

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    def format_remaining_time(self, reminder_time):
        now = datetime.now()
        delta = reminder_time - now
        minutes = delta.seconds // 60
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

    async def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            text = msg['body'].strip().lower()
            from_jid = msg['from']

            if text == "help":
                help_text = """Available commands:
- remind <time><h|m> <message>: Set a reminder (e.g., 'remind 1.5h take out laundry')
- list: Show all active reminders
- cancel <number>: Cancel reminder by number (get number from list command)
- help: Show this help message"""
                self.send_message(mto=from_jid, mbody=help_text)
                return

            if text == "list":
                if from_jid not in self.reminders or not self.reminders[from_jid]:
                    self.send_message(mto=from_jid, mbody="No active reminders.")
                    return

                reminders_list = "Active reminders:\n"
                for i, reminder in enumerate(self.reminders[from_jid], 1):
                    remaining = self.format_remaining_time(reminder['time'])
                    reminders_list += f"{i}. {reminder['message']} (in {remaining})\n"
                self.send_message(mto=from_jid, mbody=reminders_list)
                return

            cancel_match = re.match(r'^cancel\s+(\d+)$', text)
            if cancel_match:
                index = int(cancel_match.group(1)) - 1
                if (from_jid in self.reminders and 
                    0 <= index < len(self.reminders[from_jid])):
                    cancelled = self.reminders[from_jid].pop(index)
                    self.send_message(
                        mto=from_jid,
                        mbody=f"Cancelled reminder: {cancelled['message']}"
                    )
                else:
                    self.send_message(
                        mto=from_jid,
                        mbody="Invalid reminder number. Use 'list' to see available reminders."
                    )
                return

            remind_match = re.match(r'^remind\s+(\d+(?:\.\d+)?)(h|m)\s+(.+)$', text)
            if remind_match:
                amount = float(remind_match.group(1))
                unit = remind_match.group(2)
                message = remind_match.group(3)

                seconds = amount * 3600 if unit == 'h' else amount * 60
                remind_time = datetime.now() + timedelta(seconds=seconds)

                if from_jid not in self.reminders:
                    self.reminders[from_jid] = []

                self.reminders[from_jid].append({
                    'time': remind_time,
                    'message': message
                })

                asyncio.create_task(self.send_reminder(from_jid, seconds, message))
                
                self.send_message(
                    mto=from_jid,
                    mbody=f"I'll remind you about '{message}' at {remind_time.strftime('%H:%M')}"
                )
                return

            # If no command matched, show help suggestion
            self.send_message(
                mto=from_jid,
                mbody="I didn't understand that command. Type 'help' to see available commands."
            )

    async def send_reminder(self, to_jid, seconds, message):
        await asyncio.sleep(seconds)
        if to_jid in self.reminders:
            self.send_message(
                mto=to_jid,
                mbody=f"🔔 REMINDER: {message}"
            )
            # Remove the reminder
            self.reminders[to_jid] = [r for r in self.reminders[to_jid] 
                                    if r['message'] != message]

if __name__ == '__main__':
    try:
        xmpp = ReminderBot()
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0199') # XMPP Ping
        xmpp.connect()
        xmpp.process(forever=True)
    except ValueError as e:
        print(f"Error: {e}")
