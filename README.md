# PPOCRExtractor

A Python tool for extracting text from videos using OCR (Optical Character Recognition). This tool supports both PaddleOCR and EasyOCR engines, and can process multiple videos in directories.

## Features

- Extract frames from videos at specified intervals
- Support for multiple OCR engines (PaddleOCR and EasyOCR)
- Process multiple videos in directories and subdirectories
- Automatic output organization based on detected text
- Support for multiple video formats (mp4, avi, mov, mkv, wmv, flv, webm)
- Configurable frame extraction interval
- Debug mode for detailed processing information
- Word-based folder organization

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
pip install -r requirements.txt
```

3. Install ffmpeg (if not already installed):
- On macOS: `brew install ffmpeg`
- On Ubuntu: `sudo apt-get install ffmpeg`
- On Windows: Download from [ffmpeg website](https://ffmpeg.org/download.html)

4. Install OpenCC (if not already installed):
- On macOS: `brew install opencc`
- On Ubuntu: `sudo apt-get install opencc`
- On Windows: Download from [OpenCC releases](https://github.com/BYVoid/OpenCC/releases)

## Directory Structure

The tool uses the following directory structure:
- `_original/`: Place your input videos here (default input directory)
- `_converted/`: Processed videos will be organized here (default output directory)

## Usage

### Basic Usage

Process all videos in the default input directory:
```bash
python main.py
```

### Command Line Options

```bash
python main.py [options]

Options:
  --input-dir DIR    Input directory containing videos (default: _original)
  --output-dir DIR   Output directory for processed files (default: _converted)
  --frame-gap N      Time gap between frames in seconds (default: 5)
  --debug           Enable debug mode to show detailed messages and keep frames
  --ocr-engine {paddle,easyocr}  Choose OCR engine (default: paddle)
  --word-list FILE  Path to file containing words to search for (default: Facebook, Twitter, IG)
```

### Examples

1. Process videos in a specific input directory:
```bash
python main.py --input-dir /path/to/videos
```

2. Specify custom output directory:
```bash
python main.py --output-dir /path/to/output
```

3. Use EasyOCR instead of PaddleOCR:
```bash
python main.py --ocr-engine easyocr
```

4. Extract frames every 3 seconds:
```bash
python main.py --frame-gap 3
```

5. Enable debug mode:
```bash
python main.py --debug
```

6. Use custom word list:
```bash
python main.py --word-list words.txt
```

## Output Organization

The tool organizes processed videos based on detected text:
1. Videos are processed in their input folders
2. OCR is performed on extracted frames
3. Videos are moved to subdirectories in the output directory based on detected words
4. If no matching words are found, videos are moved to the root of the output directory
5. In debug mode, OCR output files are preserved for inspection

## Notes

- The tool processes videos in alphabetical order
- Text is only saved if the OCR confidence is above 80%
- In debug mode, the frames directory and OCR output files are preserved for inspection
- The tool supports both English and Simplified Chinese text recognition
- By default, the tool looks for social media platform names (Facebook, Twitter, IG)
- You can provide a custom word list file to search for specific terms
- Each video folder is processed independently

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.