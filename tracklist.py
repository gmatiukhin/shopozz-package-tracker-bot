import json
from os.path import exists, dirname
from os import makedirs

import logging


class Tracklist:
    tracking_data = dict()
    statuses = dict()
    _file_name = "./data.json"

    def add(self, chat_id, tracking_number):
        tracking_number = str(tracking_number)
        if not self.tracking_data:
            self.tracking_data[tracking_number] = [chat_id]
        elif tracking_number not in list(self.tracking_data.keys()):
            self.tracking_data[tracking_number] = [chat_id]
        elif chat_id not in self.tracking_data[tracking_number]:
            self.tracking_data[tracking_number].append(chat_id)
        else:
            return "I am already tracking your package."

        if tracking_number not in self.statuses:
            self.statuses[tracking_number] = ""

        self.serialize()

        if self.statuses[tracking_number]:
            status = self.statuses[tracking_number]
            return f"""This package is already in my system.\n\n{status}"""

        return "Done, I am tracking your package."

    def remove(self, chat_id, tracking_number):
        tracking_number = str(tracking_number)
        if self.tracking_data and self.tracking_data[tracking_number]:
            if chat_id in self.tracking_data[tracking_number]:
                self.tracking_data[tracking_number].remove(chat_id)
                # Remove the nuber if no-one tracks it
                if (
                    tracking_number in self.statuses
                    and not self.tracking_data[tracking_number]
                ):
                    self.statuses.pop(tracking_number)
                    self.tracking_data.pop(tracking_number)

                self.serialize()
                return "Done, I am no longer tracking your package."
        return "Sorry, I am not tracking your package."

    def update_status(self, tracking_number, status_message, timestamp):
        if tracking_number in self.statuses:
            self.statuses[tracking_number] = (status_message, timestamp)
            self.serialize()

    def status(self, tracking_number):
        return (
            self.statuses[tracking_number][0]
            if tracking_number in self.statuses
            else None
        )

    def timestamp(self, tracking_number):
        return (
            self.statuses[tracking_number][1]
            if tracking_number in self.statuses
            else None
        )

    def serialize(self):
        logging.info("Serializing tracking data")
        makedirs(dirname(self._file_name), exist_ok=True)
        with open(self._file_name, "w") as tracking_file:
            ser = {"trackingData": self.tracking_data, "statuses": self.statuses}
            tracking_file.write(json.dumps(ser, indent=2))

    def deserialize(self):
        logging.info("Deserializing tracking data")
        if exists(self._file_name):
            with open(self._file_name, "r") as tracking_file:
                de = json.loads(tracking_file.read())
                self.tracking_data = de["trackingData"]
                self.statuses = de["statuses"]
