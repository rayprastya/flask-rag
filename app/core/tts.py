from google.cloud import texttospeech

# Sample input
# weatherfilename = 'output.wav'
# voice_name = 'en-US-Wavenet-D'
# input_text = "Hi, this is Jenny Multilingual"

def text_to_speech(voice_name, input_text, output_filename):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=voice_name.split('-')[0],
        name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio saved to {output_filename}")

# to test the function to perform text-to-speech and save to a WAV file
# text_to_speech(voice_name, input_text, weatherfilename)

