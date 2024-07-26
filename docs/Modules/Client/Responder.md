# Responder

All it does is pulling the API end to figure out whether there is any audio have not been played, if not, use the url to
play it.

So the code is very simple and straight forward, it is just a loop to check the API, and play the audio.

code have a `play_speech.py`, all other files are some extent utilities functions.

For the hardware part, it only requires a speaker, so it can be running on a laptop, or working with a Raspberry Pi.