# /usr/bin/env python3
import paho.mqtt.client as mqtt
import tuyapower
import time
import json
import os
import yaml


def get_env(name, default=None):
    if name in os.environ:
        return os.environ[name]
    elif default != None:
        return default
    raise KeyError('Enviroment variable %s does not exists' % name)


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        raise Exception('Connection error: %i' % rc)
    print('Connected to the MQTT broker')


def scan_devices(config):
    for name, d in config['devices'].items():
        (on, w, mA, V, err) = tuyapower.deviceInfo(
            d['id'], d['ip'], d['key'], d['ver'])
        if err == 'OK':
            yield (name, on, w, mA, V)


def main(config_path):
    config = yaml.safe_load(open(config_path, 'r'))

    client = mqtt.Client()
    client.on_connect = on_connect

    if config['mqtt']['useTls']:
        cert = config['mqtt']['ca']
        print('Using TSL with ca: %s' % cert)
        client.tls_set(ca_certs=cert)

    client.username_pw_set(config['mqtt']['user'], config['mqtt']['passwd'])
    client.loop_start()
    client.connect(config['mqtt']['host'], config['mqtt']['port'], 20)

    interval = config['interval']
    print('Start polling with %s seconds interval' % interval)
    while True:
        time.sleep(interval)
        for (name, status, w, mA, v) in scan_devices(config):
            payload = {
                'name': name,
                'status': 1 if status else 0,
                'w': w,
                'mA': mA,
                'v': v
            }
            client.publish('%s%s' %
                           (config['mqtt']['prefix'], name), json.dumps(payload))


if __name__ == '__main__':
    main(get_env('TUYA_CONFIG', 'config.yml'))
