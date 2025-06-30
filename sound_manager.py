import pyxel

#* Channel references:
# 0: Background music
# 1: Sound effects
# 2: [Not used yet]
# 3: [Not used yet]

#* Sounds references:
# 0: Basic Up
# 1: Basic Down
# 2: Basic background
# 3: Basic Move

class SoundManager:
    def __init__(self):
        self.channels = [{"playing":False, "sound_id":None, "loop":False, "priority":False}] * 4

    def play_sound(self, channel: int, sound_id: int, loop: bool = False, reset: bool = False, priority: bool = True):
        """
        Play a sound on the specified channel.

        Parameters:
            channel (int): The channel to play the sound on.
            sound_id (int): The ID of the sound to play.
        """
        go_on = True
        if self.channels[channel]["priority"] and not priority:
            # If the channel is already playing a sound with priority and the new sound is not, do not play the new sound
            go_on = False

        if go_on:
            if sound_id != self.channels[channel]["sound_id"] or reset:
                self.channels[channel]["playing"] = False
            self.channels[channel] = {"playing": self.channels[channel]["playing"], "sound_id": sound_id, "loop": loop, "priority": priority}

    def update_channels(self):
        for i in range(4):
            value = self.channels[i]
            if value["sound_id"] != None and not value["playing"]:
                value["playing"] = True
                pyxel.play(i, value["sound_id"], loop=value["loop"])


