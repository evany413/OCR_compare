import easyocr
import ffmpeg
from pathlib import Path
from paddleocr import PaddleOCR
import shutil
import sys
import logging
from typing import List, Set, Optional, Union

# Global debug variable
debug: bool = False

# Configure logging to suppress all PaddleOCR messages
logging.getLogger("paddleocr").setLevel(logging.ERROR)
logging.getLogger("paddle").setLevel(logging.ERROR)
logging.getLogger("ppocr").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

def set_debug(value: bool) -> None:
    """Set the global debug variable"""
    global debug
    debug = value

def extract_frames(video_path: Union[str, Path], output_dir: Union[str, Path], frame_gap: float = 5) -> None:
    """Extract frames from video file"""
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    
    if not video_path.exists():
        logger.error(f"Video file '{video_path}' does not exist")
        sys.exit(1)
        
    # Create frames directory if it doesn't exist
    frames_dir = output_dir / 'frames'
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(exist_ok=True)
    
    try:
        # Get video information
        probe = ffmpeg.probe(str(video_path))
        duration = float(probe['format']['duration'])
        
        # Calculate total number of frames
        total_frames = int(duration / frame_gap)
        num_digits = len(str(total_frames))
        
        if debug:
            logger.info(f"Video duration: {duration:.2f} seconds")
            logger.info(f"Total frames to extract: {total_frames}")
        
        # Extract frames using ffmpeg-python API
        stream = ffmpeg.input(str(video_path))
        stream = ffmpeg.filter(stream, 'fps', fps=f'1/{frame_gap}')
        stream = ffmpeg.filter(stream, 'scale', w='iw*sar', h='ih')
        stream = ffmpeg.output(stream, str(frames_dir / f'%{num_digits}d.jpg'))
        
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        
    except Exception as e:
        logger.error(f"Error during frame extraction: {str(e)}")
        sys.exit(1)

def get_frame_files(frames_dir: Union[str, Path]) -> List[Path]:
    """Get the list of frame files in the frames directory"""
    frames_dir = Path(frames_dir)
    if not frames_dir.exists():
        logger.error("Frames directory does not exist")
        sys.exit(1)
    
    frame_files = sorted(
        [f for f in frames_dir.glob('*.jpg')],
        key=lambda x: int(x.stem)
    )
    
    if not frame_files:
        logger.error("No frame files found in the frames directory")
        sys.exit(1)
        
    return frame_files

def process_frames_paddle(ocr: PaddleOCR, frames_dir: Union[str, Path], output_file: Union[str, Path]) -> None:
    """Process frames using PaddleOCR"""
    try:
        frames_dir = Path(frames_dir)
        frame_files = get_frame_files(frames_dir)
        unique_words: Set[str] = set()
        
        for frame_path in frame_files:
            if debug:
                logger.info(f"Processing frame {frame_path.stem}")
            
            result = ocr.ocr(str(frame_path))
            if result is not None:
                for line in result[0]:
                    if line is not None and len(line) >= 2:
                        text = line[1][0]
                        confidence = line[1][1]
                        
                        if debug:
                            logger.info(f"Text: {text} (Confidence: {confidence:.2f})")
                        
                        if confidence > 0.8:
                            unique_words.add(text)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(unique_words):
                f.write(f"{word}\n")
        
        if not debug:
            shutil.rmtree(frames_dir)
            
    except Exception as e:
        logger.error(f"Error during PaddleOCR processing: {str(e)}")
        if not debug:
            shutil.rmtree(frames_dir)
        sys.exit(1)

def process_frames_easyocr(frames_dir: Union[str, Path], output_file: Union[str, Path]) -> None:
    """Process frames using EasyOCR"""
    try:
        reader = easyocr.Reader(['en', 'ch_sim'])
        frames_dir = Path(frames_dir)
        frame_files = get_frame_files(frames_dir)
        unique_words: Set[str] = set()
        
        for frame_path in frame_files:
            if debug:
                logger.info(f"Processing frame {frame_path.stem}")
            
            result = reader.readtext(str(frame_path))
            for detection in result:
                text = detection[1]
                confidence = detection[2]
                
                if debug:
                    logger.info(f"Text: {text} (Confidence: {confidence:.2f})")
                
                if confidence > 0.8:
                    unique_words.add(text)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(unique_words):
                f.write(f"{word}\n")
        
        if not debug:
            shutil.rmtree(frames_dir)
            
    except Exception as e:
        logger.error(f"Error during EasyOCR processing: {str(e)}")
        if not debug:
            shutil.rmtree(frames_dir)
        sys.exit(1)
        
        