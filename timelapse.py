import os
from tqdm import tqdm
import cv2
import sys
import datetime
import click

def get_images(folder):
    image_files = []
    for root, sub_folders, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')) and not file.startswith('.'):
                image_files.append(os.path.join(root, file))
        for sub_folder in sub_folders:
            if not sub_folder.startswith('.'):
                image_files += get_images(os.path.join(folder, sub_folder))
    image_files.sort()
    return image_files

def calculate_runtime(num_images, framerate):
    return num_images / framerate

def create_timelapse(images, output_file, framerate):
    if not images:
        print("No images found in the specified folder.")
        sys.exit(1)

    # Read the first image to get the size
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_file, fourcc, framerate, (width, height))

    for image in tqdm(images, desc="Creating timelapse", unit="images"):
        frame = cv2.imread(image)
        video.write(frame)

    video.release()
    cv2.destroyAllWindows()

@click.command()
@click.option('-f', '--framerate', prompt='Enter the framerate for the timelapse video (frames per second)', type=int, help='Framerate for the timelapse video.')
@click.option('-s', '--skip-frames', prompt='Enter the number of images to skip between each frame', type=int, help='Number of images to skip between each frame.')
def main(framerate, skip_frames):
    folder = input("Enter the path to the folder containing images: ")

    images = get_images(folder)
    print("Found ", len(images), " images.")

    images = images[::skip_frames]
    runtime = calculate_runtime(len(images), framerate)

    print(f"The generated video will have {len(images)} frames and a runtime of {runtime:.2f} seconds.")
    confirm = input("Do you want to proceed? (yes/no): ")

    first_image_date = datetime.datetime.fromtimestamp(os.path.getmtime(images[0])).strftime('%Y-%m-%d')
    output_file = f"timelapse_{first_image_date}_fr{framerate}_skip{skip_frames}.mp4"

    if confirm.lower().startswith('y'):
        create_timelapse(images, output_file, framerate)
        print("Timelapse video created successfully.")
    else:
        print("Operation canceled.")

if __name__ == "__main__":
    main()
