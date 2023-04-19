import threading
import asyncio
import websockets
from assistant import AssistantEngine

PORT = 8765

assistant = AssistantEngine()

async def custom_loop(websocket, path):
    while True:
        #msg = await websocket.recv()
        #print(msg)
        if assistant.shared_data != None:
            await websocket.send(str(assistant.shared_data))
            print("Sent: {}".format(assistant.shared_data))
            assistant.shared_data = None
        await asyncio.sleep(1)

class WebSocketThread(threading.Thread):
    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(custom_loop, "localhost", PORT)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        
class AssistantThread(threading.Thread):
    def run(self):
        assistant.run()

# Create and start the WebSocket thread
websocket_thread = WebSocketThread()
websocket_thread.start()

assistant_thread = AssistantThread()
assistant_thread.start()

websocket_thread.join()
assistant_thread.join()
