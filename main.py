import os
from pathlib import Path
import argparse
import process
import logging
from typing import Optional, Union, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Thread-safe queue for logging
log_queue = Queue()

def is_video_file(file_path: Path) -> bool:
    """Check if the file is a video file based on extension"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    return file_path.suffix.lower() in video_extensions

def process_video(video_path: Path, frame_gap: float = 5, ocr_engine: str = 'paddle', debug: bool = False) -> None:
    """Process a single video file"""
    try:
        log_queue.put(f"Processing video: {video_path}")
        
        # Create output directory for this video
        output_dir = video_path.parent / 'ocr_output'
        output_dir.mkdir(exist_ok=True)
        
        # Set debug flag in process module
        process.set_debug(debug)
        
        # Process the video
        frames_dir = output_dir / f"frames_{video_path.stem}"
        result_file = output_dir / f"result_{video_path.stem}.txt"
        
        process.extract_frames(video_path, output_dir, frame_gap)
        
        if ocr_engine == 'paddle':
            ocr = process.PaddleOCR(lang='ch', use_angle_cls=True)
            process.process_frames_paddle(ocr, frames_dir, result_file)
        else:
            process.process_frames_easyocr(frames_dir, result_file)
            
        log_queue.put(f"Successfully processed: {video_path}")
        
    except Exception as e:
        log_queue.put(f"Error processing {video_path}: {str(e)}")

def process_videos(video_files: List[Path], frame_gap: float, ocr_engine: str, debug: bool, max_workers: int) -> None:
    """Process multiple videos using thread pool"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_video = {
            executor.submit(process_video, video_path, frame_gap, ocr_engine, debug): video_path
            for video_path in video_files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_video):
            video_path = future_to_video[future]
            try:
                future.result()  # This will raise any exceptions that occurred
            except Exception as e:
                log_queue.put(f"Error processing {video_path}: {str(e)}")

def process_directory(root_dir: Union[str, Path], frame_gap: float = 5, ocr_engine: str = 'paddle', 
                     debug: bool = False, max_workers: int = 5) -> None:
    """Walk through directory and process all video files"""
    root_path = Path(root_dir)
    
    if not root_path.exists():
        logger.error(f"Directory does not exist: {root_dir}")
        return
    
    # Collect all video files
    video_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_dir = Path(dirpath)
        for filename in filenames:
            file_path = current_dir / filename
            if is_video_file(file_path):
                video_files.append(file_path)
    
    if not video_files:
        logger.info("No video files found in the specified directory")
        return
    
    # Sort video files for consistent processing order
    video_files.sort()
    
    # Process videos using thread pool
    process_videos(video_files, frame_gap, ocr_engine, debug, max_workers)

def log_worker():
    """Worker function to handle logging from threads"""
    while True:
        message = log_queue.get()
        if message is None:  # Poison pill to stop the worker
            break
        logger.info(message)
        log_queue.task_done()

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
    parser.add_argument('--threads', type=int, default=5,
                      help='Number of concurrent threads (default: 5)')
    
    args = parser.parse_args()
    
    logger.info(f"Starting video processing in directory: {args.dir}")
    logger.info(f"Using OCR engine: {args.ocr}")
    logger.info(f"Frame gap: {args.frame_gap} seconds")
    logger.info(f"Using {args.threads} concurrent threads")
    
    # Start log worker thread
    log_thread = threading.Thread(target=log_worker)
    log_thread.start()
    
    try:
        process_directory(args.dir, args.frame_gap, args.ocr, args.debug, args.threads)
    finally:
        # Stop log worker
        log_queue.put(None)
        log_thread.join()
    
    logger.info("Processing complete!")

if __name__ == "__main__":
    main()