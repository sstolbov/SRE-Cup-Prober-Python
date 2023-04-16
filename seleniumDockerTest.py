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
import names

print("Wait for selenium container")


client = docker.from_env()
network_name = names.get_first_name()
client.networks.create(network_name, driver="bridge")
networking_config = client.api.create_networking_config({
    network_name: client.api.create_endpoint_config(
            aliases=['selenium'],
    links={'selenium': 'selenium', 'another': None})
})
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
command_1 = "pip install -r requirements.txt"
_, stream = box.exec_run(cmd = command_1, workdir='/scripts', stream=True)
for data in stream:
    print(data.decode())
time.sleep(1)
print("Test running")
command_2 = "python ./runTests.py"
_, stream = box.exec_run(cmd = command_2, workdir='/scripts', stream=True)
for data in stream:
    print(data.decode())

print("Test done")

box.stop()
box.remove()
time.sleep(1)
container.stop()
container.remove()
time.sleep(1)
#container_py.stop()
#container_py.remove()
client.networks.prune(network_name)
print("Test Execution Successfully Completed!")