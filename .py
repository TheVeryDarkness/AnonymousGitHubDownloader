from genericpath import exists
from os import chdir, mkdir, stat
import pathlib
import sys
import requests
import json


def get_file(root, path, name, dir, size):
    URL = f"{root}/file{path}/{name}"

    LOCAL_PATH = f"{dir}/{name}"
    if exists(LOCAL_PATH):
        sz = stat(LOCAL_PATH).st_size
        if sz == size:
            print(f'{sz} == {size}, "{URL}" is skipped.')
            return
        else:
            print(f"{sz} != {size}, redownloading.")

    req = requests.get(URL)
    print(URL)

    with open(LOCAL_PATH, "wb") as f:
        f.write(req.content)
        f.close()


def traverse_dir(root: str, path: str, files: dict, dest_root: str):
    for name, content in files.items():
        # print(name, content)
        dir = f"{dest_root}{path}"
        if "size" not in content or type(content["size"]) != int:
            LOCAL_DIR = f"{dir}/{name}"
            if not exists(LOCAL_DIR):
                mkdir(LOCAL_DIR)
            traverse_dir(root, path + "/" + name, content, dest_root)
        else:
            get_file(root, path, name, dir, content["size"])


config = dict()

config_path = pathlib.Path(sys.path[0]) / "config.json"
if exists(config_path):
    with open(config_path, "rb") as f:
        _json = json.load(f)
        for key in ["dest", "root"]:
            if key in _json and type(_json[key]) == str:
                config[key] = _json[key]

if config["root"] == None:
    config["root"] = input("Root: ")  # https://anonymous.4open.science/api/repo/<name>
if config["root"].endswith("/"):
    config["root"] = config["root"][:-1]

if config["dest"] == None:
    config["dest"] = input("Download destination: ")  # ./download
if config["dest"].endswith("/"):
    config["dest"] = config["dest"][:-1]

files = requests.get("{}/files".format(config["root"])).json()
traverse_dir(config["root"], "", files, config["dest"])
