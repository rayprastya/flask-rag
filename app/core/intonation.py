import parselmouth
import numpy as np
import app.core.tts as tts
import wave
import tempfile
import soundfile as sf

def pitch(input_words, audio_path):
    try:
        # First try to load with soundfile to handle different formats
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            # Read audio data and resample if necessary
            data, samplerate = sf.read(audio_path)
            # Write as WAV with proper headers
            sf.write(temp_wav.name, data, samplerate, format='WAV', subtype='PCM_16')
            
            # Now analyze with Parselmouth
            sound = parselmouth.Sound(temp_wav.name)
            pitch_obj = sound.to_pitch()
            pitch_values = pitch_obj.selected_array['frequency']
            pitch = [x for x in pitch_values if x != 0]

            # Handle case where we have more words than pitch values or vice versa
            min_len = min(len(input_words), len(pitch))
            per_word_pitch = []
            
            for i in range(min_len):
                per_word_pitch.append(f'{input_words[i]}: {pitch[i]:.2f} Hz')
            
            # If we have more words than pitch values, add placeholder values
            for i in range(min_len, len(input_words)):
                per_word_pitch.append(f'{input_words[i]}: N/A')
            
            # Calculate overall pitch from valid values
            overall_average_pitch = np.mean(pitch) if pitch else 0

            return per_word_pitch, overall_average_pitch

    except Exception as e:
        print(f"Error in pitch analysis: {str(e)}")
        # Return placeholder values if analysis fails
        per_word_pitch = [f'{word}: N/A' for word in input_words]
        return per_word_pitch, 0