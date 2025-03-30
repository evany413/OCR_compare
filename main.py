import os
from pathlib import Path
import argparse
import process
import logging
from typing import Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_video_file(file_path: Path) -> bool:
    """Check if the file is a video file based on extension"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    return file_path.suffix.lower() in video_extensions

def process_video(video_path: Path, frame_gap: float = 5, ocr_engine: str = 'paddle', debug: bool = False) -> None:
    """Process a single video file"""
    try:
        logger.info(f"Processing video: {video_path}")
        
        # Create output directory for this video
        output_dir = video_path.parent / 'ocr_output'
        output_dir.mkdir(exist_ok=True)
        
        # Set debug flag in process module
        process.set_debug(debug)
        
        # Process the video
        frames_dir = output_dir / 'frames'
        result_file = output_dir / 'result.txt'
        
        process.extract_frames(video_path, output_dir, frame_gap)
        
        if ocr_engine == 'paddle':
            ocr = process.PaddleOCR(lang='ch', use_angle_cls=True)
            process.process_frames_paddle(ocr, frames_dir, result_file)
        else:
            process.process_frames_easyocr(frames_dir, result_file)
            
        logger.info(f"Successfully processed: {video_path}")
        
    except Exception as e:
        logger.error(f"Error processing {video_path}: {str(e)}")

def process_directory(root_dir: Union[str, Path], frame_gap: float = 5, ocr_engine: str = 'paddle', debug: bool = False) -> None:
    """Walk through directory and process all video files"""
    root_path = Path(root_dir)
    
    if not root_path.exists():
        logger.error(f"Directory does not exist: {root_dir}")
        return
        
    # Walk through all directories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_dir = Path(dirpath)
        
        # Process each file in the current directory
        for filename in filenames:
            file_path = current_dir / filename
            
            if is_video_file(file_path):
                process_video(file_path, frame_gap, ocr_engine, debug)

def main() -> None:
    parser = argparse.ArgumentParser(description='Process videos in directories and extract text using OCR')
    parser.add_argument('--dir', default='.',
                      help='Root directory to search for videos (default: current directory)')
    parser.add_argument('-fg', '--frame_gap', type=float, default=5,
                      help='Time gap between frames in seconds (default: 5)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode to show detailed messages and keep frames')
    parser.add_argument('--ocr', choices=['paddle', 'easyocr'], default='paddle',
                      help='Choose OCR engine (default: paddle)')
    
    args = parser.parse_args()
    
    logger.info(f"Starting video processing in directory: {args.dir}")
    logger.info(f"Using OCR engine: {args.ocr}")
    logger.info(f"Frame gap: {args.frame_gap} seconds")
    
    process_directory(args.dir, args.frame_gap, args.ocr, args.debug)
    logger.info("Processing complete!")

if __name__ == "__main__":
    main()