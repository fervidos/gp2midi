from typing import List, Set, Dict

class ChannelManager:
    """
    Manages allocation of MIDI channels (0-15).
    Channel 9 (index, so 10 in 1-based) is reserved for Percussion.
    """
    PERCUSSION_CHANNEL = 9
    
    def __init__(self):
        self.used_channels: Set[int] = {self.PERCUSSION_CHANNEL}
        self.track_channel_map: Dict[int, List[int]] = {} # Track ID -> List of Channels

    def allocate_channel(self, track_id: int, count: int = 1) -> List[int]:
        print(f"Allocating {count} channels for track {track_id}. Used: {self.used_channels}")
        allocated = []
        for ch in range(16):
            if ch == self.PERCUSSION_CHANNEL:
                continue
            if ch not in self.used_channels:
                self.used_channels.add(ch)
                allocated.append(ch)
                if len(allocated) == count:
                    break
        print(f"Result: {allocated}")

        
        # If we ran out of channels, we might need to reuse or share.
        # For now, simplistic fallback: Reuse the last allocated or channel 0.
        # In a real "World Class" app, we would implement virtual ports or port switching.
        if len(allocated) < count:
             # Basic fallback: reuse existing or just warn
             pass

        self.track_channel_map[track_id] = allocated
        return allocated

    def get_channels(self, track_id: int) -> List[int]:
        return self.track_channel_map.get(track_id, [0])

    def release_channels(self, track_id: int):
        if track_id in self.track_channel_map:
            for ch in self.track_channel_map[track_id]:
                self.used_channels.discard(ch)
            # Re-add percussion just in case
            self.used_channels.add(self.PERCUSSION_CHANNEL)
            del self.track_channel_map[track_id]
