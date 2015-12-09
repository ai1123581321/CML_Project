from window_process import exhaustive_search
from utility import save_window_txt, get_unprocessed_images, crop_window
from image_process import sift_image_batch

working_dir = "/Users/Kun/Desktop/CML_Project/sample/"
input_image_path = working_dir + "VOCdevkit/JPEGImages/"
annotation_path = working_dir + "VOCdevkit/Annotations/"
global_output_path = working_dir + "output/"
unit_ratio_list = [0.2, 0.3, 0.4, 0.5]
overlap_ratio = 0.1

def batch_one_image(input_image_path, image_name, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio, k_vocabulary):
    metadata_path = '%s%s.xml' % (annotation_path, image_name)
    output_path = "%s%s/" % (output_parent_path, image_name)
    temp_crop_path = '%stemp_crop/' % output_path
    image_path = '%s%s.jpg' % (input_image_path, image_name) 
    windows = exhaustive_search(image_path, metadata_path, output_path, unit_ratio_list, overlap_ratio)
    crop_window(image_path, temp_crop_path, win=windows)
    save_window_txt(windows, output_path, image_name)
    temp_vlad_path = '%stemp_crop/' % output_path
    sift_image_batch(input_image_path=temp_crop_path, output_path=temp_vlad_path, params=None)
    # vocabulary_batch(input_path, k=k_vocabulary )
    

def batch_all_images(input_image_path, annotation_path, output_parent_path,
            ratio_list, overlap_ratio, k_vocabulary):
    # Process all windows of all unprocessed images in a batch
    img_names = get_unprocessed_images(log_path=output_parent_path, all_image_path=input_image_path)
    count = 0
    for image_name in img_names:
        batch_one_image(input_image_path, image_name, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio)
        count += 1
    return count
