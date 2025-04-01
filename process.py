import easyocr
import ffmpeg
from pathlib import Path
from paddleocr import PaddleOCR
import shutil
import sys
from typing import List, Set, Optional, Union

# Global debug variable
debug: bool = False

def set_debug(value: bool) -> None:
    """Set the global debug variable"""
    global debug
    debug = value

def extract_frames(video_path: Union[str, Path], frame_gap: float = 5) -> Path:
    """Extract frames from video file"""
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    # Create frames directory with video name to avoid conflicts
    frames_dir = video_path.parent / f"frames_{video_path.stem}"
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
        
        # Extract frames using ffmpeg-python API
        stream = ffmpeg.input(str(video_path))
        stream = ffmpeg.filter(stream, 'fps', fps=f'1/{frame_gap}')
        stream = ffmpeg.filter(stream, 'scale', w='iw*sar', h='ih')
        stream = ffmpeg.output(stream, str(frames_dir / f'%{num_digits}d.jpg'))
        
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        return frames_dir
        
    except Exception as e:
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
        raise RuntimeError(f"Failed to extract frames from {video_path}: {str(e)}")

def get_frame_files(frames_dir: Union[str, Path]) -> List[Path]:
    """Get the list of frame files in the frames directory"""
    frames_dir = Path(frames_dir)
    if not frames_dir.exists():
        sys.exit(1)
    
    frame_files = sorted(
        [f for f in frames_dir.glob('*.jpg')],
        key=lambda x: int(x.stem)
    )
    
    if not frame_files:
        sys.exit(1)
        
    return frame_files

def process_frames_paddle(ocr: PaddleOCR, image_path: Union[str, Path], output_file: Union[str, Path]) -> None:
    """Process frames using PaddleOCR"""
    try:
        unique_words: Set[str] = set()
        result = ocr.ocr(str(image_path))
        if result is not None and len(result) > 0 and result[0] is not None:
            for line in result[0]:
                if line is not None and len(line) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    
                    if confidence > 0.9:
                        unique_words.add(text)
        
        with open(output_file, 'a', encoding='utf-8') as f:
            for word in sorted(unique_words):
                f.write(f"{word}\n")
        
    except Exception as e:
        raise RuntimeError(f"Failed to process frame {image_path} with PaddleOCR: {str(e)}")

def process_frames_easyocr(image_path: Union[str, Path], output_file: Union[str, Path]) -> None:
    """Process frames using EasyOCR"""
    try:
        reader = easyocr.Reader(['en', 'ch_sim'])
        unique_words: Set[str] = set()
        
        result = reader.readtext(str(image_path))
        for detection in result:
            text = detection[1]
            confidence = detection[2]
            
            if confidence > 0.8:
                unique_words.add(text)
        
        with open(output_file, 'a', encoding='utf-8') as f:
            for word in sorted(unique_words):
                f.write(f"{word}\n")
            
    except Exception as e:
        raise RuntimeError(f"Failed to process frame {image_path} with EasyOCR: {str(e)}")
        
        