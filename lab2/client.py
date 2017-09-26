'''
Client side for Office Forest API
'''
import requests

host = 'http://127.0.0.1'
port = 5000
username = 'guest'
password = ''
admin_password = ''

print """
Welcome to Office Forest!

    host={host}:{port}
    logged in as {username}

    home            -   access home page
    plants          -   view list of available plants
    plant <name>    -   view the plant with that particular name
    check           -   view your own plant's status
    upgrade <upg>   -   upgrade your plant with a specific upgrade

    ADMIN
    create          -   create a plant (requires admin password)
    delete <name>   -   delete a plant (requires admin password)

    config          -   set configuration of host & port
""".format(host=host, port=port, username=username)

while True:
    command = raw_input("Office Forest>>")
    if command == 'help':
        print """Welcome to Office Forest!

    host={host}:{port}
    logged in as:{username}

    home            -   access home page
    plants          -   view list of available plants
    plant <name>    -   view the plant with that particular name
    check           -   view your own plant's status
    upgrade <upg>   -   upgrade your plant with a specific upgrade

    ADMIN
    create          -   create a plant (requires admin password)
    delete <name>   -   delete a plant (requires admin password)

    config          -   set configuration of host & port
    login           -   enter username and password
    """
    elif command == 'config':
        host = raw_input('host[{}]: '.format(host)) or host
        port = raw_input('port[{}]: '.format(port)) or port
    elif command == 'login':
        username = raw_input('username[{}]: '.format(username)) or username
        password = raw_input('password: ') or password
    elif command == 'home':
        url = '{host}:{port}'.format(host=host, port=port)
        print('requesting {}'.format(url))
        r = requests.get(url)
        print r.text
    elif command == 'plants':
        url = '{host}:{port}/plants'.format(host=host, port=port)
        print('requesting {}'.format(url))
        r = requests.get(url)
        print r.text
    elif 'plant' in command:
        args = command.split()
        name = args[1]
        url = '{host}:{port}/plants/{name}'\
              .format(host=host, port=port, name=name)
        print('requesting {}'.format(url))
        r = requests.get(url)
        plant = r.json()
        print("""
        Office Plant

            Name:{name}
            Type:{type}

            Votes:{vote}
            Obtained upgrade:{upgrades}
            """).format(name=plant['name'],
                        type=plant['type'],
                        vote=plant['votes'],
                        upgrades=','.join(plant['upgrades']))
    elif command == 'check':
        if username <= '' or username == 'guest':
            username = raw_input('username[{}]: '.format(username)) or username
            password = raw_input('password: ') or password
        url = '{host}:{port}/myplant'\
              .format(host=host, port=port)
        print('requesting {}'.format(url))
        payload = {'operation':'VIEW'}
        r = requests.post(url, auth=(username, password), json=payload,
                          headers={'content-type':'application/json'})
        try:
            plant = r.json()
            print(plant)
        except:
            print(r.text)

    elif command == 'quit' or '\q':
        break