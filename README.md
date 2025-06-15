<h1 align="center"> Portfolio - Allan Ruivo </h1>
My name is Allan Ruivo Wildner, this repository is used to store the projects in my portfolio as an analytics engineer.

# Summary
- [Project 1](#project-1)
  - [1. Setting up the infrastructure](#1-setting-up-the-infrastructure)
    - [a. WSL Commands](#wsl-commands)
    - [b. Linux Commands](#linux-commands)
    - [c. Python Setup](#python-setup)
    - [d. VScode Setup](#vscode-setup)
    - [e. Git Setup](#git-setup)
    - [f. Git Commands](#git-commands)
    - [g. Virtual Env](#virtual-env)
  - [2. Creating architecture](#2-creating-architecture)
    - [a. Creating EC2](#creating-ec2)


# <h1 align="center"> Project 1 </h1>
<br>
- 1: Setting up the python, vscode and git environment  <br>
- 2: Create architecture using airflow, docker and terraform<br>  
- 3: Connect to the IBGE API and extract data and save it in a postgres database<br>  
- 4: Create a dashboard using streamlit and an agent AI flow that performs analysis <br> 
<br>

# <h2 align="center"> 1. Setting up the infrastructure</h2>

## WSL Commands
- Enable WSL
  ```bash
  wsl --install
- Check for distributions already installed 
  ```bash
  wsl -- list --verbose
- Check available distributions to install if necessary
  ```bash
  wsl --list --online
- Install new distribution
  ```bash
  wsl --install --distribution <distro>
- Uninstall old distro
  ```bash
  wsl --unregister <distro>
- Configure a distro as default
  ```bash
  wsl --set-dafault <distro>
- Updates
  ```bash
  wsl --update
- Status
  ```bash
  wsl --status
- Help
  wsl --help

## Linux Commands
- View directories
  ```bash
  ls
- View hidden directories
  ```bash
  ls -a
- Go to directorie
  ```bash
  cd <path>
- Move file
  ```bash
  mv <path1> <path2>
- Delete file
  ```bash
  rm <path>
- Delete directorie
  ```bash
  rm -rf <path>
- Create directorie
  ```bash
  mkdir <directorie>
- Permission override
  ```bash
  sudo

## Python Setup
- Go to the python website and install (select the options to install as administrator and to add python.exe to the PATH variable)
- Check that python is accessible from linux using the "python" or "python3" command, otherwise go to the windows environment variable settings and add it

## VScode Setup
- Install VS Code from the microsoft store
- Activate VS Code in WSL
  ```bash
  code
- Install python extensions and WSL
- Change vs code to the WSL environment in the bottom left corner of the screen

## Git Setup
- Install git
- Github credentials configuration
  ```bash
  git config --global user.name <nome>
  git config --global user.email <email>
- In the directorie you want to turn in a git repositore
  ```bash
  git init -b <nome da branch>
- Use SSH connection to connect WSL on github
- Go to github > settings > SSH and GPH keys
- Click on New SSH Key
- On linux use the command
  ```bash
  ssh-keygen -t ed25519 -C "seuemail@email.com"
- Press enter 3 times
- Activate the key
  ```bash
  eval "$(ssh-agent -s)"
- Create the key
  ```bash
  ssh-add ~/. ssh/id_ed25519
- If this command doesn't work, use this
  ```bash
  nano ~/.
- If you need to bring a repository that already exists to vscode
  ```bash
  git clone <repository url>

## Git Commands
- Verificar status dos commits
  ```bash
  git status
- Adicionar arquivos para o commit
  ```bash
  git add <file1> <file2> <fileN>
- Adicionar todos os arquivos para o commit
  ```bash
  git add -A
- Fazendo o commit
  ```bash
  git commit -m <message>
- Commit history on this branch
  ```bash
  git log
- Commit history on all branches
  ```bash
  git log -all
- Branch list
  ```bash
  git branch
- Create branch
  ```bash
  git branch <nova branch>
- Change branch
  ```bash
  git checkout <branch> 
- Change branch and create a new one
  ```bash
  git checkout -b <branch>
- Para fazer merge (necessário estar na branch destino e caso precise cancelar usar o mesmo comando com --abort)
  ```bash
  git merge <branch origem>
- Mudar de commit
  ```bash
  git checkou <hash commit>
- Enviando commits para repositorio remoto
  ```bash
  git push <repositorio remoto> <nome branch>
- Lista os repositorios remotos conectados
  ```bash
  git remote -V
- Conecta a um repositorio remoto
  ```bash
  git remote add origin <url>
- Deletar branch
  ```bash
  git push <nome branch remoto> -d <nome branch local>
- Baixar arquivos do repositorio remoto para as branch remotas
  ```bash
  git fetch
- Integra os arquivos da branch remota com a branch local
  ```bash
  git pull
- Reaplicar commits em outra branch
  ```bash
  git rebase <branch destino>
- Remover arquivos da stage do commit
  ```bash
  git restore --staged  <file1> <file2>

## Virtual Env
- In the repository create a python virtual environment
  ```bash
  python3 -m venv <enviroment>
- To activate the env use this command
  ```bash
  source <path>/bin/activate
- To deactivate use
  ```bash
  deactivate
- To install libraries in the env use or install directly from pip
  ```bash
  pip install -r <requirements path>
<br>

# <h2 align="center"> 2. Creating architecture </h2>

## Creating EC2
- Instale o AWS CLI fora do seu repositorio
  ```bash
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
- Na AWS configure um usuario IAM com acesso a sua conta
- No terminal use o comando
  ```bash
    aws configure sso
    SSO session name (Recommended): <nome da sessao>
    SSO start URL [None]: <link disponivel no IAM>
    SSO region [None]: <regiao AWS>
    SSO registration scopes [None]: sso:account:access
- Criar EC2 configurando chave ssh
- Ajustar regras de grupo de segurança
- Conecte na EC2 (cada AMI possui um nome de usuario padrão)
  ```bash
  ssh -i <key path> <user>@<link EC2>

# Intalling terraform
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum install -y terraform

terraform - version

# Installing docker
sudo yum update -y
sudo yum install -y docker

sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Installing airflow
sudo yum install -y python3-pip
pip3 install --upgrade pip
pip3 install apache-airflow

airflow db init

airflow scheduler &
airflow webserver -p 8080 &



- Create PostgreSQL instances and configure storage.
- Create a Dcoker environment to run the containers.
- Define networking between services.
## Task Orchestration (Airflow)
Create a DAG in Apache Airflow to automate the flow of data extraction and loading:
- Task 1: Extract data from the API using a Python operator (HttpSensor + SimpleHttpOperator).
- Task 2: Transform the data using DuckDB (for efficient columnar processing).
- Task 3: Insert the data into PostgreSQL.
- Task 4: Validate the inserted data and send notifications.
## Execution with Docker
Create a Docker Compose with:
- Container for Airflow (scheduler, webserver, worker).
- Container for PostgreSQL (database).
- Container for DuckDB (processing).
- Configure volumes and networks between containers to ensure communication.
# Automation and Deployment (GitHub Actions)
Create a workflow in GitHub Actions to:
- Validate code and run integration tests (pytest to check the API).
- Provision infrastructure via Terraform.
- Build and publish containers on Docker Hub.
- Deploy the pipeline for execution.