import os
import shutil
import glob

def input_file(path, sqlfile):
    input_file = os.path.join(path, 'INPUT_' + sqlfile.split(".")[0] + '.txt')
    for filename in glob.glob(input_file):
        os.remove(filename)
    main_file = os.path.join(path, sqlfile)
    numb = 0
    with open(main_file) as f:
        all_lines = f.readlines()
        last_line_number = len(all_lines)
        for current_line_no, current_line in enumerate(all_lines):
            if "conn " in current_line:
                count = current_line_no
                first = all_lines[current_line_no].split(" ")[1].strip()
                second = all_lines[current_line_no - 2].split("PROMPT")[1].strip()
                third = all_lines[current_line_no + 2].split("PROMPT")[1].strip()
            if current_line.startswith("@") and not all_lines[current_line_no - 2].startswith("@"):
                fourth = all_lines[current_line_no - 3].split("PROMPT")[1].strip()
            if current_line.startswith("set serveroutput"):
                fourth = all_lines[current_line_no - 2].split("PROMPT")[1].strip()
            if current_line.startswith("@") and not all_lines[current_line_no + 2].startswith("@"):
                fifth = all_lines[current_line_no + 2].split("PROMPT")[1].strip()
            if current_line.startswith("/"):
                fifth = all_lines[current_line_no + 2].split("PROMPT")[1].strip()
            if (current_line.startswith("@") and not all_lines[current_line_no + 2].startswith("@")) or (current_line.startswith("/")):
                start_line_no = max(count - 3, 0)
                end_line_no = min(last_line_number, current_line_no + 3 + 1)
                with open(os.path.join(path, 'INPUT_' + sqlfile.split("_")[0] + '_db_patch') + '.txt', 'a') as fa:
                    for i in range(start_line_no, end_line_no):
                        if all_lines[i].startswith("@"):
                            numb = numb + 1
                            sixth = str(numb) + '|' + 'JIRA|' + first + '|' + second + '|' + third + '|' + fourth + '|' + fifth + '|' + all_lines[i].split("@")[1].strip()
                            fa.write("%s \n" % sixth)
                    fa.close()
            if current_line.startswith("/"):
                with open(os.path.join(path, 'INPUT_' + sqlfile.split("_")[0] + '_db_patch') + '.txt', 'a') as fa:
                    numb = numb + 1
                    sixth = str(numb) + '|' + 'RECOMPILE|' + first + '|' + second + '|' + third + '|' + fourth + '|' + fifth
                    fa.write("%s \n" % sixth)
                    fa.close()

def version(path, sqlfile):
    main_file = os.path.join(path, sqlfile)
    with open(main_file) as tui:
        for liney in tui:
            if liney.startswith("DEFINE"):
                lineyo = liney.split(" ")[3][1:].strip()
    return lineyo


def generic_template(path, sqlfile):
    generic_template = os.path.join(path, sqlfile.split(".")[0] + '_generic' + '.sql')
    for filename in glob.glob(generic_template):
        os.remove(filename)
    main_file = os.path.join(path, sqlfile)

    generic_version = version(path, sqlfile)

    if sqlfile.split("_")[0] == 'apply':
        spool_header = "spool LOG/apply/apply_&" + str(int(generic_version) + 1) + "..log"
    else:
        spool_header = "spool LOG/rollback/rollback_&" + str(int(generic_version) + 1) + "..log"


    if_header = "IF '&" + str(int(generic_version) + 2) + "' = 'JIRA' THEN\n\n"
    PROMPT_header = "PROMPT **************************************************\n"
    prompt_start = "PROMPT &" + str(int(generic_version) + 3) + "\n"
    conn_header = "conn &" + str(int(generic_version) + 4)+ "\n"
    prompt_finish = "PROMPT &" + str(int(generic_version) + 5)+ "\n"
    prompt_start_execution = "PROMPT &" + str(int(generic_version) + 6)+ "\n"
    prompt_finish_execution = "PROMPT &" + str(int(generic_version) + 7)+ "\n"
    jira_header = "PROMPT &" + str(int(generic_version) + 8) + "\n" + "@&" + str(int(generic_version) + 8)+ "\n"
    else_header = "ELSE\n"
    recompile_header="set serveroutput on size unlimited linesize 4004\nBEGIN\nIF '&recompile' = 'TRUE' THEN\napp_utils.validate_schema_objects(FALSE);\nELSE\ndbms_output.put_line('Schema recompliation disabled by UBS_Deploy parameter');\nEND IF;\nEND;\n/\n"

    final_jira_header = if_header + PROMPT_header + prompt_start + PROMPT_header + conn_header + PROMPT_header + prompt_finish + PROMPT_header + '\n' + PROMPT_header + prompt_start_execution + PROMPT_header + jira_header + PROMPT_header + prompt_finish_execution  + PROMPT_header
    final_recompile_header = PROMPT_header + prompt_start + PROMPT_header + conn_header + PROMPT_header + prompt_finish + PROMPT_header + '\n' + PROMPT_header + prompt_start_execution + PROMPT_header + recompile_header + PROMPT_header + prompt_finish_execution  + PROMPT_header
    exit_header = "END IF;\nexit\n"

    print(spool_header)
    print(final_jira_header)
    print(else_header)
    print(final_recompile_header)
    print(exit_header)

    with open(main_file) as f:
        all_lines = f.readlines()
        last_line_number = len(all_lines)
        numb = 0
        for ui, current_line1 in enumerate(all_lines):
            if current_line1.startswith("PROMPT"):
                break
        with open(os.path.join(path, sqlfile.split(".")[0] + '_generic' + '.sql'), 'a') as fa:
            fa.write("%s \n" % spool_header)
            for i in range(1, ui):
                fa.write("%s \n" % all_lines[i].strip())
            fa.write("%s \n" % final_jira_header)
            fa.write("%s \n" % else_header)
            fa.write("%s \n" % final_recompile_header)
            fa.write("%s \n" % exit_header)
            fa.close()

def log_creation (path, sqlfile):
    if not os.path.exists(os.path.join(path, "LOG/" + sqlfile.split("_")[0])):
        os.makedirs(os.path.join(path, "LOG/" + sqlfile.split("_")[0]))


if __name__ == '__main__':
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    arry = ['apply_db_patch.sql']
    for sqlfile in arry:
        if os.path.isfile(os.path.join(path, sqlfile)):
            input_file(path, sqlfile)
            generic_template(path, sqlfile)
            log_creation(path, sqlfile)
