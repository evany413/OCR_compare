# PPOCRExtractor

A Python tool for extracting text from videos using OCR (Optical Character Recognition). This tool supports both PaddleOCR and EasyOCR engines, and can process multiple videos in directories.

## Features

- Extract frames from videos at specified intervals
- Support for multiple OCR engines (PaddleOCR and EasyOCR)
- Process multiple videos in directories and subdirectories
- Automatic output organization (creates output directory next to each video)
- Support for multiple video formats (mp4, avi, mov, mkv, wmv, flv, webm)
- Configurable frame extraction interval
- Debug mode for detailed processing information

## Requirements

- Python 3.6+
- ffmpeg
- PaddleOCR or EasyOCR (depending on your choice)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PPOCRExtractor.git
cd PPOCRExtractor
```

2. Install required packages:
```bash
pip install paddleocr easyocr ffmpeg-python
```

3. Install ffmpeg (if not already installed):
- On macOS: `brew install ffmpeg`
- On Ubuntu: `sudo apt-get install ffmpeg`
- On Windows: Download from [ffmpeg website](https://ffmpeg.org/download.html)

## Usage

### Basic Usage

Process all videos in the current directory:
```bash
python main.py
```

### Command Line Options

```bash
python main.py [options]

Options:
  --dir DIR          Root directory to search for videos (default: current directory)
  -fg, --frame_gap   Time gap between frames in seconds (default: 5)
  --debug           Enable debug mode to show detailed messages and keep frames
  --ocr {paddle,easyocr}  Choose OCR engine (default: paddle)
```

### Examples

1. Process videos in a specific directory:
```bash
python main.py --dir /path/to/videos
```

2. Use EasyOCR instead of PaddleOCR:
```bash
python main.py --ocr easyocr
```

3. Extract frames every 3 seconds:
```bash
python main.py -fg 3
```

4. Enable debug mode:
```bash
python main.py --debug
```

## Output

For each processed video, the tool creates an `ocr_output` directory next to the video file containing:
- `result.txt`: Extracted text from the video
- `frames/`: Directory containing extracted frames (only kept in debug mode)

## Notes

- The tool processes videos in alphabetical order
- Text is only saved if the OCR confidence is above 80%
- In debug mode, the frames directory is preserved for inspection
- The tool supports both English and Simplified Chinese text recognition

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.