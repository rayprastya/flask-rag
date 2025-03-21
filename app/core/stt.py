import os
from google.cloud import speech
import wave
import soundfile as sf
import tempfile
import numpy as np
from scipy import signal

# Set up Google Cloud credentials
# Make sure to set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path of your service account key file
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"

def validate_and_convert_audio(filename):
    """Validate and convert audio to proper format for Google Speech-to-Text."""
    try:
        # Try to read with soundfile first
        data, samplerate = sf.read(filename)
        
        # Check if we have valid audio data
        if data.size == 0:
            raise Exception("Empty audio data")
            
        # Check if audio is too quiet
        if np.max(np.abs(data)) < 0.01:
            raise Exception("Audio signal is too weak. Please speak louder or check your microphone.")
        
        # Convert to mono if stereo
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        
        # Remove silent parts from the beginning and end
        threshold = 0.01
        mask = np.abs(data) > threshold
        start = np.argmax(mask)
        end = len(data) - np.argmax(mask[::-1])
        if start < end:  # Only trim if we found valid start/end points
            data = data[start:end]
        
        # Check if we have enough audio data after trimming
        if len(data) < samplerate * 0.1:  # Less than 0.1 seconds
            raise Exception("Audio is too short after removing silence. Please speak for a longer duration.")
        
        # Ensure proper sample rate (16kHz for best results with Google STT)
        target_samplerate = 16000
        if samplerate != target_samplerate:
            # Calculate the number of samples for the target duration
            target_samples = int(len(data) * target_samplerate / samplerate)
            # Use scipy.signal.resample instead of soundfile.resample
            data = signal.resample(data, target_samples)
        
        # Normalize audio data
        max_val = np.max(np.abs(data))
        if max_val < 1e-10:  # Avoid division by zero with a small threshold
            raise Exception("Audio signal is too weak after processing. Please speak louder.")
        data = data / max_val
        
        # Apply a small amount of pre-emphasis to improve speech clarity
        pre_emphasis = 0.97
        emphasized_data = np.append(data[0], data[1:] - pre_emphasis * data[:-1])
        
        # Save as WAV with proper format
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            # Ensure the data is float32 and properly scaled
            emphasized_data = emphasized_data.astype(np.float32)
            # Clip to prevent any potential overflow
            emphasized_data = np.clip(emphasized_data, -1.0, 1.0)
            # Write as 16-bit PCM WAV
            sf.write(
                temp_wav.name, 
                emphasized_data, 
                target_samplerate, 
                format='WAV',
                subtype='PCM_16'
            )
            return temp_wav.name
            
    except Exception as e:
        print(f"Error in audio validation: {str(e)}")
        raise Exception(f"Audio format validation failed: {str(e)}")

def recognize_from_microphone(filename):
    """
    Transcribe speech from audio file using Google Speech-to-Text.
    
    Args:
        filename: Path to the audio file
        
    Returns:
        str: Transcribed text or empty string if transcription fails
        
    Raises:
        Exception: If audio processing or transcription fails
    """
    # Validate and convert audio
    validated_file = validate_and_convert_audio(filename)
    try:
        client = speech.SpeechClient()

        # Read the validated audio file
        with wave.open(validated_file, 'rb') as audio_file:
            content = audio_file.readframes(audio_file.getnframes())
            sample_rate = audio_file.getframerate()

        # Configure recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code="en-US",
            model='default',  # Use enhanced model for better accuracy
            use_enhanced=True,
            enable_automatic_punctuation=True
        )

        audio = speech.RecognitionAudio(content=content)

        # Make the request with timeout
        response = client.recognize(config=config, audio=audio)

        # Clean up temporary file
        if os.path.exists(validated_file):
            os.unlink(validated_file)

        if response.results:
            recognized_text = response.results[0].alternatives[0].transcript
            return recognized_text
        else:
            print("No speech could be recognized")
            return ""

    except Exception as e:
        print(f"Error in speech recognition: {str(e)}")
        if os.path.exists(validated_file):
            os.unlink(validated_file)
        raise Exception(f"Speech recognition failed: {str(e)}")

# recognize_from_microphone(filename)