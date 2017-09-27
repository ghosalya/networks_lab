'''
Client side for Office Forest API
'''
import requests


class ClientConsole:
    def __init__( self, host, port,
                  username='guest', password='',
                  admin_password=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.admin_password = admin_password

    def run(self):
        self.help()

        while True:
            command = raw_input("Office Forest>>")
            if command == 'help':
                self.help()
            elif command == 'config':
                self.config()
            elif command == 'login':
                self.login()
            elif command == 'home':
                self.home()
            elif command == 'plants':
                self.plants()
            elif 'plant' in command:
                args = command.split()
                name = args[1]
                self.plant(name)
            elif command == 'check':
                self.check()
            elif 'upgrade' in command:
                args = command.split()
                upg = args[1]
                self.upgrade(upg)
            elif 'vote' in command:
                args = command.split()
                vote = args[1]
                self.vote(vote)
            elif command == 'create':
                self.admin_create()
            elif 'delete' in command:
                args = command.split()
                deleted = args[1]
                self.delete(deleted)
            elif command == 'quit' or command == '\q':
                break
            else:
                print('Unrecognized command')

    def help(self):
        print """Welcome to Office Forest!

    host={host}:{port}
    logged in as:{username}

    home            -   access home page
    plants          -   view list of available plants
    plant <name>    -   view the plant with that particular name
    check           -   view your own plant's status
    upgrade <upg>   -   upgrade your plant with a specific upgrade
    vote <name>     -   vote a person

    ADMIN
    create          -   create a plant (requires admin password)
    delete <name>   -   delete a plant (requires admin password)

    config          -   set configuration of host & port
    login           -   enter username and password
""".format(host=self.host, port=self.port, 
                   username=self.username)


    def home(self):
        url = '{host}:{port}'.format(host=self.host, port=self.port)
        print('requesting {}'.format(url))
        r = requests.get(url)
        print r.text

    def config(self):
        self.host = raw_input('host[{}]: '.format(self.host)) or self.host
        self.port = raw_input('port[{}]: '.format(self.port)) or self.port

    def login(self):
        self.username = raw_input('username[{}]: '\
                   .format(self.username)) or self.username
        self.password = raw_input('password: ') or self.password

    def plants(self):
        url = '{host}:{port}/plants'.format(host=self.host, 
                                            port=self.port)
        print('requesting {}'.format(url))
        r = requests.get(url)
        print r.text

    def plant(self, name):
        url = '{host}:{port}/plants/{name}'\
              .format(host=self.host, port=self.port, name=name)
        print('requesting {}'.format(url))
        r = requests.get(url)
        plant = r.json()
        print("""
        Office Plant

        Name:{name}
        Type:{type}

        Votes:{vote}
        Obtained upgrade:{upgrades}""")\
        .format(name=plant['name'],
                        type=plant['type'],
                        vote=plant['votes'],
                        upgrades=','.join(plant['upgrades']))

    def check(self):
        if self.username <= '' or self.username == 'guest':
            self.login()
        url = '{host}:{port}/myplant'\
              .format(host=self.host, port=self.port)
        print('requesting {}'.format(url))
        payload = {'operation':'VIEW'}
        r = requests.post(url, 
                          auth=(self.username, self.password), 
                          json=payload,
                          headers={'content-type':'application/json'})
        try:
            plant = r.json()
            print("""
Office Plant

Name :  {name}
Type :  {type}
Votes:  {vote}

Voters:
  {voters}

Obtained upgrade:
  {upgrades}
Available upgrade:
  {aval_upgrade}
            """)\
            .format(name=plant['name'],
                            type=plant['type'],
                            vote=plant['votes'],
                            upgrades='\n  '.join(plant['upgrades']),
                            aval_upgrade='\n  '.join(plant['available_upg']),
                            voters='\n  '.join(plant['voters']))
        except:
            print(r.text)

    def upgrade(self, upgrade):
        if self.username <= '' or self.username == 'guest':
            self.login()
        url = '{host}:{port}/myplant'\
              .format(host=self.host, port=self.port)
        print('requesting {}'.format(url))
        payload = {'operation':'UPGRADE', 'upgrade':upgrade}
        r = requests.post(url, 
                          auth=(self.username, self.password), 
                          json=payload,
                          headers={'content-type':'application/json'})
        try:
            plant = r.json()
            print("""
Upgrade status: {message}

Office Plant

Name :  {name}
Type :  {type}
Votes:  {vote}

Obtained upgrade:
  {upgrades}
Available upgrade:
  {aval_upgrade}
            """)\
            .format(name=plant['name'],
                    type=plant['type'],
                    vote=plant['votes'],
                    message=plant['message'],
                    upgrades='\n  '.join(plant['upgrades']),
                    aval_upgrade='\n  '.join(plant['available_upg']))
        except:
            print(r.text)

    def vote(self, vote):
        if self.username <= '' or self.username == 'guest':
            self.login()
        url = '{host}:{port}/myplant'\
              .format(host=self.host, port=self.port)
        print('requesting {}'.format(url))
        payload = {'operation':'VOTE', 'vote':vote}
        r = requests.post(url, 
                          auth=(self.username, self.password), 
                          json=payload,
                          headers={'content-type':'application/json'})
        print(r.text)

    def admin_create(self):
        url = '{host}:{port}/admin/register'\
              .format(host=self.host, port=self.port)
        print('requesting {}'.format(url))
        name = raw_input(' name: ')
        password = raw_input(' password: ')
        plant_type = raw_input(' type: ')
        payload = {'name':name, 'password':password, 'plant_type':plant_type}
        r = requests.put(url, 
                          auth=(self.username, self.password), 
                          json=payload,
                          headers={'content-type':'application/json'})
        print(r.text)

    def delete(self, name):
        url = '{host}:{port}/admin/delete/{name}'\
              .format(host=self.host, port=self.port,
                      name=name)
        print('requesting {}'.format(url))
        r = requests.delete(url, 
                          auth=(self.username, self.password), 
                          headers={'content-type':'application/json'})
        print(r.text)







if __name__ == '__main__':
    cc = ClientConsole('http://127.0.0.1','5000',
                        username='adi', password='g3tRek7')
    cc.run()