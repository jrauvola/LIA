import parselmouth
import numpy as np
from google.cloud import storage
import io
import tempfile
import soundfile as sf
import time


def extract_audio_features(gcs_uri, answer_index):
    """
    Extract audio features from a WebM file stored in GCS and return them as a dictionary
    """
    try:
        # Parse bucket and blob name from GCS URI
        bucket_name = gcs_uri.split('/')[2]
        blob_name = '/'.join(gcs_uri.split('/')[3:])

        # Initialize GCS client and get the file
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_audio:
            blob.download_to_filename(temp_audio.name)
            sound = parselmouth.Sound(temp_audio.name)

            # Extract features
            features = {}

            # Get pitch object
            pitch = sound.to_pitch()

            # Get intensity object
            intensity = sound.to_intensity()

            # Get formant object
            formants = sound.to_formant_burg(
                time_step=None,
                max_number_of_formants=5.0,
                maximum_formant=5500.0,
                window_length=0.025,
                pre_emphasis_from=50.0
            )

            # Extract specific features
            # 1. Average first frequency band
            spectrum = sound.to_spectrum()
            features['avgBand1'] = float(spectrum.get_band_energy(0, 500))

            # 2. Percentage of unvoiced frames
            pitch_values = pitch.selected_array['frequency']
            features['unvoiced_percent'] = float(np.sum(pitch_values == 0) / len(pitch_values) * 100)

            # 3. F1 Standard Deviation
            f1_values = []
            for t in np.arange(0, sound.duration, 0.01):
                f1 = formants.get_value_at_time(1, t, parselmouth.FormantUnit.HERTZ)
                if not np.isnan(f1):
                    f1_values.append(f1)
            features['f1STD'] = float(np.std(f1_values) if f1_values else 0)

            # 4. Mean Intensity
            features['intensityMean'] = float(intensity.get_average())

            # 5. Pause Duration Features
            intensity_values = intensity.values[0]
            time_step = intensity.time_step
            silence_threshold = features['intensityMean'] - 12

            # Find silence regions
            is_silence = intensity_values < silence_threshold
            silence_changes = np.diff(is_silence.astype(int))
            silence_starts = np.where(silence_changes == 1)[0]
            silence_ends = np.where(silence_changes == -1)[0]

            if len(silence_starts) > 0 and len(silence_ends) > 0:
                pause_durations = (silence_ends - silence_starts) * time_step
                valid_pauses = pause_durations[pause_durations >= 0.28]
                features['avgDurPause'] = float(np.mean(valid_pauses) if len(valid_pauses) > 0 else 0)
                features['maxDurPause'] = float(np.max(valid_pauses) if len(valid_pauses) > 0 else 0)
            else:
                features['avgDurPause'] = 0.0
                features['maxDurPause'] = 0.0

            # Add audio length
            features['audio_length'] = float(sound.duration)

            return features

    except Exception as e:
        print(f"Error extracting audio features: {str(e)}")
        # Return default values if extraction fails
        return {
            'avgBand1': 0.0,
            'unvoiced_percent': 0.0,
            'f1STD': 0.0,
            'intensityMean': 0.0,
            'avgDurPause': 0.0,
            'maxDurPause': 0.0,
            'audio_length': 0.0
        }


def initialize_audio_features():
    """Initialize the audio_features list with empty dictionaries"""
    return [{
        'avgBand1': 0.0,
        'unvoiced_percent': 0.0,
        'f1STD': 0.0,
        'intensityMean': 0.0,
        'avgDurPause': 0.0,
        'maxDurPause': 0.0,
        'audio_length': 0.0
    } for _ in range(5)]


def update_audio_features(interview_instance, gcs_uri, answer_index):
    """Update the audio_features list in the interview instance"""
    if not hasattr(interview_instance, 'audio_features') or not interview_instance.audio_features:
        interview_instance.audio_features = initialize_audio_features()

    features = extract_audio_features(gcs_uri, answer_index)
    if features:
        interview_instance.audio_features[answer_index] = features
        return True
    return False