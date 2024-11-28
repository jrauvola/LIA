import parselmouth
import numpy as np
from google.cloud import storage
import io
from pydub import AudioSegment


def audio_segment_to_numpy_array(audio_segment):
    """Convert pydub AudioSegment to numpy array with correct format for Parselmouth."""
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float64)

    # Convert stereo to mono if needed
    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    # No normalization step
    return samples, audio_segment.frame_rate

def extract_audio_features(gcs_uri, answer_index):
    """
    Extract audio features from a WebM file stored in GCS and return them as a dictionary.
    """
    try:
        # Load audio from GCS
        bucket_name = gcs_uri.split('/')[2]
        blob_name = '/'.join(gcs_uri.split('/')[3:])
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        audio_bytes = io.BytesIO()
        blob.download_to_file(audio_bytes)
        audio_bytes.seek(0)
        webm_audio = AudioSegment.from_file(audio_bytes, format="webm")

        # Convert audio segment to numpy array
        samples, sample_rate = audio_segment_to_numpy_array(webm_audio)
        sound = parselmouth.Sound(samples, sampling_frequency=float(sample_rate))

        # Extract features
        features = {}
        pitch = sound.to_pitch()
        intensity = sound.to_intensity()
        formants = sound.to_formant_burg(max_number_of_formants=5.0, maximum_formant=5500.0)

        # 1. Average Bandwidth of F1
        bandwidth_values = []
        for t in np.arange(0, sound.duration, 0.01):  # every 10 ms
            bandwidth = formants.get_bandwidth_at_time(1, t, parselmouth.FormantUnit.HERTZ)
            if not np.isnan(bandwidth):
                bandwidth_values.append(bandwidth)
        features['avgBand1'] = np.mean(bandwidth_values) if bandwidth_values else 0

        # 2. Percentage of unvoiced frames
        pitch_values = pitch.selected_array['frequency']
        features['unvoiced_percent'] = float(np.sum(pitch_values == 0) / len(pitch_values) * 100)

        # 3. F1 Standard Deviation
        f1_values = [formants.get_value_at_time(1, t, parselmouth.FormantUnit.HERTZ)
                     for t in np.arange(0, sound.duration, 0.01) if
                     not np.isnan(formants.get_value_at_time(1, t, parselmouth.FormantUnit.HERTZ))]
        features['f1STD'] = float(np.std(f1_values) if f1_values else 0)

        # Calculate F3/F1 ratio
        f3_values = [formants.get_value_at_time(3, t, parselmouth.FormantUnit.HERTZ)
                     for t in np.arange(0, sound.duration, 0.01) if
                     not np.isnan(formants.get_value_at_time(3, t, parselmouth.FormantUnit.HERTZ))]
        f1_mean = np.mean(f1_values) if f1_values else 0
        f3_mean = np.mean(f3_values) if f3_values else 0
        features['f3meanf1'] = float(f3_mean / f1_mean if f1_mean != 0 else 0)

        # 4. Mean Intensity
        intensityMean = intensity.get_average()

        # Transform intensityMean from 222-253 to 25-71
        transformed_intensity_mean = ((intensityMean - 222) / (253 - 222)) * (61 - 25) + 25
        features['intensityMean'] = float(transformed_intensity_mean)

        # 5. Pause Duration Features
        intensity_values = intensity.values[0]
        time_step = intensity.time_step
        silence_threshold = intensityMean - 12  # 12 dB below mean intensity

        is_silence = intensity_values < silence_threshold
        silence_changes = np.diff(is_silence.astype(int))
        silence_starts = np.where(silence_changes == 1)[0]
        silence_ends = np.where(silence_changes == -1)[0]

        # Handle boundary conditions for silence
        if len(silence_starts) > 0 and len(silence_ends) > 0:
            if is_silence[0]:
                silence_starts = np.insert(silence_starts, 0, 0)
            if is_silence[-1]:
                silence_ends = np.append(silence_ends, len(intensity_values) - 1)

            min_len = min(len(silence_starts), len(silence_ends))
            silence_starts = silence_starts[:min_len]
            silence_ends = silence_ends[:min_len]

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
        return {
            'avgBand1': 0.0,
            'unvoiced_percent': 0.0,
            'f1STD': 0.0,
            'intensityMean': 0.0,
            'avgDurPause': 0.0,
            'maxDurPause': 0.0,
            'audio_length': 0.0,
            'f3meanf1': 0.0  # Default value for f3meanf1
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
        'audio_length': 0.0,
        'f3meanf1': 0.0  # Added initialization for f3meanf1
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