Current plan:

This will be a library that can be called from python. It will be responsible for reading data from
the injected dll and converting that into proto format. It will also coordinate and dispatch
grpc calls to all bots which register themselves.

Python pseudocode:
```
import RLBotSharp

RLBotSharp.init()

RLBotSharp.register_bot(name="test", playerIndex=0, port=22141)
RLBotSharp.register_bot(name="test2", playerIndex=1, port=22101)
```
