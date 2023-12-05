import cx_Oracle
import subprocess
import shutil
import os
import schedule
import time
import datetime

def current_time(msg):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(msg, formatted_time)

def run_git_command_test(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\git\iimstest\src")
    output, error = process.communicate()
    return output, error
    # try:
    #     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\Test-IIMS-PLUS")
    #     output, error = process.communicate()
    #     return output.decode(), error.decode()
    # except Exception as e:
    #     return None, str(e) 
current_time("GIT저장소와 DATABASE연동처리 시작 : ")
cx_Oracle.init_oracle_client(lib_dir=r"D:\instantclient_21_9")

#host = '16.16.16.120'
host = '10.20.20.201'
port = 1521
#sid = 'OLB19DB'
sid = 'PDB_ONE.INCAR.CO.KR'
user_name = ''
passwd = ''

get_commit_hash = ""
get_commit_msg = ""

#테스트 저장소에서 PR을 merge 한 다음 배포배치.bat 하기전에 수행 
output1, error1 = run_git_command_test("git checkout main")
if output1:
    print(output1.decode("utf-8"))
if error1:
    print(error1)
#pull 하기전 Test-IIMS-PLUS 저장소의 최신 커밋 해시값
output2, error2 = run_git_command_test("git log --pretty=format:%h -n 1")
if output2:
    print(output2.decode("utf-8"))
    get_commit_hash = output2.decode("utf-8")
if error2:
    print(error2)

output3, error3 = run_git_command_test("git pull")
if output3:
    print(output3.decode("utf-8"))
if error3:
    print(error3)
#git pull 하고나서 get_commit_hash 이후로 발생한 커밋들의 해시값과 커밋메시지 획득
insert_commit_msg =""
insert_commit_hash =""
insert_commit_hash_msg = ""
output4, error4 = run_git_command_test(f"git log --pretty=format:%ad,%h,%s {get_commit_hash}.. | sort")
#output4, error4 = run_git_command_test(f"git log --reverse --pretty=format:%ad,%h,%s {get_commit_hash}..")
if output4:
    print(output4.decode("utf-8"))
    insert_commit_hash_msg = output4.decode("utf-8")
if error4:
    print(error4)
#해쉬값은 여러개가 나올 수 있으니까 반복문
if insert_commit_hash_msg!="":
    lines = insert_commit_hash_msg.split("\n")
    conn = cx_Oracle.connect(f'{user_name}/{passwd}@{host}:{port}/{sid}')
    #i=0
    print("len_lines::", len(lines))
    for line in lines:
        #i= i+1
        #print("i::",i)
        insert_data = line.split(",")
        if len(insert_data) >= 2:
            print(insert_data[0])
            insert_commit_hash = insert_data[1]
            insert_commit_msg = insert_data[2]
            qry = f"""
                        select pk from info_request where jubsu_no ={insert_commit_msg}
                    """
            bind_arr={"jubsu_no":insert_commit_msg}
            print(qry)
            cursor = conn.cursor()
            cursor.execute(qry)
            info_request_pk = ""
            results = cursor.fetchall()
            for row in results:
                column1_value = row[0]
                info_request_pk = column1_value
            qry = f"""
                        insert into git_inforequest_link 
                        (info_request_pk, hash_code, gubun, create_date, upmu_gubun)
                        values
                        (:info_request_pk, :hash_code, '1', sysdate,'1')
                    """
            bind_arr={"info_request_pk":info_request_pk, "hash_code":insert_commit_hash}
            print(qry)
            print(bind_arr)
            cursor = conn.cursor()
            cursor.execute(qry, bind_arr)
            conn.commit()

    conn.close()      

current_time("GIT저장소와 DATABASE연동처리 종료 : ")    
