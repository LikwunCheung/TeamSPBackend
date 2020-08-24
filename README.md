# unimelb-SWEN90013Backend

    Backend Team:
    | Name | Email |
    | ---- | ---- |
    | Lihuan Zhang (Lead) | lihuanz@student.unimelb.edu.au |
    | Yue Yang Ho, Zachary | yho4@student.unimelb.edu.au |
    | Xinbo Sun | xinbos@student.unimelb.edu.au |
    | Zhaochen Fan | zhaochenf@student.unimelb.edu.au |
    | Jinxin Hu, Richard | jinxinh@student.unimelb.edu.au |

## Running the backend locally

### Using Docker

1. Ensure Docker and pip3 are installed on your machine.
2. Clone the repository on your machine.
3. Navigate to the project root (where Dockerfile is located).
4. Run `docker build -t sp90013/backend:latest` on your command line.

### Using pip3

1. Ensure pip3 is installed on your machine.
2. Clone the repository on your machine.
3. Navigate to the project root (where Dockerfile is located).
4. Run `pip3 install -r requirements.txt` on your command line.
5. Run `python3 manage.py runserver --settings=TeamSPBackend.settings.dev 0:8080`\
   on your command line.

### Using a virtual environment (**pipenv** in this example)

1. Ensure pipenv is installed on your machine.
2. Clone the repository on your machine.
3. Navigate to the project root (where Dockerfile is located).
4. Run `pipenv install -r requirements.txt` on your command line.
5. Run `pipenv shell` to launch your virtual environment.
6. Run `python3 manage.py runserver --settings=TeamSPBackend.settings.dev 0:8080`\
   on your command line.

- To access the database deployed on Unimelb's virtual machine, connect to\
   Unimelb's VPN via CISCO.
