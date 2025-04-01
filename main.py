import os
from pathlib import Path
import argparse
import process
from typing import Optional, Union, List, Set, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import re
from dataclasses import dataclass
from enum import Enum

class OCREngine(Enum):
    PADDLE = 'paddle'
    EASYOCR = 'easyocr'

@dataclass
class ProcessingConfig:
    frame_gap: float = 5
    debug: bool = False
    ocr_engine: OCREngine = OCREngine.PADDLE
    max_workers: int = 5
    word_list: List[str] = None

    def __post_init__(self):
        if self.word_list is None:
            self.word_list = ['Facebook', 'Twitter', 'IG']

# Default directories
INPUT_DIR = '_original'
OUTPUT_DIR = '_converted'

def extract_words_from_file(file_path: Path) -> Set[str]:
    """Read file and extract words, returning them as a set"""
    if not file_path.exists():
        return set()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        return set(re.findall(r'\w+', text.lower()))

def is_video_file(file_path: Path) -> bool:
    """Check if the file is a video file based on extension"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    return file_path.suffix.lower() in video_extensions

def organize_folders(folder_path: Path, output_dir: Path, word_list: List[str], debug: bool = False) -> None:
    """Organize folders based on OCR results and word list priority"""
    if not folder_path.is_dir() or not folder_path.exists():
        print(f"Folder path is not a directory or doesn't exist: {folder_path}")
        return
        
    txt_file = folder_path / 'ocr_output.txt'
    if not txt_file.exists():
        print(f"No text files found in OCR output directories under {folder_path}")
        return
    
    extracted_words = extract_words_from_file(txt_file)
    print(f"Extracted words: {extracted_words}")
    
    matching_word = next(
        (word for word in word_list if word.lower() in extracted_words),
        None
    )
    
    if matching_word:
        target_dir = output_dir / matching_word
        target_dir.mkdir(exist_ok=True)
        path_return = shutil.move(str(folder_path), str(target_dir / folder_path.name))
        txt_file = Path(path_return) / 'ocr_output.txt'
    else:
        path_return = shutil.move(str(folder_path), str(output_dir / folder_path.name))
        txt_file = Path(path_return) / 'ocr_output.txt'
    
    if not debug:
        txt_file.unlink()

def process_videos(root_dir: Union[str, Path], config: ProcessingConfig) -> List[Path]:
    """Process all video files in directory sequentially"""
    root_path = Path(root_dir)
    if not root_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {root_dir}")

    video_files = list(root_path.rglob('*.mp4'))
    if not video_files:
        print("No video files found in the specified directory")
        return []
    
    frames_folders_list = []
    for video_path in video_files:
        try:
            frames_folder = process.extract_frames(video_path, config.frame_gap)
            frames_folders_list.append(frames_folder)
        except Exception as e:
            print(f"Error processing {video_path}: {str(e)}")

    return frames_folders_list

def process_images(root_dir: Union[str, Path], config: ProcessingConfig) -> None:
    """Process all image files in directory sequentially"""
    root_path = Path(root_dir)
    if not root_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {root_dir}")
        
    image_files = list(root_dir.rglob('*.jpg'))
    if not image_files:
        print("No image files found in the specified directory")
        return
    
    output_file = root_dir / 'ocr_output.txt'
    
    if config.ocr_engine == OCREngine.PADDLE:
        ocr = process.PaddleOCR(lang='ch', use_angle_cls=True)
        for image_path in image_files:
            try:
                process.process_frames_paddle(ocr, image_path, output_file)
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
    else:
        for image_path in image_files:
            try:
                process.process_frames_easyocr(image_path, output_file)
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")

def clean_up_ocr_output(frames_folders_list: List[Path]) -> None:
    """Clean up temporary OCR output folders"""
    for frames_folder in frames_folders_list:
        shutil.rmtree(frames_folder)

def main():
    parser = argparse.ArgumentParser(description='Process videos and extract frames with OCR')
    parser.add_argument('--input-dir', type=str, default=INPUT_DIR, help='Input directory containing videos')
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR, help='Output directory for processed files')
    parser.add_argument('--frame-gap', type=float, default=5, help='Time gap between frames in seconds')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--ocr-engine', type=str, choices=['paddle', 'easyocr'], default='paddle', help='OCR engine to use')
    parser.add_argument('--word-list', type=str, help='Path to file containing words to search for')
    
    args = parser.parse_args()
    
    # Convert paths to Path objects
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get word list from file if provided
    word_list = None
    if args.word_list:
        word_list = list(extract_words_from_file(Path(args.word_list)))
    
    # Create processing config
    config = ProcessingConfig(
        frame_gap=args.frame_gap,
        debug=args.debug,
        ocr_engine=OCREngine(args.ocr_engine),
        word_list=word_list
    )
    
    # process folders in input_dir
    for folder in input_dir.iterdir():
        if folder.is_dir():
            print(f"Processing folder: {folder}")
            # Get all video files
            video_files = [f for f in folder.glob('**/*') if is_video_file(f)]
        
            if not video_files:
                print(f"No video files found in {folder}")
                continue
            
            print(f"Found {len(video_files)} video files")
            
            # Process videos sequentially
            frames_folders_list = process_videos(folder, config)
            
            # Process images sequentially
            process_images(folder, config)

            # Clean up temporary files
            if not config.debug:
                clean_up_ocr_output(frames_folders_list)
            
            # Organize folders based on OCR results
            organize_folders(folder, output_dir, config.word_list, config.debug)
    
    print("Processing completed!")

if __name__ == '__main__':
    main()