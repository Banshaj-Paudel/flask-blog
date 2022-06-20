import sys
import requests

try:
    file_name: str = sys.argv[1]
    packages_list = []
    if file_name.endswith(".py"):
        with open(file_name, "r") as f:
            for line in f.readlines():
                string = ""
                if line.startswith("from"):
                    for i in line[5:]:
                        if i != " " and i != ".":
                            string += i
                        else:
                            break
                    if string != "":
                        packages_list.append(string)
                if line.startswith("import"):
                    string += line[7 : len(line) - 1]
                    packages_list.append(string)
        for i in packages_list:
            response = requests.get(f"https://pypi.org/project/{i}/")
            if not (response.status_code) != 404:
                packages_list.remove(i)
        with open("requirements.txt", "w") as req_file:
            for package in packages_list:
                req_file.write(package + "\n")
    else:
        print("python files")
except IndexError:
    print("pass a python")
