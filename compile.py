import os

os.system("fbs clean")
os.system("fbs freeze")

# symlink resource files to load correctly
os.system(
    "ln -s '{0}/target/Fiddle.app/Contents/Resources/lib2to3' '{0}/target/Fiddle.app/Contents/MacOS/lib2to3'".format(
        os.getcwd()
    )
)
os.system("fbs installer")

print("Application successfully compiled!")
