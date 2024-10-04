import os
from google.cloud import texttospeech, speech
import wave

# Set the environment variable for authentication
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/your/service-account-file.json'

def synthesize_speech(text, output_filename, voice_type='MALE', speed=1.0):
    # Initialize the client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request
    if voice_type == 'MALE':
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D",  # male voice
        )
    elif voice_type == 'FEMALE':
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-F",  # female voice
        )
    elif voice_type == 'HISPANIC_MALE':
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-US",
            name="es-US-Wavenet-B",  # Hispanic male voice
        )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speed
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Write the response to the output file
    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
    print(f'Audio content written to file {output_filename}')

def transcribe_speech(input_filename):
    # Initialize the client
    client = speech.SpeechClient()

    # Load the audio file into memory
    with wave.open(input_filename, "rb") as audio_file:
        frames = audio_file.readframes(audio_file.getnframes())
        audio_content = frames

    audio = speech.RecognitionAudio(content=audio_content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    # Print the transcription
    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

# List of phonemes and their example translations
phonemes = {
    'AA': 'odd' 
    # 'AE': 'at', 'AH': 'hut', 'AO': 'ought', 'AW': 'cow',
    # 'AY': 'hide', 'B': 'be', 'CH': 'cheese', 'D': 'dee', 'DH': 'thee',
    # 'EH': 'Ed', 'ER': 'hurt', 'EY': 'ate', 'F': 'fee', 'G': 'green',
    # 'HH': 'he', 'IH': 'it', 'IY': 'eat', 'JH': 'gee', 'K': 'key',
    # 'L': 'lee', 'M': 'me', 'N': 'knee', 'NG': 'ping', 'OW': 'oat',
    # 'OY': 'toy', 'P': 'pee', 'R': 'read', 'S': 'sea', 'SH': 'she',
    # 'T': 'tea', 'TH': 'theta', 'UH': 'hood', 'UW': 'two', 'V': 'vee',
    # 'W': 'we', 'Y': 'yield', 'Z': 'zee', 'ZH': 'seizure'
}

# Generate and save .wav files for each phoneme
for phoneme, example in phonemes.items():
    filename = f"{phoneme}.wav"
    synthesize_speech(example, filename, voice_type='MALE', speed=1.0)

# Transcribe the generated .wav files
# for phoneme in phonemes.keys():
#     filename = f"{phoneme}.wav"
#     print(f"Transcribing {filename}:")
#     transcribe_speech(filename)