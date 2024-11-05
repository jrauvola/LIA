import os
import parselmouth
import numpy as np
import moviepy.editor as mp
import pandas as pd
from tqdm import tqdm
import time

# Directory containing the video files
video_directory = r"C:\Users\benth\Desktop\capstone\smile_test"

# Get a list of all .avi files in the directory
video_files = [f for f in os.listdir(video_directory) if f.endswith('.avi')]

# Create a list to store results for all videos
all_results = []


def extract_prosodic_features(sound):
    feature_times = {}
    start = time.time()
    features = {}  # Initialize features dictionary at start

    # Get pitch object
    pitch = sound.to_pitch()
    feature_times['pitch'] = time.time() - start

    # Get intensity object
    intensity = sound.to_intensity()
    feature_times['intensity'] = time.time() - start

    # Get formant object using recommended parameters
    formants = sound.to_formant_burg(
        time_step=None,  # auto
        max_number_of_formants=5.0,
        maximum_formant=5500.0,
        window_length=0.025,
        pre_emphasis_from=50.0
    )
    feature_times['formants'] = time.time() - start

    # Extract specific features

    # 1. Get bandwidth of first formant (F1)
    bandwidth_values = []
    for t in np.arange(0, sound.duration, 0.01):  # sample every 10ms
        bandwidth = formants.get_bandwidth_at_time(1, t, parselmouth.FormantUnit.HERTZ)
        if not np.isnan(bandwidth):
            bandwidth_values.append(bandwidth)

    avgBand1 = np.mean(bandwidth_values) if bandwidth_values else 0

    # 2. Percentage of unvoiced frames
    pitch_values = pitch.selected_array['frequency']
    unvoiced = np.sum(pitch_values == 0) / len(pitch_values) * 100

    # 3. F1 Standard Deviation
    f1_values = []
    for t in np.arange(0, sound.duration, 0.01):  # every 10ms
        f1 = formants.get_value_at_time(1, t, parselmouth.FormantUnit.HERTZ)
        if not np.isnan(f1):
            f1_values.append(f1)
    f1STD = np.std(f1_values) if f1_values else 0

    # 4. Mean Intensity
    intensityMean = intensity.get_average()

    # 5. Pause Duration Features using intensity-based method
    intensity_values = intensity.values[0]  # Get intensity values
    time_step = intensity.time_step  # Get time step between measurements
    silence_threshold = intensityMean - 12  # 12dB below mean intensity
    min_pause_duration = 0.28  # Minimum pause duration in seconds
    merge_threshold = 0.06  # Maximum gap between pauses to merge them

    # Check for silence at boundaries
    starts_with_silence = intensity_values[0] < silence_threshold
    ends_with_silence = intensity_values[-1] < silence_threshold

    # Find regions below threshold
    is_silence = intensity_values < silence_threshold
    silence_changes = np.diff(is_silence.astype(int))
    silence_starts = np.where(silence_changes == 1)[0]
    silence_ends = np.where(silence_changes == -1)[0]

    # Handle boundary conditions
    if starts_with_silence and len(silence_ends) > 0:
        silence_starts = np.insert(silence_starts, 0, 0)
    if ends_with_silence and len(silence_starts) > 0:
        silence_ends = np.append(silence_ends, len(intensity_values) - 1)

    # Calculate and merge pauses
    if len(silence_starts) > 0 and len(silence_ends) > 0:
        # Ensure matching starts and ends
        if len(silence_starts) > len(silence_ends):
            silence_starts = silence_starts[:-1]
        if len(silence_ends) > len(silence_starts):
            silence_ends = silence_ends[1:]

        # Initialize lists for merged pauses
        merged_starts = [silence_starts[0]]
        merged_ends = []

        # Merge close pauses
        for i in range(1, len(silence_starts)):
            gap_duration = (silence_starts[i] - silence_ends[i - 1]) * time_step
            if gap_duration < merge_threshold:
                # Skip this start, continue current pause
                continue
            else:
                # End previous pause and start new one
                merged_ends.append(silence_ends[i - 1])
                merged_starts.append(silence_starts[i])

        # Add final end
        merged_ends.append(silence_ends[-1])

        # Calculate durations and filter by minimum duration
        pause_durations = (np.array(merged_ends) - np.array(merged_starts)) * time_step
        valid_pauses = pause_durations[pause_durations >= min_pause_duration]

        avgDurPause = np.mean(valid_pauses) if len(valid_pauses) > 0 else 0
        maxDurPause = np.max(valid_pauses) if len(valid_pauses) > 0 else 0
    else:
        avgDurPause = 0
        maxDurPause = 0

    # 6. Ratio of F3 mean to F1 mean
    f3_values = []
    for t in np.arange(0, sound.duration, 0.01):
        f3 = formants.get_value_at_time(3, t, parselmouth.FormantUnit.HERTZ)
        if not np.isnan(f3):
            f3_values.append(f3)

    f1_mean = np.mean(f1_values) if f1_values else 0
    f3_mean = np.mean(f3_values) if f3_values else 0
    f3mean1 = f3_mean / f1_mean if f1_mean != 0 else 0

    feature_times['total'] = time.time() - start

    features = {
        'avgBand1': avgBand1,
        'unvoiced_percent': unvoiced,
        'f1STD': f1STD,
        'intensityMean': intensityMean,
        'avgDurPause': avgDurPause,
        'maxDurPause': maxDurPause,
        'f3mean1': f3mean1
    }

    return features, feature_times


for video_file in tqdm(video_files, desc="Processing videos"):
    print(f"\nProcessing {video_file}...")
    start_time = time.time()

    # Convert video to audio
    video_path = os.path.join(video_directory, video_file)
    audio_path = os.path.join(video_directory, f"temp_audio_{video_file}.wav")

    try:
        # Extract audio from video
        print("Extracting audio...")
        t0 = time.time()
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        print(f"Audio extraction took {time.time() - t0:.2f} seconds")

        # Load audio and extract features
        print("Extracting features...")
        t0 = time.time()
        sound = parselmouth.Sound(audio_path)
        features, timing = extract_prosodic_features(sound)
        print(f"Feature extraction took {time.time() - t0:.2f} seconds")

        # Add filename to results
        features['filename'] = video_file
        all_results.append(features)

        # Clean up temporary audio file
        os.remove(audio_path)

        # Print timing summary
        print(f"\nTiming breakdown for {video_file}:")
        for feature, time_taken in timing.items():
            print(f"{feature}: {time_taken:.2f} seconds")

    except Exception as e:
        print(f"Error processing {video_file}: {str(e)}")
        continue

# Convert results to DataFrame
results_df = pd.DataFrame(all_results)

# Save results to CSV
output_path = os.path.join(video_directory, 'prosodic_features.csv')
results_df.to_csv(output_path, index=False)

print("\nProcessing complete!")
print(f"Results saved to: {output_path}")
print("\nResults Summary:")
print(results_df.to_string())