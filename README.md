# ControlVolumeByHand

Control your computer's system volume and music playback using hand gestures and a webcam.

This project uses computer vision and hand tracking to provide a touch-free way to interact with your computer.

## Features

- **Volume Control:** Adjust system volume using hand gestures.
- **Music Navigation:** Switch between songs using horizontal hand movements.
- **Playback Control:** Play or pause music using vertical hand movements.
- **Real-Time Hand Tracking:** Detect and track hand landmarks.
- **Webcam Preview:** Display the live camera feed.
- **FPS Display:** Monitor application performance.

## Technologies

- Python
- OpenCV
- MediaPipe
- NumPy
- python-vlc
- VLC Media Player

## Requirements

- Ubuntu or another compatible Linux distribution
- A compatible Python version
- A working webcam
- VLC Media Player
- `pactl` or `amixer` for system volume control

## Installation

### 1. Install system dependencies

On Ubuntu, run:

    sudo apt update
    sudo apt install python3-venv python3-pip vlc

### 2. Clone the repository

    git clone https://github.com/amirhossein-isarinia/ControlVolumeByHand.git
    cd ControlVolumeByHand

### 3. Create a virtual environment

    python3 -m venv .venv
    source .venv/bin/activate

### 4. Install Python dependencies

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

Make sure your Python version is supported by the installed MediaPipe release.

## Add Your Music

Place your own audio files in the `music/` directory.

Example:

    music/
    ├── song-one.mp3
    └── song-two.mp3

Music files are excluded from this repository. Add your own audio files locally before running the application.

## Usage

Start the application:

    python VolumeHandControl.py

Press `q` in the webcam window to quit.

## Project Structure

    ControlVolumeByHand/
    ├── VolumeHandControl.py
    ├── HandTrackingModule.py
    ├── requirements.txt
    ├── README.md
    └── music/

- `VolumeHandControl.py` — Main application and gesture controls.
- `HandTrackingModule.py` — Hand detection and tracking utilities.
- `requirements.txt` — Python dependencies.
- `music/` — Directory for local audio files.

## Troubleshooting

- **Webcam issues:** Check that your webcam is connected and accessible.
- **Audio issues:** Verify that VLC and its system libraries are installed.
- **Volume issues:** Check that `pactl` or `amixer` is available.
- **Installation issues:** Make sure your Python version supports the required packages.

## Author

**Amirhossein Sarinia**

GitHub: https://github.com/amirhossein-isarinia

## License

No license has been specified for this project yet.
