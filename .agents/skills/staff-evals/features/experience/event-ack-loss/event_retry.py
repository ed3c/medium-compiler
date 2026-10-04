"""Controlled local fixture. No network or production writes."""
import json

class Sink:
    def __init__(self):
        self.events = []
        self.calls = 0

    def publish(self, event):
        self.calls += 1
        self.events.append(dict(event))
        if self.calls == 1:
            raise TimeoutError('acknowledgement lost')
        return {'accepted': True}

def deliver(sink, event):
    for attempt in range(2):
        try:
            return sink.publish(event)
        except TimeoutError:
            if attempt == 1:
                raise

if __name__ == '__main__':
    sink = Sink()
    response = deliver(sink, {'id': 'evt-42', 'payload': 'ready'})
    print(json.dumps({'response': response, 'calls': sink.calls, 'events': sink.events}))
