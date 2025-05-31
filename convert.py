import sys
import os
import shutil
from zipfile import ZipFile

from drunub.dings import error, config, rename_files, extract_skin_meshes, get_tm_user_dir
from drunub.skinfix import fix_skin


OUT_EXTENSIONS = [".dds", ".mesh.gbx", ".txt", ".wav", ".ogg"]

WORK_TEMP_DIR = "./temp/"


OUT_DIR = "./out/"

conf = config("./paths.ini")

blender = conf.get("blender", "./blender/blender.exe")
tm2020 = conf.get("tm2020")

tm_user_dir = get_tm_user_dir(os.path.join(tm2020, "nadeo.ini"))

ni_work_dir = tm_user_dir + "\\Work\\Skins\\temp\\"
ni_out_dir = tm_user_dir + "\\Skins\\temp\\"

importer = tm2020 + "\\nadeoimporter.exe"

if not os.path.isfile(blender):
    error(f"Can't find Blender, nothing to do :0(\nCheck paths.ini or {blender}")


skin_zip_path = sys.argv[1]

print("Extracting skin...\n\n")

shutil.rmtree(WORK_TEMP_DIR, ignore_errors=True)

with ZipFile(skin_zip_path, 'r') as z:
    z.extractall(WORK_TEMP_DIR)


rename_files(WORK_TEMP_DIR)
extract_skin_meshes(WORK_TEMP_DIR)

blender_script = os.path.join(WORK_TEMP_DIR, "temp.py")
os.system(f"{blender} --background --factory-startup -P {blender_script}")


if not os.path.isfile(WORK_TEMP_DIR + "mainbody.fbx"):
    error("Mainbody.fbx missing, something failed :0(")

shutil.move(WORK_TEMP_DIR + "mainbody.fbx", ni_work_dir + "mainbody.fbx")
shutil.copyfile("./drunub/export/MainBody.MeshParams.xml", ni_work_dir + "MainBody.MeshParams.xml")

if os.system(importer + " Mesh Skins\\temp\\MainBody.fbx"):
    error("NadeoImporter failed :0(")

fix_skin(ni_out_dir + "mainbody.mesh.gbx")

shutil.move(ni_out_dir + "mainbody.mesh.gbx", WORK_TEMP_DIR + "mainbody.mesh.gbx")

skin_name = os.path.basename(skin_zip_path).rsplit(".", 1)[0]

out_dir_files = list(os.walk(WORK_TEMP_DIR))[0][2]

out_files = []
for fn in out_dir_files:
    for ext in OUT_EXTENSIONS:
        if fn.lower().endswith(ext):
            out_files.append(WORK_TEMP_DIR + fn)


with ZipFile(OUT_DIR + skin_name + " tm2020.zip", "w") as z:
    for fn in out_files:
        z.write(fn, arcname=os.path.basename(fn))
    z.write("./drunub/export/drunub.txt", arcname="drunub.txt")



shutil.rmtree(WORK_TEMP_DIR, ignore_errors=True)