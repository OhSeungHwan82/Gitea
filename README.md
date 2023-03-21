# Gitea 환경설정

## 1. mariaDB 설치
  repo 설정
    vi /etc/yum.repos.d/MariaDB.repo

    [mariadb]
    ame = MariaDB
    baseurl = http://yum.mariadb.org/10.4/centos7-amd64
    gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
    gpgcheck=1

  설치
    yum install MariaDB
  확인
    rpm -qa | grep MariaDB
  DB시작 / 패스워드 변경
    systemctl start mariadb
    /usr/bin/mysqladmin -u root password 'P@ssw0rd'
    netstat -anp | grep 3306
  접속확인
    mysql -u root -p

  DB생성
    create database gitea;
    create user 'gitea'@'localhost' identified by '~~~~~';
    grant all on gitea.* TO 'gitea'@'localhost' identified by '~~~~~' with grant option;
    flush privileges;
    exit;

## 2. GITEA 설치
  gitea 사용자
    sudo adduser --system --shell /bin/bash --comment 'Git Version Control' --user-group --home-dir /home/git -m git
  디렉토리 구조
    sudo mkdir -p /var/lib/gitea/{custom,data,indexers,public,log}
    
    sudo chown git:git /var/lib/gitea/{data,indexers,log}
    
    sudo chmod 750 /var/lib/gitea/{data,indexers,log}
    
    sudo mkdir /etc/gitea
    
    sudo chown root:git /etc/gitea

    sudo chmod 770 /etc/gitea
  GITEA 설치
    sudo wget -O https://dl.gitea.com/gitea/1.19/gitea-1.19-linux-amd64

  GITEA 서비스 작성
    sudo chmod +x gitea
    sudo touch /etc/systemd/system/gitea.service

    [Unit]

    Description=Gitea (Git with a cup of tea)

    After=network.target

    After=mariadb.service



    [Service]

    RestartSec=2s

    Type=simple

    User=git

    Group=git

    WorkingDirectory=/var/lib/gitea/

    ExecStart=/usr/local/bin/gitea web -c /etc/gitea/app.ini

    Restart=always

    Environment=USER=git HOME=/home/git GITEA_WORK_DIR=/var/lib/gitea

    [Install]

    WantedBy=multi-user.target

    sudo systemctl daemon-reload
    sudo systemctl enable gitea
    sudo systemctl start gitea
    sudo systemctl status gitea
