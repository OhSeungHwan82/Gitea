import cx_Oracle
import subprocess
import shutil
import os
import requests
import xml.etree.ElementTree as ET
import datetime

def current_time(msg):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(msg, formatted_time)


def run_git_command_prod(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\deploy\release_build\src")
    output, error = process.communicate()
    return output, error

def run_git_command_deploy(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r"D:\git\iims\src")
    output, error = process.communicate()
    return output, error

current_time("운영브랜치 병합 시작 : ")  
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

#운영브랜치로 체크아웃
output, error = run_git_command_prod("git checkout main")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)
#운영브랜치 pull
output, error = run_git_command_prod("git pull")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)
#운영브랜치의 최신 커밋 해시값 출력
output, error = run_git_command_prod("git log --pretty=format:%h -n 1")
if output:
    #print("get_commit_hash : ",output.decode("utf-8"))
    get_commit_hash = output.decode("utf-8")
if error:
    print(error)

output, error = run_git_command_prod("git checkout release")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)
output, error = run_git_command_prod("git pull")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)
output, error = run_git_command_prod("git rebase main")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)        
output, error = run_git_command_prod("git checkout main")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)    
output, error = run_git_command_prod("git merge release")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)
output, error = run_git_command_prod("git push origin main")
if output:
    print(output.decode("utf-8"))
if error:
    print(error)
#병합하고 get_commit_hash 이후로 발생한 커밋들의 해시값과 커밋메시지 획득
#get_commit_hash = "265ba5c"
insert_commit_msg =""
insert_commit_hash =""
insert_commit_hash_msg = ""
output, error = run_git_command_prod(f"git log --pretty=format:%h,%s {get_commit_hash}..")
if output:
    #print("insert_commit_hash_msg : ",output.decode("utf-8"))
    insert_commit_hash_msg = output.decode("utf-8")
if error:
    print(error)
    
if insert_commit_hash_msg!="":    
    #해쉬값은 여러개가 나올 수 있으니까 반복문
    lines = insert_commit_hash_msg.split("\n")
    conn = cx_Oracle.connect(f'{user_name}/{passwd}@{host}:{port}/{sid}')
    for line in lines:
        insert_data = line.split(",")
        #print("insert_commit_hash : ",insert_data[0])
        #print("insert_commit_msg : ",insert_data[1])
        insert_commit_hash = insert_data[0]
        insert_commit_msg = insert_data[1]

        
        #insert_commit_hash 커밋 해시값 , insert_commit_msg 커밋 메시지 = 접수번호
        qry = f"""
                    select pk from info_request where jubsu_no =:jubsu_no
                """
        bind_arr={"jubsu_no":insert_commit_msg}
        print(qry)
        print(bind_arr)
        cursor = conn.cursor()
        cursor.execute(qry, bind_arr)
        info_request_pk = ""
        results = cursor.fetchall()
        for row in results:
            info_request_pk = row[0]
            #print("info_request_pk",info_request_pk)
        qry = f"""
                    insert into git_inforequest_link 
                    (info_request_pk, hash_code, gubun, create_date, upmu_gubun)
                    values
                    (:info_request_pk, :hash_code, '2', sysdate, '1')
                """
        
        bind_arr={"info_request_pk":info_request_pk, "hash_code":insert_commit_hash}
        print(qry)
        print(bind_arr)
        cursor = conn.cursor()
        cursor.execute(qry, bind_arr)
        conn.commit()
        
        qry = """
                select  ip
                from    sawon
                where   sawon_cd =1611006
            """
        cursor = conn.cursor()
        cursor.execute(qry)
        pw = ""
        results = cursor.fetchall()
        for row in results:
            pw = row[0]
        
        dataInfo = {'registCd':'1611006','registPw':pw,'pk':info_request_pk,'gubun':'8'}
        URL = 'http://air.incar.co.kr/Etc/InfoRequest/SaveConfirm'
        response = requests.post(URL, data=dataInfo)
        print(response.text)
        if response.status_code == 200:  # 정상 응답 확인
            xml_data = response.text
            root = ET.fromstring(xml_data)  # XML 파싱
            print("root : ",root)
            for status in root.findall('status'):
                value = status.find('ercode').text
                print("value",value)
            # 이제 XML 요소에 접근하여 필요한 작업 수행 가능
            # 예를 들어, 특정 요소의 값을 가져오는 방법은 아래와 같습니다:
            #value = root.find('sawon_cd').text
            #print(value)
        else:
            print("Error:", response.status_code)
    conn.close() 
    output, error = run_git_command_deploy(f"git pull")
    if output:
        print(output.decode("utf-8"))
    if error:
        print(error)
current_time("운영브랜치 병합 종료 : ")  
    

    
