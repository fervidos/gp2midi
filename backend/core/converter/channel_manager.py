from typing import Dict, List, Set


class ChannelManager:
    """
    Manages allocation of MIDI channels (0-15).
    Channel 9 (index, so 10 in 1-based) is reserved for Percussion.
    """

    PERCUSSION_CHANNEL = 9

    def __init__(self):
        self.used_channels: Set[int] = {self.PERCUSSION_CHANNEL}
        self.track_channel_map: Dict[
            int, List[int]
        ] = {}  # Track ID -> List of Channels

    def allocate_channel(self, track_id: int, count: int = 1) -> List[int]:
        # Try to allocate desired count
        allocated = self._try_allocate(count)
        
        # If failed and count > 1 (e.g. High Fidelity), try fallback to 1
        if not allocated and count > 1:
            print(f"Track {track_id}: Failed to allocate {count} channels. Falling back to Standard (1).")
            allocated = self._try_allocate(1)

        # If still failed (out of channels entirely), fallback to channel 0 (sharing)
        if not allocated:
            print(f"Track {track_id}: OUT OF CHANNELS. Sharing Channel 0.")
            allocated = [0] 

        self.track_channel_map[track_id] = allocated
        return allocated

    def _try_allocate(self, count: int) -> List[int]:
        allocated = []
        # Find contiguous or available block? Just available is fine for now.
        temp_allocation = []
        for ch in range(16):
            if ch == self.PERCUSSION_CHANNEL:
                continue
            if ch not in self.used_channels:
                temp_allocation.append(ch)
                if len(temp_allocation) == count:
                    break
        
        if len(temp_allocation) == count:
            for ch in temp_allocation:
                self.used_channels.add(ch)
            return temp_allocation
        return []

    def get_channels(self, track_id: int) -> List[int]:
        return self.track_channel_map.get(track_id, [0])

    def release_channels(self, track_id: int):
        if track_id in self.track_channel_map:
            for ch in self.track_channel_map[track_id]:
                self.used_channels.discard(ch)
            # Re-add percussion just in case
            self.used_channels.add(self.PERCUSSION_CHANNEL)
            del self.track_channel_map[track_id]
