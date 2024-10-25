# Video Replay Project

The Video Replay Project is an AI-driven video processing system designed to detect and extract specific soccer events within match footage, such as goals, corners, and fouls. This project aims to develop a backend AI service that can analyze soccer videos in near real-time, automatically identifying and creating replay clips for key events.

## Dataset
The dataset used for training and testing the model can be accessed here:
[Dataset Link](https://drive.google.com/drive/folders/17SPHH6pIHW1s8s2cW4501KOwmX6sImzL?usp=sharing)

## Project Goals
This project focuses on developing an AI service for event-based video analysis and clip generation. The main goals include:

- **Event Detection**: Detect specific soccer events such as:
  - Goal
  - Corner
  - Shoot on Goal
  - Saves
  - Foul
  - Freekick
  - VAR

  **Output**: The AI recognizes and categorizes events within the video input.

- **Event Extraction**: Segment and extract 20-second replay clips based on detected events, in near-real-time, for each event occurrence.
  
  **Output**: For each detected event, the AI will generate a video clip based on the event's specific time frame.

## How It Works
This project includes a custom-trained YOLOv8 model capable of processing video frames to detect and classify events. When an event is detected, the system will extract the relevant 20-second video segment for easy review and replay.
