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

#디렉토리 경로
dir_path = 'D:/Prod-IIMS-PLUS'
# 권한 플래그 (예: 0o755)
permissions = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
# 권한 변경
os.chmod(dir_path, permissions)
dir_path2 = 'D:/deploy/release_build/src'
# 권한 플래그 (예: 0o755)
permissions2 = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
# 권한 변경
os.chmod(dir_path2, permissions2)

# cx_Oracle.init_oracle_client(lib_dir=r"D:\instantclient_21_9")
def run_git_command_test(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\Test-IIMS-PLUS")
    output, error = process.communicate()
    return output, error

def run_git_command_prod(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\deploy\release_build\src")
    output, error = process.communicate()
    return output, error

def webhook_send(content):
    dataInfo = {'content':content}
    #URL = 'https://teamroom.nate.com/api/webhook/f3af6d62/l4y0v5TG4fSZWdf94A0drnDb'
    URL = 'https://teamroom.nate.com/api/webhook/20a53730/MaHSX4CwEq86fS5bCuqsb2Up'
    response = requests.post(URL, data=dataInfo)

current_time("접수번호 브랜치 생성 시작 : ")      
# #host = '16.16.16.120'
# host = '10.20.20.201'
# port = 1521
# #sid = 'OLB19DB'
# sid = 'PDB_ONE.INCAR.CO.KR'
# user_name = ''
# passwd = ''

# conn = cx_Oracle.connect(f'{user_name}/{passwd}@{host}:{port}/{sid}')

# 실행 중인지 여부를 확인하기 위한 파일 경로
lock_file = "release_branch_create_lock.txt"

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

        #이행승인 단계에 있는 정보처리요청번호의 info_request_pk 가져오기 
        output, error = run_git_command_prod("git checkout release")
        if output:
            print(output.decode("utf-8"))
        if error:
            print(error)
        output, error = run_git_command_prod("git fetch --all")
        if output:
            print(output.decode("utf-8"))
        if error:
            print(error)
        output, error = run_git_command_prod("git merge origin/release")
        if output:
            print(output.decode("utf-8"))
        if error:
            print(error)
#         qry = """
# select  a.info_request_pk
#         , b.jubsu_no
# from    git_inforequest_link a    -- 작업스케줄러 - 테스트원격저장소와 정보처리요청게시판 연동      
#         , info_request b
# where   a.gubun ='1'
# and     b.status_cd ='10'--정보처리요청게시판 이행승인
# and     a.upmu_gubun ='1'
# and     a.info_request_pk = b.pk
# group by a.info_request_pk
#         , b.jubsu_no
#                 """
#         print(qry)
#         cursor = conn.cursor()
#         cursor.execute(qry)
#         rows = cursor.fetchall()
        api_url = "http://10.16.16.160/api/giteaApi/createBranch/1/1"

        # POST 요청 보내기
        response = requests.get(api_url)  
        print(response.status_code)
        print(response.text)
        #print(response.json())  
        json_data = response.json()
        data_list = json_data.get('list', [])
        for row in data_list:#for row in rows:
            #print(row)
            # info_request_pk = row[0]
            # jubsu_no = row[1]
            info_request_pk = row.get('INFO_REQUEST_PK')
            jubsu_no = row.get('JUBSU_NO')
            output, error = run_git_command_prod("git checkout release")
            if output:
                print("git checkout release:",output.decode("utf-8"))
            if error:
                print(error)
            #접수번호 원격 브랜치가 있는지 체크
            branck_chk = ""
            output, error = run_git_command_prod(f"git ls-remote --heads git@16.16.16.200:Incar-IT/Prod-IIMS-PLUS.git {jubsu_no}")
            if output:
                print("branck_chk:",output.decode("utf-8"))
                branck_chk = output.decode("utf-8")
            if error:
                print(error)
            if branck_chk!="":
                continue
            #접수번호 커밋이력이 있는지 체크
            his_chk = ""
            output, error = run_git_command_prod(f"git log --grep={jubsu_no}")
            if output:
                print("his_chk:",output.decode("utf-8"))
                his_chk = output.decode("utf-8")
            if error:
                print(error)
            if his_chk!="":
                continue
            output, error = run_git_command_prod(f"git branch -D {jubsu_no}")
            if output:
                print(f"git branch -D {jubsu_no}:",output.decode("utf-8"))
                #print(output.decode("utf-8"))
            if error:
                print(error)
            output, error = run_git_command_prod(f"git branch {jubsu_no}")
            if output:
                print(f"git branch {jubsu_no}:",output.decode("utf-8"))
                #print(output.decode("utf-8"))
            if error:
                print(error)
            output, error = run_git_command_prod(f"git checkout {jubsu_no}")
            if output:
                print(f"git checkout {jubsu_no}:",output.decode("utf-8"))
                #print(output.decode("utf-8"))
            if error:
                print(error)
            output, error = run_git_command_prod(f"git push origin {jubsu_no}")
            if output:
                print(f"git push origin {jubsu_no}:",output.decode("utf-8"))
                #print(output.decode("utf-8"))
            if error:
                print(error)
            # info_request_pk 로 hash 를 찾기
            # qry = f"""select hash_code from git_inforequest_link where info_request_pk = :info_request_pk and gubun='1' and upmu_gubun ='1'"""
            # bind_arr={"info_request_pk":info_request_pk}
            # print(qry)
            # print(bind_arr)
            # cursor = conn.cursor()
            # cursor.execute(qry,bind_arr)
            # lines = cursor.fetchall()
            api_url = f"""http://10.16.16.160/api/giteaApi/createBranch/2/{info_request_pk}"""

            # POST 요청 보내기
            response = requests.get(api_url)  
            print(response.status_code)
            print(response.text)
            #print(response.json())  
            json_data = response.json()
            data_list = json_data.get('list', [])
            for line in data_list:
                #print(line[0])
                # teat_hash_code = line[0]
                teat_hash_code = line.get('HASH_CODE')
                # 테스트해시값으로 변경된 파일가져오기
                output1, error1 = run_git_command_test(f"git fetch origin")
                if output1:
                    print(output1.decode("utf-8"))
                if error1:
                    print(error1)
                output1, error1 = run_git_command_test(f"git merge origin/main")
                if output1:
                    print(output1.decode("utf-8"))
                if error1:
                    print(error1)
                output1, error1 = run_git_command_test(f"git diff-tree --no-commit-id --name-status -r {teat_hash_code}")
                if output1:
                    print(output1.decode("utf-8"))
                if error1:
                    print(error1)
                #변경된 파일들 운영으로 복사
                add_file_original = output1.decode("utf-8")
                add_file_split = add_file_original.split("\n")
                add_file_split = [line for line in add_file_split if line.strip()]  # 빈 줄 제거

                add_file_list = "\n".join(add_file_split)
                #print(add_file_list)
                if add_file_list!="":
                    
                    #변경된 파일이 여러개가 나올 수 있으니까 반복문
                    dir_lines = add_file_list.split("\n")
                    
                    for dir_line in dir_lines:
                        status_file_gb = dir_line.split("\t")
                        #print(status_file_gb[0])
                        #print(status_file_gb[1])
                        file_status = status_file_gb[0]
                        dir_file = status_file_gb[1]
                        from_file = "D:/Test-IIMS-PLUS/"+dir_file
                        to_git_file = "D:/deploy/release_build/src/"+dir_file
                        
                        #변경된 파일중에 새로운 디렉토리가 있을 수 있으니까 디렉토리 생성
                        if "/" in  to_git_file:
                            directory_path1 = to_git_file.rsplit("/", 1)[0] + "/"
                            #print(directory_path)

                            to_dir1 = os.path.dirname(directory_path1)
                            os.makedirs(to_dir1, exist_ok=True)

                        if file_status=="D":
                            if os.path.exists(to_git_file):
                                print("삭제파일"+to_git_file)
                                os.remove(to_git_file)
                            else:
                                print("삭제파일없음"+to_git_file)
                        else:
                            print(to_git_file)
                            #변경된 파일들 복사
                            shutil.copy(from_file,to_git_file)
                            # if os.path.exists(to_git_file):
                            #     shutil.copy(from_file,to_git_file)
                            # else:
                            #     print("경로없음")
                    
            output, error = run_git_command_prod(f"git add .")
            if output:
                print(output.decode("utf-8"))
            if error:
                print(error)
            output, error = run_git_command_prod(f"git commit -m {jubsu_no}")
            if output:
                print(output.decode("utf-8"))
            if error:
                print(error)
            output, error = run_git_command_prod(f"git push --set-upstream origin {jubsu_no}")
            if output:
                print(output.decode("utf-8"))
            if error:
                print(error)
            output, error = run_git_command_prod(f"git checkout release")
            if output:
                print(output.decode("utf-8"))
            if error:
                print(error)
            output, error = run_git_command_prod(f"git branch -D {jubsu_no}")
            if output:
                print(output.decode("utf-8"))
            if error:
                print(error)
                    
            content = f"""□  운영 배포브랜치 병합  □\n접수번호 : {jubsu_no}\n처리내용 : 이행승인된 접수번호로 새로운 브랜치가 생성되었습니다. \n             배포브랜치로 병합 하시기 바랍니다."""
            webhook_send(content)
    finally:
        # 실행 중인 표시를 위해 생성한 파일을 삭제합니다.
        os.remove(lock_file)
# 스케줄에 따라 작업을 실행합니다.
run_task()
# conn.close()    
current_time("접수번호 브랜치 생성 종료 : ")   
