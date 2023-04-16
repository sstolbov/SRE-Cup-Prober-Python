#
#input('Name')
#input('Password')

# Run docker container docker run -d -p o:4444 --shm-size=2g selenium/standalone-chrome
# docker-compose run https://github.com/SeleniumHQ/docker-selenium/blob/trunk/docker-compose-v3-video.yml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.service import Service
import time
from time import sleep
import docker
import os
import sys
import names

print("Wait for selenium container")
try:
    client = docker.from_env()
    network_name = names.get_first_name()
    client.networks.create(network_name, driver="bridge")
    networking_config = client.api.create_networking_config({
        network_name: client.api.create_endpoint_config(
                aliases=['selenium'],
        links={'selenium': 'selenium', 'another': None})
    })

    client.api.pull("selenium/standalone-chrome")
    client.api.pull("selenium/video:ffmpeg-4.3.1-20230404")
    client.api.pull("python:alpine3.17")

    container = client.api.create_container(
        image="selenium/standalone-chrome",
        healthcheck={'test': ['CMD', 'curl', '-v', 'localhost:4444/'], 'interval': 100000000},
        networking_config=networking_config
    )
    client.api.start(container=container.get('Id'))

    timeout = 5
    stop_time = 3
    elapsed_time = 0
    while container.get('status') != 'running' and elapsed_time < timeout:
        sleep(stop_time)
        elapsed_time += stop_time
        continue

    print("Video container starts")
    video = client.containers.run(image = "selenium/video:ffmpeg-4.3.1-20230404",
                                remove = True,
                                volumes={os.getcwd(): {'bind': '/videos/', 'mode': 'rw'}},
                                detach = True,
                                network=network_name,
                                tty = True)

    print("Test container starts")
    box = client.containers.run(image = "python:alpine3.17",
                                remove = True,
                                volumes={os.getcwd(): {'bind': '/scripts/', 'mode': 'rw'}},
                                working_dir='/scripts',
                                detach = True,
                                network=network_name,
                                tty = True,
                                command = "/bin/sh")
    # send a test command
    print("Install dependencies")
    command_1 = "pip3 install -r requirements.txt"
    _, stream = box.exec_run(cmd = command_1, workdir='/scripts', stream=True)
    for data in stream:
        print(data.decode())
    time.sleep(1)
    print("Test running")
    original_stdout = sys.stdout
    command_2 = "python3 ./runTests.py"
    _, stream = box.exec_run(cmd = command_2, workdir='/scripts', stream=True)
    for data in stream:
        with open("testlogs-{}.txt".format(network_name), 'w') as f:
            sys.stdout = f # Change the standard output to the file we created.
            print(data.decode())
            sys.stdout = original_stdout # Rese

    print("Test done")
    print("Test Execution Successfully Completed!")

finally:
    box.stop()
    video.stop()
    time.sleep(2)
    client.api.stop(container=container.get('Id'))
    client.api.remove_container(container=container.get('Id'))
    #container_py.remove()
    #client.networks.prune(network_name)
    print("Purge Successfully Completed!")