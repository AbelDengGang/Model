# -*- coding:utf-8 -*-
import os
import shutil
from pycocotools.coco import COCO
import argparse

# coco_ver = 2014
# coco_home = '/home/gang/YOLO/coco/'
# coco_root = coco_home + f'/coco{coco_ver}/'
custom_category = {
                    'cell phone': 0,
                    'person': 1,
                    }
category_id_map = {}

def load_annotation(coco_ver = '2014',type='train'):
    global coco_root
    annFile = coco_root + 'annotations/' + f'instances_{type}{coco_ver}.json'
    coco=COCO(annFile)
    return coco

def construct_category_list(coco):
    """
    setup id map between coco and custom data set
    """
    global category_id_map
    for custom_key, custom_id in custom_category.items():
        ids = coco.getCatIds(custom_key)
        if len(ids) == 0:
            print(f'Can not find category {custom_key} in coco data set !!!!!!')
            raise Exception()

        id_coco = ids[0]
        category_id_map[id_coco] = custom_id

def get_img_ids(coco):
    """
    遍历category_id_map, 找出包含有key的图片列表
    """
    global category_id_map
    img_ids_uion = []

    for coco_category_id in category_id_map.keys():
        img_ids = coco.getImgIds(catIds = [coco_category_id])
        img_ids_uion = list(set(img_ids_uion) | set(img_ids))
    
    # here's a test for images with 2 categories
    # img_ids = coco.getImgIds(category_id_map.keys())

    return img_ids_uion



def annotation_coco_to_yolo(coco_ann,imgInfo = None,category_id_map=None):
    
    # coco bbox: top_left(x,y) (w,h)
    bbx_coco = coco_ann['bbox']
    bbx_coco_w = bbx_coco[2]
    bbx_coco_h = bbx_coco[3]
    bbx_center_x = bbx_coco[0] +  bbx_coco_w / 2
    bbx_center_y = bbx_coco[1] +  bbx_coco_h / 2
    
    imgId = coco_ann['image_id']
    category_id = coco_ann['category_id']
    
    # 把 coco category_id 映射成自定义数据集的 category_id
    if category_id_map:
        category_id = category_id_map[category_id]
        
    # 出于性能考虑,优先已经准备好的imgInfo
    if imgInfo is None:
        imgInfo = coco.loadImgs(imgId)[0]
        
    height = imgInfo['height']
    width = imgInfo['width']
    file_name = imgInfo['file_name']
    
    yolo_x = bbx_center_x / width
    yolo_y = bbx_center_y / height
    yolo_w = bbx_coco_w / width
    yolo_h = bbx_coco_h / height
    
    return (category_id, yolo_x, yolo_y, yolo_w, yolo_h,file_name)

def construct_single_yolo_label_file(coco,img_id):
    global category_id_map

    imgInfo = coco.loadImgs(img_id)[0]
    file_name = imgInfo['file_name']
    
    
    annIds = coco.getAnnIds(imgIds=[img_id])
    anns = coco.loadAnns(annIds)

    # 获取所有在interested_ids列表中的annotation
    interested_ids = category_id_map.keys()
    interested_anns = [ann for ann in anns if ann['category_id'] in interested_ids]
    yolo_labels = []

    for interested_ann in interested_anns:
        category_id, yolo_x, yolo_y, yolo_w, yolo_h, file_name_drop = annotation_coco_to_yolo(coco_ann = interested_ann, imgInfo = imgInfo, category_id_map = category_id_map)
        yolo_labels.append(f"""{category_id} {yolo_x} {yolo_y} {yolo_w} {yolo_h}""")

    # print(file_name,img_id, yolo_labels)
    return yolo_labels,file_name



def convert_to_yolo_file_name(coco,file_name,yolo_type,yolo_ver,coco_picture_folder):
    global coco_root
    yolo_custom_pic_folder = coco_root + "yolo_custom_picture/"

    # coco2017文件名里没有train/val前缀,为了避免冲突,统一加上 yolo_type yolo_ver 前缀
    custom_yolo_file_name = f'{yolo_type}_{yolo_ver}_{file_name}'

    # yolo 图片名
    yolo_pic_file = yolo_custom_pic_folder + custom_yolo_file_name

    #label name
    label_file_name = yolo_custom_pic_folder + custom_yolo_file_name.split('.')[0] + '.txt'

    return yolo_pic_file, label_file_name


def create_link_and_label_file(coco,file_name,yolo_type,yolo_ver,coco_picture_folder):
    """
    在coco_picture_folder目录下创建文件的符号链接,并返回 .txt/jpg 文件路径
    """
    global coco_root
    yolo_custom_pic_folder = coco_root + "yolo_custom_picture/"

    isExists=os.path.exists(yolo_custom_pic_folder)
    if not isExists:
        os.makedirs(yolo_custom_pic_folder)
        print(f"create {yolo_custom_pic_folder}")

    yolo_pic_file, label_file_name = convert_to_yolo_file_name(coco = coco,file_name = file_name,yolo_type = yolo_type,yolo_ver = yolo_ver,coco_picture_folder = coco_picture_folder)
    # 创建符号链接
    if os.path.exists(yolo_pic_file): # 在这个目录下第二次运行,如果不删除原来的符号连接,再次创建时会报错
        os.remove(yolo_pic_file)
    os.symlink(coco_picture_folder + file_name,yolo_pic_file)

    #创建空.txt文件
    f = open(label_file_name , "w")
    f.close()

    return yolo_pic_file,label_file_name

    


def construct_yolo_labels(coco,img_ids,yolo_type,yolo_ver,coco_picture_folder):
    global coco_root
    pic_file_name_with_select_cat_list = []
    for img_id in img_ids:
        labels ,file_name = construct_single_yolo_label_file(coco=coco,img_id = img_id)

        pic_file_name, label_file_name = convert_to_yolo_file_name(coco = coco , file_name = file_name, yolo_type=yolo_type,yolo_ver=yolo_ver,coco_picture_folder=coco_picture_folder)

        print("write label to {}".format(label_file_name))
        pic_file_name_with_select_cat_list.append(pic_file_name)
        
        with open(label_file_name , "w") as f:
            for label in labels:
                f.write(label + '\n')
            f.close()
    print('{} label writed'.format(len(img_ids)))    
    
    # 生成只包含指定种类的图片的列表文件
    pic_with_cat_list_file_name = coco_root + f'yolo_{yolo_type}_pic_cat_only_lists.txt'
    f_pic_file = open(pic_with_cat_list_file_name,'w')    
    for pic_file_name in pic_file_name_with_select_cat_list:
        f_pic_file.write(pic_file_name + '\n')
    f_pic_file.close()
    print(f"Write picture with category file list into {pic_with_cat_list_file_name}")



def construct_background_yolo_labels(coco, yolo_type,yolo_ver,coco_picture_folder):
    """
    为所有jpg文件在coco_picture_folder建立链接,并建立空.txt文件.
    在这之后调用construct_yolo_labels 建立正样本.其余的空 .txt 文件作为负样本
    """
    pic_file_list = []
    for local_file in os.listdir(coco_picture_folder):
        file_path = os.path.join(coco_picture_folder, local_file)  
        if os.path.isdir(file_path):  
            pass
        else:
            file_name_parts = os.path.splitext(local_file)
            if len(file_name_parts) == 2:
                if file_name_parts[1] == ".jpg":
                    pic_file_list.append(local_file)

    # 生成包含所有图片的列表文件
    pic_file_list_file_name = coco_root + f'yolo_{yolo_type}_pic_lists.txt'
    f_yolo_pic_list = open(pic_file_list_file_name,'w')

    for pic_file in pic_file_list:
        yolo_pic_file, _ = create_link_and_label_file(coco = coco , file_name = pic_file, yolo_type=yolo_type,yolo_ver=yolo_ver,coco_picture_folder=coco_picture_folder)

        f_yolo_pic_list.write(yolo_pic_file+'\n')

    f_yolo_pic_list.close()
    print('{} symbol created'.format(len(pic_file_list)))
    print(f'write all picture file list into {pic_file_list_file_name}')
    pass


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--coco_home", type=str, required=True, help="the folder including coco2014")
    parser.add_argument("--coco_ver", type=str, default="2014", help="coco version, such 2014 , 2017")
    parser.add_argument("--coco_type", type=str, default="train", help="data set type, such train , val")

    opt = parser.parse_args()
    print(opt)
    coco_home = opt.coco_home
    coco_ver = opt.coco_ver
    coco_root = coco_home + f'/coco{coco_ver}/'
    coco_dataset_type = opt.coco_type
    coco = load_annotation(coco_ver = coco_ver,type=coco_dataset_type)
    construct_category_list(coco = coco)
    img_ids = get_img_ids(coco = coco)
    construct_background_yolo_labels(coco=coco,yolo_type = coco_dataset_type,yolo_ver = coco_ver,coco_picture_folder = coco_root + f'{coco_dataset_type}{coco_ver}/')
    construct_yolo_labels(coco=coco,img_ids = img_ids, yolo_type = coco_dataset_type,yolo_ver = coco_ver,coco_picture_folder = coco_root + f'{coco_dataset_type}{coco_ver}/')


    
