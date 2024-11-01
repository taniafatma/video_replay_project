import subprocess
import numpy as np
from scipy.signal import find_peaks
from datetime import datetime
import os
import multiprocessing
import json

# YouTube Live Stream URL
youtube_url = "https://www.youtube.com/watch?v=QsX6VNcselc"

# Default configuration values
DEFAULT_CLIP_DURATION = 20  # Duration of each clip (in seconds)
THRESHOLD = 0.9  # Threshold for spike detection
CHUNK_SIZE = 4096  # Buffer size for audio data
PRE_SPIKE_OFFSET = 5  # Start clip 5 seconds before spike
MINIMUM_GAP_BETWEEN_CLIPS = 20  # Minimum gap between clips to avoid overlap

def get_stream_url(format_code):
    command = ['yt-dlp', '-f', format_code, '-g', youtube_url]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error getting stream URL: {result.stderr}")
        return None
    return result.stdout.strip()

def get_audio_sample_rate(stream_url):
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'stream=sample_rate',
        '-of', 'json', stream_url
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error getting sample rate: {result.stderr}")
        return None

    try:
        info = json.loads(result.stdout)
        return int(info['streams'][0]['sample_rate'])
    except (KeyError, IndexError, ValueError) as e:
        print(f"Failed to parse sample rate: {e}")
        return None

def stream_audio_to_buffer(stream_url, audio_queue, sample_rate):
    command = [
        'ffmpeg',
        '-i', stream_url,
        '-f', 's16le',
        '-acodec', 'pcm_s16le',
        '-ar', str(sample_rate),
        '-ac', '1',
        '-'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    try:
        while True:
            data = process.stdout.read(CHUNK_SIZE)
            if not data:
                break
            audio_queue.put(data)
    except Exception as e:
        print(f"Streaming error: {e}")
    finally:
        process.terminate()

def detect_audio_spikes(audio_queue, stream_url, sample_rate, clip_duration=DEFAULT_CLIP_DURATION):
    position = 0
    last_clip_time = -MINIMUM_GAP_BETWEEN_CLIPS  # Initialize to ensure the first clip is allowed

    while True:
        try:
            if not audio_queue.empty():
                audio_data = audio_queue.get()

                # Convert raw PCM data to numpy array (16-bit PCM)
                chunk = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                chunk = np.abs(chunk) / 32768.0  # Normalize values between 0 and 1

                # Detect spikes
                peaks, _ = find_peaks(chunk, height=THRESHOLD)

                if peaks.size > 0:
                    global_peaks = peaks + position
                    detected_times = [p / sample_rate for p in global_peaks]
                    print(f"Detected spikes at: {detected_times} seconds")

                    # Trim the stream clip for each detected peak, avoiding overlap
                    for peak in global_peaks:
                        spike_time = peak / sample_rate
                        if spike_time - last_clip_time >= MINIMUM_GAP_BETWEEN_CLIPS:
                            start_time = max(0, spike_time - PRE_SPIKE_OFFSET)
                            trim_stream_clip(stream_url, start_time, clip_duration)
                            last_clip_time = spike_time  # Update last clip time

                position += len(chunk)
        except Exception as e:
            print(f"Detection error: {e}")

def trim_stream_clip(stream_url, start_time, duration=DEFAULT_CLIP_DURATION):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"video_chunks/clip_{timestamp}.mp4"
    os.makedirs("video_chunks", exist_ok=True)
    
    command = [
        'ffmpeg',
        '-i', stream_url,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-y',
        output_file
    ]
    
    result = subprocess.run(command)
    if result.returncode == 0:
        print(f"Saved clip to {output_file}")
    else:
        print(f"Error saving clip: {result.stderr}")

if __name__ == "__main__":
    print("Getting stream URLs...")
    stream_url_audio = get_stream_url('bestaudio')
    if not stream_url_audio:
        print("Audio stream URL could not be retrieved. Exiting.")
        exit(1)

    stream_url_video = get_stream_url('best')
    if not stream_url_video:
        print("Video stream URL could not be retrieved. Exiting.")
        exit(1)

    # Detect sample rate from audio stream
    sample_rate = get_audio_sample_rate(stream_url_audio)
    if sample_rate is None:
        print("Failed to detect sample rate. Exiting.")
        exit(1)

    print(f"Detected sample rate: {sample_rate} Hz")

    # Initialize a multiprocessing queue
    audio_queue = multiprocessing.Queue()

    # Process for streaming audio to buffer
    stream_process = multiprocessing.Process(target=stream_audio_to_buffer, args=(stream_url_audio, audio_queue, sample_rate))
    # Process for detecting audio spikes
    detect_process = multiprocessing.Process(target=detect_audio_spikes, args=(audio_queue, stream_url_video, sample_rate, DEFAULT_CLIP_DURATION))

    stream_process.start()
    detect_process.start()

    try:
        # Wait for processes to complete
        stream_process.join()
        detect_process.join()
    except KeyboardInterrupt:
        print("Terminating processes...")
    finally:
        stream_process.terminate()
        detect_process.terminate()
