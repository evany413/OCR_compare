import easyocr
import argparse
import ffmpeg
from pathlib import Path
from paddleocr import PaddleOCR

def extract_frames(video_path):
    # Create frames directory if it doesn't exist
    frames_dir = Path('frames')
    frames_dir.mkdir(exist_ok=True)
    
    try:
        # Get video information
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        
        print(f"Video duration: {duration:.2f} seconds")
        print(f"Extracting frames from video: {video_path}")
        
        # Extract frames every 5 seconds
        stream = (
            ffmpeg
            .input(video_path)
            .filter('fps', fps=1/5)  # 1 frame per 5 seconds
            .output(
                str(frames_dir / '%d.jpg'),
                q=2,  # High quality (2 is high quality, lower number = higher quality)
                frame_pts=1  # Add frame number to filename
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        print("Frame extraction complete!")
        
    except ffmpeg.Error as e:
        print(f"Error during frame extraction: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

def save_results_to_file(text):
    """Save OCR results to a text file"""
    with open('ocr_results.txt', 'a', encoding='utf-8') as f:
        f.write(f"{text}\n")

def process_frames():
    # Initialize EasyOCR reader for English only
    reader = easyocr.Reader(['en', 'ch_sim'])
    
    # Get the frames directory path
    frames_dir = Path('frames')
    
    # Clear the results file at the start
    with open('ocr_results.txt', 'w', encoding='utf-8') as f:
        f.write("")  # Just clear the file without any header
    
    # Process each frame in order
    for i in range(11):  # We have frames 0-10
        frame_path = frames_dir / f'{i}.jpg'
        if not frame_path.exists():
            print(f"Frame {i} not found")
            continue
            
        print(f"\nProcessing frame {i}:")
        print("-" * 50)
        
        # Read text from the image
        result = reader.readtext(str(frame_path))
        
        # Display the extracted text and save high confidence results
        for detection in result:
            text = detection[1]  # The actual text content
            confidence = detection[2]  # Confidence score
            print(f"Text: {text}")
            print(f"Confidence: {confidence:.2f}")
            print("-" * 30)
            
            # Save results with confidence > 80%
            if confidence > 0.8:
                save_results_to_file(text)

def process_frames_paddle(ocr):
    """Process frames using PaddleOCR"""
    # Get the frames directory path
    frames_dir = Path('frames')
    
    # Clear the results file at the start
    with open('ocr_results.txt', 'w', encoding='utf-8') as f:
        f.write("")  # Just clear the file without any header

    # Process each frame in order
    for i in range(11):  # We have frames 0-10
        frame_path = frames_dir / f'{i}.jpg'
        if not frame_path.exists():
            print(f"Frame {i} not found")
            continue
            
        print(f"\nProcessing frame {i}:")
        print("-" * 50)
        
        # Read text from the image
        result = ocr.ocr(str(frame_path))
        
        # Display and save the extracted text
        if result is not None:  # Check if result exists
            for line in result:
                if line is not None and len(line) >= 2:  # Ensure line has enough elements
                    text = line[1][0]  # The actual text content
                    confidence = line[1][1]  # Confidence score
                    print(f"Text: {text}")
                    print(f"Confidence: {confidence:.2f}")
                    print("-" * 30)
                    
                    # Save results with confidence > 80%
                    if confidence > 0.8:
                        save_results_to_file(text)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract frames from video and perform OCR')
    parser.add_argument('--video', help='Path to the video file (optional)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Extract frames if video path is provided
    if args.video:
        # Initialize PaddleOCR
        ocr = PaddleOCR(lang='en')
        extract_frames(args.video)
        # process_frames()
        process_frames_paddle(ocr)
    
        