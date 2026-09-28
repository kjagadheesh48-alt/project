class MockStreamManager:
    def __init__(self):
        self.active_streams = {}
        
    def connect(self, camera_id: str, url: str):
        self.active_streams[camera_id] = {"status": "connected", "url": url}
        
    def disconnect(self, camera_id: str):
        if camera_id in self.active_streams:
            del self.active_streams[camera_id]

    def get_status(self, camera_id: str):
        return self.active_streams.get(camera_id, {"status": "disconnected"})

stream_manager = MockStreamManager()
