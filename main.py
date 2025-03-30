import easyocr
import argparse
import ffmpeg
from pathlib import Path
from paddleocr import PaddleOCR
import shutil
import sys
import logging

# Global debug variable
debug = False

# Configure logging to suppress all PaddleOCR messages
logging.getLogger("paddleocr").setLevel(logging.ERROR)
logging.getLogger("paddle").setLevel(logging.ERROR)
logging.getLogger("ppocr").setLevel(logging.ERROR)
# Disable all logging from paddle and ppocr
logging.getLogger("paddle").disabled = True
logging.getLogger("ppocr").disabled = True

def extract_frames(video_path, frame_gap=5):
    """Extract frames from video file"""
    if not Path(video_path).exists():
        print(f"Error: Video file '{video_path}' does not exist")
        sys.exit(1)
        
    # Create frames directory if it doesn't exist
    frames_dir = Path('frames')
    frames_dir.mkdir(exist_ok=True)
    
    try:
        # Get video information
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        
        # Calculate total number of frames
        total_frames = int(duration / frame_gap)
        
        # Calculate number of digits needed for leading zeros
        num_digits = len(str(total_frames))
        
        if debug:
            print(f"Video duration: {duration:.2f} seconds")
            print(f"Total frames to extract: {total_frames}")
            print(f"Using {num_digits} digits for frame numbering")
            print(f"Extracting frames from video: {video_path}")
        
        # Extract frames using ffmpeg-python API
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.filter(stream, 'fps', fps=f'1/{frame_gap}')
        stream = ffmpeg.filter(stream, 'scale', w='iw*sar', h='ih')
        stream = ffmpeg.output(stream, str(frames_dir / f'%{num_digits}d.jpg'))
        
        if debug:
            print(f"Running ffmpeg command: {ffmpeg.compile(stream)}")
            
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
        if debug:
            print("Frame extraction complete!")
        
    except ffmpeg.Error as e:
        print(f"Error during frame extraction: {e.stderr.decode() if e.stderr else str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during frame extraction: {str(e)}")
        sys.exit(1)

def save_results_to_file(text):
    """Save OCR results to a text file"""
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(f"{text}\n")

def get_frame_files(frames_dir):
    """Get the list of frame files in the frames directory"""
    frames_dir = Path(frames_dir)
    if not frames_dir.exists():
        print("Error: Frames directory does not exist")
        sys.exit(1)
    
    # Get all jpg files and sort them numerically
    frame_files = sorted(
        [f for f in frames_dir.glob('*.jpg')],
        key=lambda x: int(x.stem)  # Sort by the numeric part of the filename
    )
    
    if not frame_files:
        print("Error: No frame files found in the frames directory")
        sys.exit(1)
        
    return frame_files

def process_frames_paddle(ocr):
    """Process frames using PaddleOCR"""
    try:
        # Get the frames directory path
        frames_dir = Path('frames')
        
        # Clear the results file at the start
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write("")  # Just clear the file without any header

        # Get the list of frame files
        frame_files = get_frame_files(frames_dir)
        
        # Set to store unique words
        unique_words = set()
        
        # Process each frame
        for frame_path in frame_files:
            if debug:
                print(f"\nProcessing frame {frame_path.stem}:")
                print("-" * 50)
            
            # Read text from the image
            result = ocr.ocr(str(frame_path))
            
            # Display and save the extracted text
            if result is not None:  # Check if result exists
                for line in result[0]:  # PaddleOCR returns a list of lists, first element contains the detections
                    if line is not None and len(line) >= 2:  # Ensure line has enough elements
                        text = line[1][0]  # The actual text content
                        confidence = line[1][1]  # Confidence score
                        
                        if debug:
                            print(f"Text: {text}")
                            print(f"Confidence: {confidence:.2f}")
                            print("-" * 30)
                        
                        # Save results with confidence > 80%
                        if confidence > 0.8:
                            unique_words.add(text)
        
        # Write unique words to file
        with open('result.txt', 'w', encoding='utf-8') as f:
            for word in sorted(unique_words):
                f.write(f"{word}\n")
        
        if not debug:
            # Clean up frames directory
            shutil.rmtree(frames_dir)
            
    except Exception as e:
        print(f"Error during PaddleOCR processing: {str(e)}")
        if not debug:
            shutil.rmtree(frames_dir)
        sys.exit(1)

def process_frames_easyocr():
    """Process frames using EasyOCR"""
    try:
        # Initialize EasyOCR reader for English and Chinese
        reader = easyocr.Reader(['en', 'ch_sim'])
        
        # Get the frames directory path
        frames_dir = Path('frames')
        
        # Clear the results file at the start
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write("")  # Just clear the file without any header
        
        # Get the list of frame files
        frame_files = get_frame_files(frames_dir)
        
        # Set to store unique words
        unique_words = set()
        
        # Process each frame
        for frame_path in frame_files:
            if debug:
                print(f"\nProcessing frame {frame_path.stem}:")
                print("-" * 50)
            
            # Read text from the image
            result = reader.readtext(str(frame_path))
            
            # Display and save the extracted text
            for detection in result:
                text = detection[1]  # The actual text content
                confidence = detection[2]  # Confidence score
                
                if debug:
                    print(f"Text: {text}")
                    print(f"Confidence: {confidence:.2f}")
                    print("-" * 30)
                
                # Save results with confidence > 80%
                if confidence > 0.8:
                    unique_words.add(text)
        
        # Write unique words to file
        with open('result.txt', 'w', encoding='utf-8') as f:
            for word in sorted(unique_words):
                f.write(f"{word}\n")
        
        if not debug:
            # Clean up frames directory
            shutil.rmtree(frames_dir)
            
    except Exception as e:
        print(f"Error during EasyOCR processing: {str(e)}")
        if not debug:
            shutil.rmtree(frames_dir)
        sys.exit(1)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract frames from video and perform OCR')
    parser.add_argument('--video', help='Path to the video file (optional)')
    parser.add_argument('-fg', '--frame_gap', type=float, default=5,
                      help='Time gap between frames in seconds (default: 5)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode to show detailed messages and keep frames')
    parser.add_argument('--ocr', choices=['paddle', 'easyocr'], default='paddle',
                      help='Choose OCR engine (default: paddle)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set global debug variable
    debug = args.debug
    
    # Extract frames if video path is provided
    if args.video:
        try:
            # Extract frames first
            extract_frames(args.video, args.frame_gap)
            
            # Process frames with selected OCR engine
            if args.ocr == 'paddle':
                ocr = PaddleOCR(lang='ch', use_angle_cls=True)  # Enable angle classifier
                process_frames_paddle(ocr)
            else:
                process_frames_easyocr()
                
            if not debug:
                print("Processing complete! Results saved to result.txt")
                
        except KeyboardInterrupt:
            print("\nProcess interrupted by user")
            if not debug:
                shutil.rmtree('frames', ignore_errors=True)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            if not debug:
                shutil.rmtree('frames', ignore_errors=True)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
        
        