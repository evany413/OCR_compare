# PPOCRExtractor

A Python tool for extracting text from video frames using OCR (Optical Character Recognition). Supports both PaddleOCR and EasyOCR engines.

## Features

- Extract frames from video files at configurable intervals
- Support for both PaddleOCR and EasyOCR engines
- Automatic text deduplication
- Debug mode for detailed processing information
- Automatic cleanup of temporary files
- Support for both English and Chinese text

## Requirements

- Python 3.7+
- FFmpeg
- PaddleOCR
- EasyOCR
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PPOCRExtractor.git
cd PPOCRExtractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg (if not already installed):
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

## Usage

Basic usage:
```bash
python main.py --video path/to/your/video.mp4
```

Advanced options:
```bash
python main.py --video path/to/your/video.mp4 \
    --frame_gap 2 \  # Extract frames every 2 seconds
    --debug \        # Enable debug mode
    --ocr easyocr    # Use EasyOCR instead of PaddleOCR
```

### Command Line Arguments

- `--video`: Path to the video file (required)
- `-fg, --frame_gap`: Time gap between frames in seconds (default: 5)
- `--debug`: Enable debug mode to show detailed messages and keep frames
- `--ocr`: Choose OCR engine (default: paddle)
  - `paddle`: PaddleOCR (optimized for Chinese text)
  - `easyocr`: EasyOCR (general-purpose)

## Output

The tool generates a `result.txt` file containing:
- Unique text extracted from the video frames
- Only text with confidence > 80% is included
- Text is sorted alphabetically
- Duplicates are automatically removed

## Debug Mode

When debug mode is enabled (`--debug`):
- Detailed processing information is displayed
- Frame extraction details are shown
- OCR confidence scores are displayed
- Temporary frame files are preserved
- All internal messages are shown

## Error Handling

The tool includes comprehensive error handling for:
- Missing video files
- Invalid frame extraction
- OCR processing errors
- File system errors
- User interruptions (Ctrl+C)

## Notes

- PaddleOCR is optimized for Chinese text but also handles English
- EasyOCR is more general-purpose but might be slower
- Frame extraction time depends on video length and frame gap
- Processing time depends on the number of frames and chosen OCR engine

## License

[Your chosen license]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.