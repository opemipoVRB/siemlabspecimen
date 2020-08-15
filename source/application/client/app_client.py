#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pandas as pd
import random

import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time


class Client:
    """
    Client Interface

    """

    def __init__(self, ):
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp("ws://localhost:9000/",
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.mode = "initialize"

        self.ws = ws
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_message(self, message):
        print(message)
        return message

    def on_error(self, error):
        return error

    def on_close(self):
        print("### closed ###")

    def fetch_data(self):
        filename = '../../../datastore/kddcup.data_demo.csv'
        n = sum(1 for line in open(filename)) - 1  # number of records in file (excludes header)
        s = random.randint(500, 1000)  # desired sample size
        print("Number of samples: ", s)
        skip = sorted(
            random.sample(range(1, n + 1), n - s))  # the 0-indexed header will not be included in the skip list
        data = pd.read_csv(filename, skiprows=skip)

        json_data = data.to_json(orient='records')[1:-1].replace('},{', '} {')

        return json_data

    def run(self, *args):
        global driver
        driver = True
        while driver:
            try:
                time.sleep(1)
                print("Sending Traffic Simulation Data")
                self.ws.send(json.dumps(self.fetch_data()))

            except KeyboardInterrupt:
                driver = False
        time.sleep(1)
        self.ws.close()
        print("thread terminating...")

    def on_open(self):
        if self.mode == "initialize":
            self.ws.send(json.dumps({"id": "Device 2019"}))
            self.mode = "run"
        if self.mode == "run":
            thread.start_new_thread(self.run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    onyx_client = Client()
