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
- Use the command wsl -- list --verbose to check for distributions already installed.
- If necessary, use command wsl --list --online to check available distributions to install.
- Use command wsl --install --distribution <distro> to install new distribution.
- Use command wsl --unregister <distro> to uninstall old distro.

## Python Setup
- Intall python. Go to the python website and install. Select the options to install as administrator and to add python.exe to the PATH variable.
- Check that python is accessible from linux using the "python" or "python3" command, otherwise go to the windows environment variable settings and add it.

## VScode Setup
- Installing VS Code.
- Install VS Code from the microsoft store.
- Activate VS Code in WSL using the "code" command.
- Install python extensions and WSL.
- Change vs code to the WSL environment in the bottom left corner of the screen.
- Use SSH connection to connect WSL on github.
- Go to github > settings > SSH and GPH keys.
- Click on New SSH Key.
- On linux use the command "ssh-keygen -t ed25519 -C "seuemail@email.com"
- Press enter 3 times.
- Use the command "eval "$(ssh-agent -s)"" to activate.
- Use the command "ssh-add ~/. ssh/id_ed25519" to create the key.
- If this command doesn't work, use the command "nano ~/.
