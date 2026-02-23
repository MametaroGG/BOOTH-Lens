import yaml

CLASSES_FILE = "backend/yolo_dataset/test_v1/classes.txt"
DATA_YAML = "backend/yolo_dataset/test_v1/data.yaml"

def main():
    with open(CLASSES_FILE, 'r') as f:
        classes = [line.strip() for line in f.readlines() if line.strip()]

    with open(DATA_YAML, 'r') as f:
        data = yaml.safe_load(f)

    data['nc'] = len(classes)
    data['names'] = {i: name for i, name in enumerate(classes)}

    with open(DATA_YAML, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print(f"Updated data.yaml with {len(classes)} classes.")

if __name__ == "__main__":
    main()
