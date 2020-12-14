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

def construct_yolo_labels(coco,img_ids,yolo_type,coco_picture_folder):
    global coco_root
    yolo_custom_pic_folder = coco_root + "yolo_custom_picture/"

    isExists=os.path.exists(yolo_custom_pic_folder)
    if not isExists:
        os.makedirs(yolo_custom_pic_folder)
        print(f"create {yolo_custom_pic_folder}")


    f_yolo_pic = open(coco_root + f'yolo_{yolo_type}_pic_lists.txt','w')
    for img_id in img_ids:
        labels ,file_name = construct_single_yolo_label_file(coco=coco,img_id = img_id)
        # coco2017文件名里没有train/val前缀,为了避免冲突,统一加上 yolo_type 前缀
        custom_yolo_file_name = f'{yolo_type}_{file_name}'

        #todo write label into file
        label_file_name = yolo_custom_pic_folder + custom_yolo_file_name.split('.')[0] + '.txt'
        print(custom_yolo_file_name)

        yolo_pic_file = yolo_custom_pic_folder + custom_yolo_file_name
        if os.path.exists(yolo_pic_file): # 在这个目录下第二次运行,如果不删除原来的符号连接,再次创建时会报错
            os.remove(yolo_pic_file)
        os.symlink(coco_picture_folder + file_name,yolo_custom_pic_folder + custom_yolo_file_name)

        f_yolo_pic.write(yolo_pic_file+'\n')

        with open(label_file_name , "w") as f:
            for label in labels:
                f.write(label + '\n')
            f.close()
            
    f_yolo_pic.close()


    


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
    construct_yolo_labels(coco=coco,img_ids = img_ids, yolo_type = coco_dataset_type,coco_picture_folder = coco_root + f'{coco_dataset_type}{coco_ver}/')


    
