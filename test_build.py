import subprocess
import requests
import os
import time
import chardet
import datetime

def current_time(msg):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(msg, formatted_time)
    
def webhook_send(content):
    dataInfo = {'content':content}
    URL = 'https://teamroom.nate.com/api/webhook/f3af6d62/l4y0v5TG4fSZWdf94A0drnDb'
    URL = 'https://teamroom.nate.com/api/webhook/20a53730/MaHSX4CwEq86fS5bCuqsb2Up'
    response = requests.post(URL, data=dataInfo)

def run_git_command_test(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\deploy\test_build\src")
    output, error = process.communicate()
    return output, error

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
    output_file = "test_build_output.txt"

    # 배치 파일 실행
    subprocess.run("test_build.bat", stdout=open(output_file, "w"), stderr=subprocess.STDOUT, shell=True)

    # 파일 내용 읽기
    encoding_str = "ANSI"
    result = detect_encoding(output_file)
    if result['encoding'] =="utf-8":
        encoding_str = "utf-8"

    with open(output_file, "r",encoding=encoding_str) as file:
        output_content = file.read()

    # 실행 결과 출력
    print(output_content)
    os.remove(output_file)
    # 에러 여부 체크
    if "warning" in output_content.lower() or "error" in output_content.lower():
        #어느 커밋에서 오류인지 알 수 없어 커밋별 변경파일을 가져옴
        output, error = run_git_command_test(f"git log --pretty=format:%h,%s,%an {get_commit_hash}..")
        if output:
            print(output.decode("utf-8"))
            commit_hash_list = output.decode("utf-8")
        if error:
            print(error)
        lines = commit_hash_list.split("\n")
        err_chk2 = False #커밋목록에서 오류가 없을 경우 이전 커밋이 오류
        for line in lines:
            err_chk = False #커밋목록에서 오류 체크
            commit_hash = ""
            
            insert_data = line.split(",")
            commit_hash = insert_data[0]
            commit_jubsu_no = insert_data[1]
            commit_user = insert_data[2]
            output, error = run_git_command_test(f"git diff-tree --no-commit-id --name-only -r {commit_hash}")
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
                dir_line = dir_line.replace("/", "\\")
                #print(dir_line.lower())
                if dir_line.lower() in output_content.lower():  
                # output_content 에 해당 파일이 있으면 그 커밋이 오류
                    err_chk = True
                    err_chk2 = True
                    continue
                    # print("에러")
                    # # 오류인 커밋은 rebase interactive 옵션으로 해당 커밋을 삭제하고 다시 빌드를 시작
                    # output, error = run_git_command_test(f"git rebase -i {commit_hash}^")
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
                    # output, error = run_git_command_test(f"git rebase --continue")
                    # if output:
                    #     print(output.decode("utf-8"))
                    # if error:
                    #     print(error)
                    
                    # #오류 커밋을 정리 했고 다시 빌드 하기위해 반복문 종료
                    # break
            if err_chk  == True:
                #오류인 커밋으로 메시지 전송
                output_content_cut = output_content[0:1000]
                content = f"□  PR 빌드  □\n접수번호 : {commit_jubsu_no}\n작성자 : {commit_user}\n처리내용 : 테스트 IIMS 빌드에 실패했습니다. \n {output_content_cut}"
                webhook_send(content)
                print(content)
                current_time("테스트 IIMS 빌드 작업종료 : ")
                
                #build(get_commit_hash)
                # 빌드 성공하면 나머지는 성공 메시지 출력
        if err_chk2  == False:
            #커밋목록중에 오류가 없음
            content = f"□  PR 빌드  □\n처리내용 : 이전 커밋에 오류가 있습니다.\n테스트 IIMS 빌드에 실패했습니다. \n {output_content}"
            webhook_send(content)
            print(content)
            current_time("테스트 IIMS 빌드 작업종료 : ")
        
    else:        
        #print(get_commit_hash)
        commit_hash_list = ""
        output, error = run_git_command_test(f"git log --pretty=format:%h,%s,%an {get_commit_hash}..")
        if output:
            print(output.decode("utf-8"))
            commit_hash_list = output.decode("utf-8")
        if error:
            print(error)
        #print('commit_hash_list',commit_hash_list)
        if commit_hash_list!="":
            lines = commit_hash_list.split("\n")
            for line in lines:
                jubsu_no = ""
                login_user = ""
                
                insert_data = line.split(",")
                #insert_commit_hash = insert_data[0]
                jubsu_no = insert_data[1]
                login_user = insert_data[2]
                
                content = f"□  PR 빌드  □\n접수번호 : {jubsu_no}\n작성자 : {login_user}\n처리내용 : 테스트 IIMS 빌드 성공했습니다. \n             최종배포는 17:30 이후에 진행 됩니다."
                webhook_send(content)
                print(content)
                current_time("테스트 IIMS 빌드 작업종료 : ")
                #print("성공")
        else:
            content = f"□  PR 빌드  □\n접수번호 : {jubsu_no}\n작성자 : {login_user}\n처리내용 : 테스트 IIMS 빌드 성공했습니다. \n             최종배포는 17:30 이후에 진행 됩니다."
            webhook_send(content)
            print(content)
            current_time("테스트 IIMS 빌드 작업종료 : ")
            #print("성공")
            
        

# 실행 중인지 여부를 확인하기 위한 파일 경로
lock_file = "test_build_lock.txt"

def is_running():
    # 실행 중인지 여부를 파일의 존재 여부로 판단합니다.
    return os.path.exists(lock_file)

def run_task():
    current_time("테스트 IIMS 빌드 작업시작 : ")
    # 실행 중인지 확인합니다.
    if is_running():
        print("Task is already running. Skipping additional execution.")
        return
    
    # 실행 중인 표시를 위해 파일을 생성합니다.
    with open(lock_file, "w"):
        pass

    try:
        
        output1, error1 = run_git_command_test("git checkout main")
        if output1:
            print(output1.decode("utf-8"))
        if error1:
            print(error1)
            
        #pull 하기전 Test-IIMS-PLUS 저장소의 최신 커밋 해시값
        get_commit_hash = ""
        
        output2, error2 = run_git_command_test("git log --pretty=format:%h -n 1")
        if output2:
            print(output2.decode("utf-8"))
            get_commit_hash = output2.decode("utf-8")
            #get_commit_hash = "31c0d25"
        if error2:
            print(error2)

        output3, error3 = run_git_command_test("git pull")
        if output3:
            print(output3.decode("utf-8"))
            pull_chk = output3.decode("utf-8")
            if "Already" in pull_chk:
                #content = f"□  PR 빌드  □\n처리내용 : 빌드 할 변경이 없습니다. \n"
                #webhook_send(content)
                #os.remove(lock_file)
                current_time("테스트 IIMS 빌드 작업종료 : ")
                return
        if error3:
            print(error3)
            
        # output4, error4 = run_git_command_test("git branch build")
        # if output4:
        #     print(output4.decode("utf-8"))
        # if error4:
        #     print(error4)
            
        # output5, error5 = run_git_command_test("git checkout build")
        # if output5:
        #     print(output5.decode("utf-8"))
        # if error5:
        #     print(error5)
            
        build(get_commit_hash)
        
        # output, error = run_git_command_test("git checkout main")
        # if output:
        #     print(output.decode("utf-8"))
        # if error:
        #     print(error)
        # output, error = run_git_command_test("git branch -D build")
        # if output:
        #     print(output.decode("utf-8"))
        # if error:
        #     print(error)

        # 작업이 종료될 때까지 기다립니다.
        time.sleep(10)

    finally:
        # 실행 중인 표시를 위해 생성한 파일을 삭제합니다.
        os.remove(lock_file)
# 스케줄에 따라 작업을 실행합니다.
run_task()
