from pyspark import SparkConf, SparkContext, SparkFiles

sc = SparkContext(conf=SparkConf())


# ./requirements.txt
import emoji
print(emoji.emojize("\n\n Beginning Execution \n\n"))

# ./src/src_module.py
import src_module

# ./src/example_package/ex_package
import ex_package

# ./included/code/caesarcipher.zip
from caesarcipher import CaesarCipher
cc = CaesarCipher()


# ./include/code/included_folderA/included_module.py
import included_module

print(f"\n\nWhat does the module say?\n  {included_module.the_module_says()}\n\n")

# ./include/include_assets.txt
with open(SparkFiles.get("sagely.txt")) as art_file:
    print(f"\nSage says: {art_file.read()}\n\n")

# ./include/include_code.txt
import my_module

# ./include/assets/fancy_art.txt
with open(SparkFiles.get("fancy_art.txt")) as art_file:
    print(art_file.read())

print(emoji.emojize("\n The File Executed Successfully \n\n"))

