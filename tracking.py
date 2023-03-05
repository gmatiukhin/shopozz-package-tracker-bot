import json
from os.path import exists, expanduser

class Tracklist:
    _data = dict()
    _file_path = expanduser('~') + "/tracking.json"

    def add(self, chat_id, tracking_number):
        data = self._data
        if not data:
            data[chat_id] = [tracking_number]
        elif chat_id not in list(data.keys()):
            data[chat_id] = [tracking_number]
        else:
            data[chat_id].append(tracking_number)

    def remove(self, chat_id, tracking_number):
        data = self._data
        if data and data[chat_id]:
            if tracking_number in data[chat_id]:
                data[chat_id].remove(tracking_number)

    def serialize(self):
        with open(self._file_path, "w") as tracking_file:
            tracking_file.write(json.dumps(self._data))

    def deserialize(self):
        if exists(self._file_path):
            with open(self._file_path, "r") as tracking_file:
                self._data = json.loads(tracking_file.read())

    def data(self):
        return self._data
