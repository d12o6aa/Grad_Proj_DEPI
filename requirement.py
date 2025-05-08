import re
with open("requirements.txt") as f:
    lines = f.readlines()
with open("requirements.txt", "w") as f:
    for line in lines:
        f.write(re.sub(r" @ file://.*", "", line))
