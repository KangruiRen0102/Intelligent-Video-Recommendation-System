import subprocess
import os 
import pandas as pd

def get_git_revisions_hash():
    hashes = []
    hashes.append(subprocess.check_output(['git', 'rev-parse', 'HEAD']))
    # hashes.append(subprocess.check_output(['git', 'rev-parse', 'HEAD^']))
    return hashes[0].decode('ascii')


def write_version_to_model(path, commit_id):
    file = path + "model_version.txt"
    f = open(file, "w")
    f.write("model version, " + commit_id)
    f.write("dataset version, " + commit_id)
    f.write("pipeline version, " + commit_id)
    f.close()

def write_version_to_dataset(path, commit_id):
    file = path + "dataset_version.txt"
    f = open(file, "w")
    f.write(commit_id)
    f.close()

def checkout_previous_dataset(commit_id):
    subprocess.run(["git", "checkout", str(commit_id)])
    subprocess.run(["dvc", "checkout"])

def read_version_from_model(path):
    d = {}
    file = path + "model_version.txt"
    with open(file) as f:
        for line in f:
            (key, value) = line.split(",")
            d[key] = value
    return d



if __name__ == "__main__":
    example = True
    if example == True:
        my_path = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.join(my_path, '../checkpoint/model/')
        dataset_path = os.path.join(my_path, '../dataset/final_csv/')
        hashes = get_git_revisions_hash()

        # track version files
        write_version_to_model(model_path, hashes)
        verions = read_version_from_model(model_path)

