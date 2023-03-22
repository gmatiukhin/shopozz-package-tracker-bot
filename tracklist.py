import json
from os.path import exists, expanduser, dirname
from os import makedirs


class Tracklist:
    user_data = dict()
    statuses = dict()
    _file_name = "./tracking.json"

    def add(self, chat_id, tracking_number):
        data = self.user_data
        chat_id = str(chat_id)
        if not data:
            data[chat_id] = [tracking_number]
        elif chat_id not in list(data.keys()):
            data[chat_id] = [tracking_number]
        elif tracking_number not in data[chat_id]:
            data[chat_id].append(tracking_number)
        else:
            return "I am already tracking your package."

        if tracking_number not in self.statuses:
            self.statuses[tracking_number] = ""
            self.serialize()
        elif self.statuses[tracking_number]:
            status = self.statuses[tracking_number]
            return f"""This package is already in my system.\n\n{status}"""

        return "Done, I am tracking your package."

    def remove(self, chat_id, tracking_number):
        data = self.user_data
        chat_id = str(chat_id)
        if data and data[chat_id]:
            if tracking_number in data[chat_id]:
                data[chat_id].remove(tracking_number)
                if tracking_number in self.statuses:
                    self.statuses.pop(tracking_number)
                self.serialize()
                return "Done, I am no longer tracking your package."
        return "Sorry, I am not tracking your package."

    def update_status(self, tracking_number, status_message):
        if tracking_number in self.statuses:
            self.statuses[tracking_number] = status_message
            self.serialize()

    def status(self, tracking_number):
        return (
            self.statuses[tracking_number] if tracking_number in self.statuses else None
        )

    def serialize(self):
        makedirs(dirname(self._file_name), exist_ok=True)
        with open(self._file_name, "w") as tracking_file:
            ser = {"userData": self.user_data, "statuses": self.statuses}
            tracking_file.write(json.dumps(ser))

    def deserialize(self):
        if exists(self._file_name):
            with open(self._file_name, "r") as tracking_file:
                de = json.loads(tracking_file.read())
                self.user_data = de["userData"]
                self.statuses = de["statuses"]
