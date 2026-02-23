import os
import glob
import xml.etree.ElementTree as ET

# Paths
LABELS_DIR = "backend/yolo_dataset/test_v1/labels"
CLASSES_FILE = "backend/yolo_dataset/test_v1/classes.txt"

def get_classes():
    if os.path.exists(CLASSES_FILE):
        with open(CLASSES_FILE, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def save_classes(classes):
    with open(CLASSES_FILE, 'w') as f:
        for c in classes:
            f.write(c + '\n')
    print(f"Updated classes.txt with {len(classes)} classes")

def convert(box, size):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    return (x * dw, y * dh, w * dw, h * dh)

def main():
    classes = get_classes()
    xml_files = glob.glob(os.path.join(LABELS_DIR, "*.xml"))
    print(f"Found {len(xml_files)} XML files.")

    new_classes_added = False

    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)

        txt_file = xml_file.replace('.xml', '.txt')
        
        with open(txt_file, 'w') as out_file:
            for obj in root.iter('object'):
                cls = obj.find('name').text
                if cls not in classes:
                    classes.append(cls)
                    new_classes_added = True
                    print(f"New class found: {cls}")
                
                cls_id = classes.index(cls)
                xmlbox = obj.find('bndbox')
                b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), 
                     float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                bb = convert(b, (w, h))
                out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

    if new_classes_added:
        save_classes(classes)
        print("Updated classes.txt")
    
    print("Conversion complete.")

if __name__ == "__main__":
    main()
