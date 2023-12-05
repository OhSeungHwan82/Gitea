import cx_Oracle
import subprocess
import shutil
import os
import stat
import requests
import chardet
import datetime

def current_time(msg):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(msg, formatted_time)

# 디렉토리 경로
# dir_path = '../Prod-IIMS-PLUS'
# # 권한 플래그 (예: 0o755)
# permissions = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
# # 권한 변경
# os.chmod(dir_path, permissions)
# dir_path2 = './release_build/src'
# # 권한 플래그 (예: 0o755)
# permissions2 = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
# # 권한 변경
# os.chmod(dir_path2, permissions2)

def run_git_command_prod(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\deploy\release_build\src")
    output, error = process.communicate()
    return output, error

def webhook_send(content):
    dataInfo = {'content':content}
    URL = 'https://teamroom.nate.com/api/webhook/f3af6d62/l4y0v5TG4fSZWdf94A0drnDb'
    URL = 'https://teamroom.nate.com/api/webhook/20a53730/MaHSX4CwEq86fS5bCuqsb2Up'
    response = requests.post(URL, data=dataInfo)

def detect_encoding(file_path):
    with open(file_path,'rb') as file:
        raw_data = file.read()
        
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    confidence = result['confidence']
    
    return result

def build(get_commit_hash):
    #print('get_commit_hash',get_commit_hash)
    # 배치 파일 실행 및 결과 저장할 파일 경로
    output_file = "release_build_output.txt"

    # 배치 파일 실행
    subprocess.run("release_build.bat", stdout=open(output_file, "w"), stderr=subprocess.STDOUT, shell=True)

    # 파일 내용 읽기
    encoding_str = "ansi"
    result = detect_encoding(output_file)
    if result['encoding'] =="utf-8":
        encoding_str = "utf-8"

    with open(output_file, "r",encoding=encoding_str) as file:
        output_content = file.read()

    # 실행 결과 출력
    print(output_content)

    # 에러 여부 체크
    if "warning" in output_content.lower() or "error" in output_content.lower():
        #어느 커밋에서 오류인지 알 수 없으니까 커밋별 변경파일을 가져옴
        output, error = run_git_command_prod(f"git log --pretty=format:%h,%s,%an {get_commit_hash}..")
        if output:
            print(output.decode("utf-8"))
            commit_hash_list = output.decode("utf-8")
        if error:
            print(error)
        lines = commit_hash_list.split("\n")
        for line in lines:
            
            insert_data = line.split(",")
            commit_hash = insert_data[0]
            commit_msg = insert_data[1]
            commit_user = insert_data[2]
            output, error = run_git_command_prod(f"git diff-tree --no-commit-id --name-only -r {commit_hash}")
            if output:
                print(output.decode("utf-8"))
            if error:
                print(error)
            add_file_original = output.decode("utf-8")
            add_file_split = add_file_original.split("\n")
            add_file_split = [line for line in add_file_split if line.strip()]  # 빈 줄 제거

            add_file_list = "\n".join(add_file_split)
            #print(add_file_list)
            #변경된 파일이 여러개가 나올 수 있으니까 반복문
            dir_lines = add_file_list.split("\n")
            for dir_line in dir_lines:
                #print("xxxxxxxxxxxxxxxxxxxxxxx")
                if dir_line.lower() in output_content.lower():  
                # output_content 에 해당 파일이 있으면 그 커밋이 오류
                    #print("vvvvvvvvvvvvvvv")
                    output_content_cut = output_content[0:1000]
                    content = f"""□  운영 배포브랜치 빌드  □\n접수번호 : {commit_msg}\n작성자 : {commit_user}\n처리내용 : 운영 IIMS 빌드에 실패했습니다. \n {output_content_cut}"""
                    webhook_send(content)
                    print(content)
                    current_time("운영 IIMS 빌드 작업종료 : ")
                    return
                    # print("에러")
                    # # 오류인 커밋은 rebase interactive 옵션으로 해당 커밋을 삭제하고 다시 빌드를 시작
                    # output, error = run_git_command_prod(f"git rebase -i {commit_hash}^")
                    # if output:
                    #     print(output.decode("utf-8"))
                    # if error:
                    #     print(error)
                    # # 편집기로부터 변경된 커밋 목록 읽기
                    # with open('.git/rebase-merge/git-rebase-todo', 'r') as file:
                    #     rebase_lines = file.readlines()

                    # # 삭제할 커밋을 찾아서 해당 줄을 주석 처리
                    # for i in range(len(rebase_lines)):
                    #     if rebase_lines[i].startswith('pick') and commit_hash in rebase_lines[i]:
                    #         rebase_lines[i] = '#' + rebase_lines[i]
                    #         break

                    # # 변경된 커밋 목록을 파일에 쓰기
                    # with open('.git/rebase-merge/git-rebase-todo', 'w') as file:
                    #     file.writelines(rebase_lines)

                    # # 리베이스 계속 진행
                    # output, error = run_git_command_prod(f"git rebase --continue")
                    # if output:
                    #     print(output.decode("utf-8"))
                    # if error:
                    #     print(error)
                        
                    # build(get_commit_hash)
                    # # 빌드 성공하면 나머지는 성공 메시지 출력
        
    else:        
        commit_hash_list = ""
        output, error = run_git_command_prod(f"git log --pretty=format:%h,%s,%an {get_commit_hash}..")
        if output:
            print(output.decode("utf-8"))
            commit_hash_list = output.decode("utf-8")
        if error:
            print(error)
        lines = commit_hash_list.split("\n")
        for line in lines:
            jubsu_no = ""
            login_user = ""
            
            insert_data = line.split(",")
            #insert_commit_hash = insert_data[0]
            jubsu_no = insert_data[1]
            login_user = insert_data[2]
            
            content = f"□  운영 배포브랜치 빌드  □\n접수번호 : {jubsu_no}\n작성자 : {login_user}\n처리내용 : 운영 배포브랜치 빌드 성공했습니다. \n             최종배포는 배포일에 진행 됩니다."
            webhook_send(content)
            print(content)
    
current_time("운영 IIMS 빌드 작업시작 : ")  
cx_Oracle.init_oracle_client(lib_dir=r"D:\instantclient_21_9")          
#host = '16.16.16.120'
host = '10.20.20.201'
port = 1521
#sid = 'OLB19DB'
sid = 'PDB_ONE.INCAR.CO.KR'
user_name = 'NEWINCAR'
passwd = 'NEWSTART'

conn = cx_Oracle.connect(f'{user_name}/{passwd}@{host}:{port}/{sid}')

# 실행 중인지 여부를 확인하기 위한 파일 경로
lock_file = "release_build_lock.txt"

def is_running():
    # 실행 중인지 여부를 파일의 존재 여부로 판단합니다.
    return os.path.exists(lock_file)

def run_task():
    # 실행 중인지 확인합니다.
    if is_running():
        print("Task is already running. Skipping additional execution.")
        return
    
    # 실행 중인 표시를 위해 파일을 생성합니다.
    with open(lock_file, "w"):
        pass

    try:
        #배포브랜치로 체크아웃
        output, error = run_git_command_prod("git checkout release")
        if output:
            print(output.decode("utf-8"))
        if error:
            print(error)
        #pull 하기전 release의 최신 커밋 해시값
        get_commit_hash = ""
        output, error = run_git_command_prod("git log --pretty=format:%h -n 1")
        if output:
            print(output.decode("utf-8"))
            get_commit_hash = output.decode("utf-8")
        if error:
            print(error)
        #배포브랜치 pull
        output, error = run_git_command_prod("git pull origin release")
        if output:
            print(output.decode("utf-8"))
        if error:
            print(error)
        #최신 커밋 해시값 이후로 추가 커밋이 있는지 체크
        #get_commit_hash ="72de040"
        insert_commit_info = ""
        output, error = run_git_command_prod(f"git log --pretty=format:%h,%s,%an {get_commit_hash}..")
        if output:
            print(output.decode("utf-8"))
            insert_commit_info = output.decode("utf-8")
        if error:
            print(error)    
        #insert_commit_info = "6406f33,20230803008,INCAR"
        #커밋 메시지 유효성 검사
        if insert_commit_info!="":
            err_chk = True
            # lines = insert_commit_info.split("\n")
            # for line in lines:
            #     insert_data = line.split(",")
            #     print(insert_data[0])
            #     insert_commit_hash = insert_data[0]
            #     insert_commit_msg = insert_data[1]
            #     insert_commit_user = insert_data[2]
            #     if not insert_commit_msg.isdigit() or len(insert_commit_msg)!=11:
            #         err_chk = False
            #         content = f"""□  운영 배포브랜치 빌드  □\n접수번호 : {insert_commit_msg}\n작성자 : {insert_commit_user}\n처리내용 : 병합제목은 접수번호만 가능합니다. \n             다시 요청 하시기 바랍니다."""
            #         webhook_send(content)
            #     else:
            #         qry = f"""
            #                 select  count(*) cnt
            #                 from    git_inforequest_link a         
            #                         , info_request b
            #                 where   a.gubun ='1'
            #                 and     b.status_cd ='10'
            #                 and     a.info_request_pk = b.pk
            #                 and     b.jubsu_no = :jubsu_no
            #                 """
            #         bind_arr={"jubsu_no":insert_commit_msg}
            #         cursor = conn.cursor()
            #         cursor.execute(qry,bind_arr)
            #         line = cursor.fetchone()
            #         if line is not None:
            #             if line==0 :
            #                 err_chk = False
            #                 content = f"""□  운영 배포브랜치 빌드  □\n접수번호 : {insert_commit_msg}\n작성자 : {insert_commit_msg}\n처리내용 : 이행승인된 접수번호가 아닙니다. \n             다시 요청 하시기 바랍니다."""
            #                 webhook_send(content)
                
            if err_chk==True:
                #get_commit_hash = "ab351f2"
                build(get_commit_hash)
        
        else:
            content = f"""□  운영 배포브랜치 빌드  □\n처리내용 : 빌드 할 커밋이 없습니다."""
            #webhook_send(content)
            print(content)
            
                
    finally:
        # 실행 중인 표시를 위해 생성한 파일을 삭제합니다.
        os.remove(lock_file)
# 스케줄에 따라 작업을 실행합니다.
run_task()
conn.close()    
current_time("운영 IIMS 빌드 작업종료 : ")
