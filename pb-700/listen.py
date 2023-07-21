import pyaudio
import audioop
import wave

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENCE_THRESHOLD = 1000  # Adjust this value based on your environment and microphone sensitivity
SILENCE_SECONDS = 1  # Maximum silence in seconds

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open audio stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Waiting for non silence...")

# silent_frames = 0
# window_frames = int( RATE/CHUNK*0.3 )
# print( window_frames )

while True:
    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)  # Calculate root mean square (RMS) to measure volume
    if rms > SILENCE_THRESHOLD:
        break

print( "Found audio, recording until silence..." )

# Variables to track silence duration
silent_frames = 0
max_silent_frames = int(RATE / CHUNK * SILENCE_SECONDS)

frames = []
# Continuously record audio until silence is detected
while silent_frames < max_silent_frames:
    data = stream.read(CHUNK)
    frames.append(data)

    # Check for silence
    rms = audioop.rms(data, 2)  # Calculate root mean square (RMS) to measure volume
    if rms < SILENCE_THRESHOLD:
        silent_frames += 1
    else:
        silent_frames = 0

print("Silence detected. Finished recording.")

# frames = [audioop.mul(data, 2, 2.0) for data in frames]

# Stop recording and close the audio stream
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded audio to a file (e.g., WAV)
output_filename = "recorded_audio.wav"
wf = wave.open(output_filename, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(2) #audio.get_sample_size(FORMAT)
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"Audio saved to {output_filename}")
