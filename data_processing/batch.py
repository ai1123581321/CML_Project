from window_process import exhaustive_search, save_window_txt, crop_window, validate_windows, de_serialize_window
from utility import delete_file, append_file, get_target_pos_names, list_all_files, load_matrix, save_matrix, pca_dataset
from image_process import sift_image_batch, parse_image_metadata
from vlad_process import vlad_vector_batch, learn_vocabulary, get_data_set_X_Y
from os.path import isfile

def batch_one_image_pre_VLAD(input_image_path, image_name, metadata_path, output_parent_path,
            unit_ratio_list, overlap_ratio):
    print "------Begin batch for image", image_name
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

def batch_one_image_dataset(global_X_path, global_Y_path, img_window_path, img_vlad_path, img_metadata_path, target, overlap_threshold=0.5):
    pic = parse_image_metadata(file_path=img_metadata_path, parseObject=True)
    winL = de_serialize_window(input_path=img_window_path)
    vladL = load_matrix(input_path=img_vlad_path).tolist()
    dataset = get_data_set_X_Y(winL, vladL, pic, target, overlap_threshold)
    X, Y = dataset[0], dataset[1]
    append_file(dest_file=global_X_path, strInput=X)
    append_file(dest_file=global_Y_path, strInput=Y)
    
def batch_all_images(input_image_path, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio, target, target_pos_path, target_count=20, pca=True,
            k=30, max_iter=30, preVLAD=False, voca_path=None, dataset_mode=False, overlap_threshold=0.5):
    global_sift_path = '%sglobal_sift.txt' % (output_parent_path)
    image_name_list = get_target_pos_names(input_path=target_pos_path, target=target, target_count=target_count)
    sift_path_L = []
    if preVLAD:
        delete_file(file_path=global_sift_path)
        for image_name in image_name_list:
            metadata_path = '%s%s.xml' % (annotation_path, image_name)
            win_sift_path = batch_one_image_pre_VLAD(input_image_path, image_name, metadata_path, output_parent_path,
                unit_ratio_list, overlap_ratio)
            sift_path_L.append(win_sift_path)
            append_file(dest_file=global_sift_path, input_path=win_sift_path)
        print "----------pre-VLAD Done"
    else:
        all_dir = list_all_files(input_path=output_parent_path, onlyDir=True)
        for d in all_dir:
            sift_path_L.append("%s%s/temp_sift/" % (output_parent_path, d))
        print "----------pre-VLAD is enabled"
    if voca_path is None or not isfile(voca_path):
        print "~~~~~~~Learning vocabulary by the sift vectors of all windows of all images"
        vector_matrix = None
        if pca:
            vector_matrix = pca_dataset(input_path=global_sift_path)
        vocabulary = learn_vocabulary(input_path=global_sift_path,
                    k=k, max_iter=max_iter, single_file=True, vector_matrix=vector_matrix)
        save_matrix(v=vocabulary, output_path=voca_path)
        print "~~~~~~~Learning vocabulary done"
    else:
        print "~~~~~~~Loading existing vocabulary"
        vocabulary = load_matrix(input_path=voca_path)
    for i in xrange(len(image_name_list)):
        image_name = image_name_list[i]
        output_path = "%s%s/" % (output_parent_path, image_name)
        print "\t======Creating VLAD vectors"
        vlad_vector_batch(input_path=sift_path_L[i], output_path=output_path + image_name, vocabulary=vocabulary)
        print "\t======VLAD Done for", image_name
    if dataset_mode:
        print "^^^^^^^^^^Generate data set for global windows and VLAD"
        global_X_path = output_parent_path + "global_X.txt"
        global_Y_path = output_parent_path + "global_Y.txt"
        delete_file(global_X_path)
        delete_file(global_Y_path)
        for img_name in image_name_list:
            img_window_path = "%s%s/%s_windows.txt" % (output_parent_path, img_name , img_name)
            img_vlad_path = "%s%s/%s_vlad.txt" % (output_parent_path, img_name , img_name)
            metadata_path = '%s%s.xml' % (annotation_path, image_name)
            batch_one_image_dataset(global_X_path, global_Y_path, img_window_path,
                        img_vlad_path, metadata_path, target, overlap_threshold=overlap_threshold)
            print "\tData set done for", img_name
    print "....................All done"
