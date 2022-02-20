import os
import shutil
import glob


def search_string(path, sqlfile):
    versiont = version(path, sqlfile)
    main_filer = os.path.join(path, sqlfile.split("_")[0] + '_db_patch_*')
    main_filed = os.path.join(path, 'INPUT_' + sqlfile.split("_")[0] + '_*')
    for filename in glob.glob(main_filer):
        os.remove(filename)
    for filename1 in glob.glob(main_filed):
        os.remove(filename1)

    id = []
    main_file = os.path.join(path, sqlfile)
    with open(main_file) as f:
        all_lines = f.readlines()
        last_line_number = len(all_lines)
        numb = 0
        for ui, current_line1 in enumerate(all_lines):
            if current_line1.startswith("PROMPT"):
                break
        for current_line_no, current_line in enumerate(all_lines):
            if "conn " in current_line:
                count = current_line_no
                ola = current_line.split(" ")[1][1:].strip()
                if len(glob.glob(os.path.join(path, sqlfile.split("_")[0] + '_db_patch_') + ola + "*")) >= 1:
                    print("hi")
                    ola = ola + "_" + str(len(glob.glob(os.path.join(path, sqlfile.split("_")[0] + '_db_patch_') + ola + "*")) + 1)
                else:
                    print(glob.glob(os.path.join(path, sqlfile.split("_")[0] + '_db_patch_') + ola + "*"))
                    print("bye")
                    ola = ola + "_1"
                print(ola)
                if (current_line.startswith("@") and not all_lines[current_line_no + 2].startswith("@")) or (current_line.startswith("/")):
                    start_line_no = max(count - 3, 0)
                    end_line_no = min(last_line_number,current_line_no + 3 + 1)
                    with open(os.path.join(path, sqlfile.split("_")[0] + '_db_patch_') + ola + '.sql', 'a') as fa:
                        for i in range(0, ui):
                            id.append(all_lines[i].strip())
                            fa.write("%s \n" % all_lines[i].strip())
                        for i in range(start_line_no, end_line_no):
                            id.append(all_lines[i].strip())
                            fa.write("%s \n" % all_lines[i].strip())
                        fa.write("%s \n" % "exit")
                        fa.close()


def vgetu(path, sqlfile):
    versiont = version(path, sqlfile)
    file_id = []
    for file in os.listdir(path):
        if file.startswith(sqlfile.split("_")[0] + "_db_patch_"):
            file_id.append(file)
    for input_script in file_id:
        with open(os.path.join(path, input_script), "r") as inputed:
            for lnd in inputed:
                if lnd.startswith("@"):
                    with open(os.path.join(path, 'INPUT_') + input_script.split(" ")[0] + ".txt", "a") as fai:
                        fai.write("%s" % lnd[1:])
                        fai.close()
            inputed.close()

    file_id_input = []
    for file in os.listdir(path):
        if file.startswith(sqlfile.split("_")[0] + "_db_patch_"):
            file_id_input.append(file)

    if not os.path.exists(path + "/BACKUP/"):
        os.makedirs(path + "/BACKUP/")

    for input_script in file_id_input:
        shutil.copy2(os.path.join(path, input_script.strip()), os.path.join(path + "/BACKUP/", input_script.strip()) + '_backup')
        if os.path.isfile(os.path.join(path, 'INPUT_') + input_script.split(".")[0] + ".txt"):
            ser = open(os.path.join(path, 'INPUT_') + input_script.split(".")[0] + ".txt").read().splitlines()
            with open(os.path.join(path + "/BACKUP/", input_script.strip()) + '_backup') as oldfile, open(os.path.join(path, input_script.strip()), "w") as gu:
                for line in oldfile:
                    if not any(bad_word in line for bad_word in ser[1:]):
                        gu.write("%s" % line)

        user = input_script.split(sqlfile.split("_")[0] + '_db_patch_')[1].split(".")[0][:-2]
        with open(os.path.join(path, input_script.strip()), 'r') as uio:
            pos = uio.readlines()

        with open(os.path.join(path, input_script.strip()), 'w') as uior:
            for lineu in pos:
                if os.path.isfile(os.path.join(path, 'INPUT_' + input_script.split(".")[0] + ".txt")):
                    if lineu.startswith("spool"):
                        if "apply" == lineu.split(" ")[1].split(".")[0] or "rollback" == lineu.split(" ")[1].split(".")[0]:
                            lineu = lineu.replace(lineu.split(" ")[1], "LOG/" + lineu.split(" ")[1].split(".")[0] + "/" + lineu.split(" ")[1].split(".")[0] + "_&45" + ".." + lineu.split(".")[1])
                        else:
                            lineu = lineu.replace(lineu.split(" ")[1], "LOG/" + lineu.split(" ")[1].split(".")[0].split("_")[1] + "/" + lineu.split(" ")[1].split(".")[0] + "_&45" + ".." + lineu.split(".")[1])
                        lineu = lineu.replace(ser[0], '&44')
                    else:
                        if lineu.startswith("spool"):
                            if "apply" == lineu.split(" ")[1].split(".")[0] or "rollback" == lineu.split(" ")[1].split(".")[0]:
                                lineu = lineu.replace(lineu.split(" ")[1], "LOG/" + lineu.split(" ")[1].split(".")[0] + "/" + lineu.split(" ")[1].split(".")[0] + "_recompiling_" + user + "." + lineu.split(".")[1])
                            else:
                                lineu = lineu.replace(lineu.split(" ")[1], "LOG/" + lineu.split(" ")[1].split(".")[0].split("_")[1] + "/" + lineu.split(" ")[1].split(".")[0] + "_&45" + ".." + lineu.split(".")[1])


                    uior.write(lineu)
            uior.close()

def log_creation (path, sqlfile):
    if not os.path.exists(os.path.join(path, "LOG/" + sqlfile.split("_")[0])):
        os.makedirs(os.path.join(path, "LOG/" + sqlfile.split("_")[0]))

def version(path, sqlfile):
    main_file = os.path.join(path, sqlfile)
    with open(main_file) as tui:
        for liney in tui:
            if liney.startswith("DEFINE"):
                lineyo = liney.split(" ")[3][1:].strip()
    return lineyo


if __name__ == '__main__':
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    arry = ['apply_db_patch.sql']
    for sqlfile in arry:
        if os.path.isfile(os.path.join(path, sqlfile)):
            search_string(path, sqlfile)
            vgetu(path, sqlfile)
            log_creation(path, sqlfile)
