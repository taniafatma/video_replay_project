# Video Stream Spike Detection and Chunk Extraction

## Description
This program detects audio spikes in a live YouTube video stream and creates video clips (video chunks) each time a spike is detected. Video segments are only generated when the time interval between detected spikes is at least 20 seconds, avoiding overlapping video clips.

### General Workflow
1. **Fetch Stream URL**: The program retrieves audio and video stream URLs from YouTube using yt-dlp.
2. **Determine Audio Sample Rate**: The sample rate is obtained from the audio stream, which is used for spike analysis.
3. **Streaming and Spike Detection**: The program streams audio and detects spikes within the audio data.
4. **Video Clipping**: When a spike is detected, a video clip is created, starting a few seconds before the spike and lasting for a defined duration.
5. **Avoid Overlapping Clips**: The program ensures that video chunks are not created within a 20-second range of the previous clip.

### Input
- **YouTube URL**: The YouTube video URL to be analyzed (set in the variable `youtube_url`).
- **Spike Detection Configuration**: Configurations such as clip duration, spike threshold, audio chunk size, pre-spike offset, and minimum gap between clips.

### Output
- **Video Clips**: Video segments in `.mp4` format are saved in the `video_chunks` folder, with filenames generated randomly.

---

## Program Structure and Function Roles

### Main Functions

1. **`get_stream_url(format_code)`**
   - Retrieves the YouTube stream URL for audio or video according to the provided format code.
   - **Input**: `format_code` (the yt-dlp format code, e.g., 'bestaudio' or 'best').
   - **Output**: The stream URL to be used for audio or video streaming.

2. **`get_audio_sample_rate(stream_url)`**
   - Gets the audio sample rate from the stream URL using `ffprobe`.
   - **Input**: `stream_url` (audio stream URL).
   - **Output**: Audio sample rate (Hz) for calculating spike timing.

3. **`stream_audio_to_buffer(stream_url, audio_queue, sample_rate)`**
   - Runs an `ffmpeg` process to stream audio from the URL into a buffer (queue).
   - **Input**: `stream_url` (audio stream URL), `audio_queue` (queue to store audio data), `sample_rate` (audio sample rate).
   - **Output**: Streams audio data continuously to `audio_queue`.

4. **`detect_audio_spikes(audio_queue, stream_url, sample_rate, clip_duration=DEFAULT_CLIP_DURATION)`**
   - Detects spikes in audio data using peak detection (`find_peaks`).
   - Checks the time gap between spikes to avoid overlapping video clips.
   - Calls `trim_stream_clip` to create a video clip if a spike is detected and the time gap is sufficient.
   - **Input**: `audio_queue` (queue for audio data), `stream_url` (video stream URL), `sample_rate`, `clip_duration`.
   - **Output**: Spike detection and video clipping based on detected spikes.

5. **`trim_stream_clip(stream_url, start_time, duration=DEFAULT_CLIP_DURATION)`**
   - Creates a video clip from the stream URL starting at `start_time` and lasting `duration` seconds.
   - **Input**: `stream_url` (video stream URL), `start_time` (clip start time in seconds), `duration` (clip duration).
   - **Output**: A `.mp4` video clip saved in the `video_chunks` folder.

### Overall Program Workflow

1. **Initial Setup**:
   - Retrieve audio and video URLs from YouTube using `get_stream_url`.
   - Retrieve audio sample rate from the audio URL using `get_audio_sample_rate`.
   - If either the URL or sample rate is invalid, the program exits.

2. **Audio Streaming**:
   - The `stream_audio_to_buffer` process is initialized to stream audio data from the stream into `audio_queue`.

3. **Spike Detection**:
   - The `detect_audio_spikes` process reads audio data from `audio_queue`, detects spikes, and evaluates the time interval between them.
   - If a spike is detected and it is at least 20 seconds apart from the previous spike, the `trim_stream_clip` function is called to create a video clip.

4. **Video Clipping**:
   - `trim_stream_clip` trims and saves a video based on the detected spike time, with an offset.

5. **Program Termination**:
   - When the process is completed or manually interrupted with `KeyboardInterrupt`, the program terminates all processes.

---

## Notes
1. Ensure a stable internet connection for video streaming.
2. This program is designed to continuously run on live streams until manually stopped.
