import os
# import sys
# sys.path.insert(0, '../imageFunc')
# sys.path.insert(0, '../')
# import image_module as i_m
# print(i_m.ColorRecog((0,93,84.2)))


# os.system("export GOOGLE_CLOUD_PROJECT=rotricstest")
# print (os.environ["LANG"])
# aaa = os.environ.get("AAA")
# print(aaa)

for key in os.environ.keys():
    print(f"{key}={os.environ.get(key)}")
# b = os.environ["ENV_VAR_NAME1"]
# print (b)