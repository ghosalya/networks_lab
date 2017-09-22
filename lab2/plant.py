'''
Data structure for office forest
'''
from flask import json


class PlantUpgrade:
    def __init__(self, name, cost):
        self._name = name
        self._cost = cost

    @property
    def name(self):
        return self.name

    @property
    def cost(self):
        return self.cost


available_upgrades = [PlantUpgrade('Backlight',3),
                      PlantUpgrade('Front Light', 4),
                      PlantUpgrade('Water Sensor', 5),
                      PlantUpgrade('Motion Sensor', 12)]


class Plant:
    event_log = []

    def __init__(self, name, plant_type, password):
        self.name = name
        self.type = plant_type
        self.password = password
        self.votes = 0
        self.voters = []
        self.upgrades = []
        Plant.event_log.append('{plant} joined our office!'\
                                .format(plant=name))

    def vote(self, voter):
        if voter not in self.voters:
            self.voters.append(voter)
            self.votes += 1
            Plant.event_log.append('{voter} voted for {voted}'\
                                   .format(voter=voter.name, voted=self.name))

    def upgrade(self, upgrade):
        if upgrade not in available_upgrades:
            return 'Upgrade not valid'
        if upgrade in self.upgrades:
            return 'Plant already have this upgrade'
        if self.votes >= upgrade.cost:
            self.votes -= upgrade.cost
            self.upgrades.append(upgrade)
            Plant.event_log.append('{plant} has purchased the {upgrade} upgrade'\
                                   .format(plant=self.name, upgrade=upgrade.name))
            return 'Upgrade successful'
        else:
            return 'Not enough votes'

    def to_public_json(self):
        self_parameter = {'name':self.name,
                          'type': self.type,
                          'votes': self.votes,
                          'upgrades': [up.name for up in self.upgrades]}
        return json.dumps(self_parameter)

    def to_private_json(self, password):
        if self.password != password:
            return json.dumps({'error':'wrong password'})
        self_parameter = {'name':self.name,
                          'type': self.type,
                          'votes': self.votes,
                          'voters': self.voters,
                          'upgrades': [up.name for up in self.upgrades]}



