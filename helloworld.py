#!/usr/bin/env python
"""A very basic example of Adapter Set where we push the alternated strings
"Hello" and "World", by the current timestamp, from the server to the browser.
"""
import threading
import time
import random
import os
import traceback
from lightstreamer_adapter.interfaces.data import DataProvider
from lightstreamer_adapter.server import DataProviderServer

__author__ = "Lightstreamer Srl"
__copyright__ = "Copyright"
__credits__ = ["Lightstreamer Srl"]
__license__ = "Apache Licence 2.0"
__version__ = "1.0.0"
__maintainer__ = "Lightstreamer Srl"
__email__ = "support@lightstreamer.com"
__status__ = "Production"


class HelloWorldDataAdapter(DataProvider):
    """Simple implementation of the DataProvider abstract class, which pushes
    the alternated strings 'Hello' and 'World', followed by the current
    timestamp.
    """

    def __init__(self):
        self.greetings = None
        self.executing = threading.Event()

        # Reference to the provided ItemEventListener instance
        self.listener = None

    def initialize(self, parameters, config_file=None):
        """Invoked to provide initialization information to the Data
        Adapter."""
        # Not needed
        pass

    def set_listener(self, event_listener):
        """Caches the reference to the provided ItemEventListener instance."""
        self.listener = event_listener

    def subscribe(self, item_name):
        """Invoked to request data for the item_name item."""
        if item_name == "greetings":
            self.greetings = threading.Thread(target=self.generate_greetings,
                                              name="Greetings")
            self.greetings.start()

    def unsubscribe(self, item_name):
        """Invoked to end a previous request of data for an item."""
        if item_name == "greetings":
            # Sets the Event flag and wait for 'Greetings' thread termination
            self.executing.clear()
            self.greetings.join()

    def issnapshot_available(self, item_name):
        """Invoked to provide initialization information to the Data Adapter.
        """
        # No snapshot available
        return False

    def generate_greetings(self):
        """Target method of the 'Greetings' Thread."""
        random.seed()
        counter = 0
        while not self.executing.is_set():
            # Prepares the events dictionary
            events = {"message": 'Hello' if counter % 2 == 0 else 'World',
                      "timestamp": time.strftime("%a, %d %b %Y %H:%M:%S")}
            counter += 1

            # Sends updates to the Lightstreamer Server
            self.listener.update("greetings", events, False)

            # Randomly generated pause
            time.sleep(random.uniform(1, 2))


def main():
    """Module Entry Point."""

    # Host and request/reply port of the Proxy Adapter
    address = ("localhost", 6663)

    # Creates a new instance of the Remote Data Adapter
    data_adapter = HelloWorldDataAdapter()

    # Creating and starting the DataProviderServer
    dataprovider_server = DataProviderServer(data_adapter, address)
    dataprovider_server.start()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        os._exit(0)

    # after calling dataprovider_server.start()
    # we have to keep the main thread active in some way (see the docs)
    shutdown_event = threading.Event()
    shutdown_event.wait()
