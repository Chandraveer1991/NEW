import os
import shutil
import glob


def remove_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)


def dictionary_creation(filename):
    define_dict = {}
    with open(filename) as f:
        for ln in f:
            if ln.startswith("DEFINE"):
                define_dict[ln.split(" ")[1]] = ln.split(" ")[-1].strip("&").strip("\n")
    return define_dict


def spool_header(counter):
    return "spool LOG/&" + str(int(counter) + 1) + "/&" + str(int(counter) + 1) + "_&" + "" + str(int(counter) + 2) + "..log"


def get_list(filename):
    with open(filename) as f:
        all_lines = f.readlines()
    return all_lines


def connection_block(counter):
    star_line = '*' * 50
    prompt_line = '\nPROMPT '
    start_text = "Start connecting to &" + str(int(counter) + 3) + " on &db_instance"
    connection = "\nconn &" + str(int(counter) + 4)
    finish_text = "Finish connecting to &" + str(int(counter) + 3) + " on &db_instance"
    return prompt_line + star_line + prompt_line + start_text + prompt_line + star_line + connection + prompt_line + star_line + prompt_line + finish_text + prompt_line + star_line


def create_script_block(counter, filename):
    star_line = '*' * 50
    prompt_line = '\nPROMPT '
    start_text = "Start &" + str(int(counter) + 5)
    finish_text = "Finish &" + str(int(counter) + 5)
    if filename == 'sql_recompile_template.sql':
        execution_block = "\nset serveroutput on size unlimited linesize 4004\nBEGIN\nIF '&recompile' = 'TRUE' THEN\napp_utils.validate_schema_objects(FALSE);\nELSE\ndbms_output.put_line('Schema recompliation disabled by UBS_Deploy parameter');\nEND IF;\nEND;\n/"
    else:
        execution_block = "\nPROMPT " + str(int(counter) + 6) + "\n@ " + str(int(counter) + 6)
    return prompt_line + star_line + prompt_line + start_text + prompt_line + star_line + execution_block + prompt_line + star_line + prompt_line + finish_text + prompt_line + star_line


def generic_file_creation(basedir):
    main_file = os.path.join(basedir, "apply_db_patch.sql")
    generic_template = ["sql_jira_template.sql", "sql_recompile_template.sql"]
    counter = len(dictionary_creation(main_file))

    spool_placeholder = spool_header(counter)
    all_lines = get_list(main_file)
    connection_placeholder = connection_block(counter)

    for ui, current_line in enumerate(all_lines):
        if current_line.startswith("PROMPT"):
            break

    for template in generic_template:
        file_name = os.path.join(basedir, template)
        remove_file(file_name)
        schema_block = create_script_block(counter, template)

        with open(file_name, 'a') as fa:
            fa.write("%s \n" % spool_placeholder)
            for i in range(1, ui):
                fa.write("%s \n" % all_lines[i].strip())
            fa.write("%s \n" % connection_placeholder)
            fa.write("%s \n" % schema_block)
            fa.write("%s \n" % "\nexit")
            fa.close()


def input_file(filename, stage, path):
    numb = 0
    main_file = os.path.join(path, filename)
    all_lines = get_list(main_file)
    last_line_number = len(all_lines)
    define_dict = dictionary_creation(main_file)
    remove_file(os.path.join(path, 'INPUT_' + stage + '_db_patch' + ".txt"))
    for current_line_no, current_line in enumerate(all_lines):
        if "conn " in current_line:
            count = current_line_no
            first = define_dict.get(all_lines[current_line_no - 2].split(" ")[4].strip("&"))
            second = define_dict.get(all_lines[current_line_no].split(" ")[1].strip("&").strip("\n"))
        if current_line.startswith("@") and not all_lines[current_line_no - 2].startswith("@"):
            third = all_lines[current_line_no - 3].split(" ")[3].strip()
            fourth = all_lines[current_line_no - 3].split(" ")[-1].strip()
            # print(fifth)
        if current_line.startswith("set serveroutput"):
            third = all_lines[current_line_no - 2].split(" ")[2].strip()
            fourth = define_dict.get(all_lines[current_line_no - 2].split(" ")[-1].strip("&").strip("\n"))
        if current_line.startswith("@") and not all_lines[current_line_no + 2].startswith("@"):
            start_line_no = max(count - 3, 0)
            end_line_no = min(last_line_number, current_line_no + 3 + 1)
            with open(os.path.join(path, 'INPUT_' + stage + '_db_patch') + '.txt', 'a') as fa:
                for i in range(start_line_no, end_line_no):
                    if all_lines[i].startswith("@"):
                        numb = numb + 1
                        sixth = str(numb) + '|' + 'JIRA|' + first + '|' + second + '|' + third + '|' + fourth + '|' + \
                                all_lines[i].split("@")[1].strip()
                        fa.write("%s \n" % sixth)
                fa.close()
        if current_line.startswith("/"):
            with open(os.path.join(path, 'INPUT_' + stage + '_db_patch') + '.txt', 'a') as fa:
                numb = numb + 1
                sixth = str(numb) + '|' + 'RECOMPILE|' + first + '|' + second + '|' + third + '|' + fourth
                fa.write("%s \n" % sixth)
                fa.close()


def log_creation(basedir, stage):
    if not os.path.exists(os.path.join(basedir, "LOG/" + stage)):
        os.makedirs(os.path.join(basedir, "LOG/" + stage))


if __name__ == '__main__':
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    generic_file_creation(path)
    available_action = ['apply_db_patch.sql']
    for sqlfile in available_action:
        if os.path.isfile(os.path.join(path, sqlfile)):
            stage = sqlfile.split("_")[0]
            input_file(sqlfile, stage, path)
            log_creation(path, stage)
