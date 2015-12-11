from batch import batch_all_images

working_dir = "/Users/Kun/Desktop/Project_CML/sample/"
input_image_path = working_dir + "JPEGImages/"
annotation_path = working_dir + "Annotations/"
output_parent_path = working_dir + "output/"
target_pos_path = working_dir + "ImageSets/Main/"
unit_ratio_list = [0.2, 0.3 , 0.4, 0.5, 0.6, 0.7, 0.8]
overlap_ratio = 0.1
target = "sheep"
target_count = 20
k = 30
max_iter = 30
batch_all_images(input_image_path, annotation_path, output_parent_path,
            unit_ratio_list, overlap_ratio, target,
            target_pos_path, target_count=target_count, k=k, max_iter=max_iter)
