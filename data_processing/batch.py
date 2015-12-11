from window_process import exhaustive_search
from utility import save_window_txt, crop_window, validate_windows, delete_file, append_file, get_target_pos_names
from image_process import sift_image_batch
from vlad_process import vlad_vector_batch
from data_processing.vlad_process import learn_vocabulary
from data_processing.utility import list_all_files

def batch_one_image_pre_VLAD(input_image_path, image_name, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio):
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
    return temp_sift_path
    
def batch_one_image_VLAD(window_sift_path, output_path, vocabulary):
    print "\t======Creating VLAD vectors"
    vlad_vector_batch(window_sift_path, output_path, vocabulary)
    
def batch_all_images(input_image_path, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio, target, target_pos_path, target_count=20,
            k=30, max_iter=30, preVLAD=False):
    global_sift_path = '%s%s_global_sift.txt' % (output_parent_path, target)
    image_name_list = get_target_pos_names(input_path=target_pos_path, target=target, target_count=target_count)
    sift_path_L = []
    if preVLAD:
        delete_file(file_path=global_sift_path)
        for image_name in image_name_list:
            win_sift_path = batch_one_image_pre_VLAD(input_image_path, image_name, annotation_path, output_parent_path,
                unit_ratio_list, overlap_ratio)
            sift_path_L.append(win_sift_path)
            append_file(dest_file=global_sift_path, input_path=win_sift_path)
        print "----------pre-VLAD Done", image_name
    else:
        all_dir = list_all_files(input_path=output_parent_path, onlyDir=True)
        for d in all_dir:
            sift_path_L.append("%s%s/temp_sift/" % (output_parent_path, d))
        print "----------pre-VLAD is enabled"
    print "~~~~~~~Learning vocabulary by the sift vectors of  all windows of all images"
    vocabulary = learn_vocabulary(input_path=global_sift_path, k=k, max_iter=max_iter, single_file=True)
    print "~~~~~~~Learning vocabulary done"
    for i in xrange(len(image_name_list)):
        image_name = image_name_list[i]
        output_path = "%s%s/" % (output_parent_path, image_name)
        batch_one_image_VLAD(window_sift_path=sift_path_L[i], output_path=output_path + image_name, vocabulary=vocabulary)
        print "\t======VLAD Done for", image_name
    print "....................All done"
