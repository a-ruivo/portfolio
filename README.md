<h1 align="center"> Portfolio - Allan Ruivo </h1>

My name is Allan Ruivo Wildner, this repository is used to store the projects in my portfolio as an analytics engineer.

<h1 align="center"> Project 1 </h1>
# :hammer: Steps  <br>
- 1: Setting up the python, vscode and git environment.  <br>
- 2: Create architecture using airflow, docker and terraform.<br>  
- 3: Connect to the IBGE API and extract data and save it in a postgres database.<br>  
- 4: Create a dashboard using streamlit and an agent AI flow that performs analysis. <br> 
<br>
<h2 align="center"> 1. Setting up </h2>

## GitHub Setup
- Create a GitHub account.
- Create a repository for the project.

## Install Necessary Tools
- Install **GitHub Desktop**.
- Install **Git** for version control.

## Set Up WSL
- Enable WSL using:
  ```bash
  wsl --install
- Selecting WSL distribution
- To check for distributions already installed use the command:
  ```bash
  wsl -- list --verbose
- To check available distributions to install if necessary, use command:
  ```bash
  wsl --list --online
- To install new distribution use the command:
  ```bash
  wsl --install --distribution <distro>
- To uninstall old distro use the command:
  ```bash
  wsl --unregister <distro>

## Python Setup
- Intall python. Go to the python website and install. Select the options to install as administrator and to add python.exe to the PATH variable.
- Check that python is accessible from linux using the "python" or "python3" command, otherwise go to the windows environment variable settings and add it.

## VScode Setup
- Installing VS Code.
- Install VS Code from the microsoft store.
- Activate VS Code in WSL using the command:
  ```bash
  code
- Install python extensions and WSL.
- Change vs code to the WSL environment in the bottom left corner of the screen.
- Use SSH connection to connect WSL on github.
- Go to github > settings > SSH and GPH keys.
- Click on New SSH Key.
- On linux use the command:
  ```bash
  ssh-keygen -t ed25519 -C "seuemail@email.com"
- Press enter 3 times.
- To activate use the command:
  ```bash
  eval "$(ssh-agent -s)"
- To create the key use the command:
  ```bash
  ssh-add ~/. ssh/id_ed25519
- If this command doesn't work, use the command:
  ```bash
  nano ~/.
