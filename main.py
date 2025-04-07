from pathlib import Path
import argparse
import process
from typing import List, Set
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
    """Read file and extract words, returning them as a set of original words"""
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(re.findall(r'\w+', f.read()))

def organize_folders(folder_path: Path, output_dir: Path, ocr_output_file: Path, config: ProcessingConfig) -> None:
    """Organize folders based on OCR results and word list priority"""
        
    if not ocr_output_file.exists():
        raise FileNotFoundError(f"Output file does not exist: {ocr_output_file}")
    
    extracted_words = extract_words_from_file(ocr_output_file)
    print(f"Extracted words: {extracted_words}")
    
    lower_extracted_words = {word.lower() for word in extracted_words}
    
    # Find first matching word (case-insensitive)
    matching_word = next(
        (word for word in config.word_list if word.lower() in lower_extracted_words),
        None
    )

    # if not config.debug:
    #     ocr_output_file.unlink()
    
    if matching_word:
        target_dir = output_dir / matching_word
        target_dir.mkdir(exist_ok=True)
        shutil.move(str(folder_path), str(target_dir / folder_path.name))
    else:
        shutil.move(str(folder_path), str(output_dir / folder_path.name))
    

def process_videos(root_dir: Path, video_files: List[Path], config: ProcessingConfig) -> List[Path]:

    if not root_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {root_dir}")

    frames_folder_list = []
    for video_path in video_files:
        try:
            frames_folder = process.extract_frames(video_path, config.frame_gap)
            frames_folder_list.append(frames_folder)
        except Exception as e:
            print(f"Error processing {video_path}: {str(e)}")

    return frames_folder_list

def process_images(root_dir: Path, image_files: List[Path], config: ProcessingConfig) -> Path:

    if not root_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {root_dir}")
    
    output_file = root_dir / 'ocr_output.txt'
    if not output_file.exists():
        output_file.touch()
    
    if config.ocr_engine == OCREngine.PADDLE:
        for image_path in image_files:
            try:
                process.process_frames_paddle(image_path, output_file)
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
    elif config.ocr_engine == OCREngine.EASYOCR:
        for image_path in image_files:
            try:
                process.process_frames_easyocr(image_path, output_file)
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
    return output_file

def clean_up_ocr_output(frames_folders_list: List[Path], config: ProcessingConfig) -> None:
    if config.debug:
        return
    for frames_folder in frames_folders_list:
        shutil.rmtree(frames_folder)

def main():
    parser = argparse.ArgumentParser(description='Process videos and extract frames with OCR')
    parser.add_argument('-i', '--input-dir', type=str, default=INPUT_DIR, help='Input directory containing videos')
    parser.add_argument('-o', '--output-dir', type=str, default=OUTPUT_DIR, help='Output directory for processed files')
    parser.add_argument('-fp', '--frame-gap', type=float, default=5, help='Time gap between frames in seconds')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--ocr-engine', type=str, choices=['paddle', 'easyocr'], default='paddle', help='OCR engine to use')
    parser.add_argument('--word-list', type=str, nargs='+', help='Words to search for (space-separated)')
    
    args = parser.parse_args()
    
    # Convert paths to Path objects
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create processing config
    config = ProcessingConfig(
        frame_gap=args.frame_gap,
        debug=args.debug,
        ocr_engine=OCREngine(args.ocr_engine),
        word_list=args.word_list
    )
    
    # process folders in input_dir
    for folder in input_dir.iterdir():
        if folder.is_dir():
            print(f"Processing folder: {folder}")
            # Get all video files
            video_files = [f for f in folder.rglob('*.mp4')]
            print(f"Found {len(video_files)} video files")
            frames_folders_list = process_videos(folder, video_files, config)

            image_files = [f for f in folder.rglob('*.jpg')]
            output_file = process_images(folder, image_files, config)
            
            clean_up_ocr_output(frames_folders_list, config)
            organize_folders(folder, output_dir, output_file, config)
    
    print("Processing completed!")

if __name__ == '__main__':
    main()