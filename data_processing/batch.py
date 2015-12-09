from window_process import exhaustive_search
from utility import save_window_txt, crop_window, validate_windows
from image_process import sift_image_batch
from vlad_process import learn_vocabulary, vlad_vector_batch
from data_processing.utility import delete_file

image_name = "000012"
working_dir = "/Users/Kun/Desktop/CML_Project/sample/"
input_image_path = working_dir + "VOCdevkit/JPEGImages/"
annotation_path = working_dir + "VOCdevkit/Annotations/"
output_parent_path = working_dir + "output/"
unit_ratio_list = [0.2, 0.3]  # , 0.4, 0.5, 0.6, 0.7, 0.8]
overlap_ratio = 0.1

def batch_one_image(input_image_path, image_name, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio, k=10, max_iter=20, VLAD=True):
    print "------Begin batch for image", image_name
    metadata_path = '%s%s.xml' % (annotation_path, image_name)
    output_path = "%s%s/" % (output_parent_path, image_name)
    delete_file(file_path=output_path, isDir=True)
    temp_crop_path = '%stemp_crop/' % output_path
    image_path = '%s%s.jpg' % (input_image_path, image_name)
    print "\t======Generating windows"
    windows = exhaustive_search(image_path, metadata_path, unit_ratio_list, overlap_ratio)
    crop_window(image_path, temp_crop_path, windows=windows)
    temp_sift_path = '%stemp_sift/' % output_path
    print "\t======Sifting windows"
    sift_image_batch(input_path=temp_crop_path, output_path=temp_sift_path)
    windows = validate_windows(input_windows=windows, crop_path=temp_crop_path, sift_path=temp_sift_path)
    save_window_txt(windows, output_path, image_name)
    if VLAD:
        print "\t======Creating VLAD vectors"
        vocabulary = learn_vocabulary(input_path=temp_sift_path, k=k, max_iter=max_iter)
        vlad_vector_batch(temp_sift_path, output_path, vocabulary)
    print "\t------Done", image_name
    
c = batch_one_image(input_image_path, image_name, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio)

