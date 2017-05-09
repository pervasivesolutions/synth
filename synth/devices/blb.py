import logging
import random  # TODO: replace with safe random.
import pendulum

from synth.common.ordinal import as_ordinal
from synth.common.conftime import get_interval
from synth.devices.device import Device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Blb(Device):
    """ Battery (powered) light (measuring) button. """

    def get_state(self):
        pass

    def __init__(self, conf, engine, client):
        super(Device, self).__init__()
        self.engine = engine
        self.client = client

        self.id = conf['id']

        # setup battery
        self.battery = 100
        if ['batteryLifeMu', 'batteryLifeSigma'] in conf:
            battery_life_mu = get_interval('batteryLifeMu', None)
            battery_life_sigma = get_interval('batteryLifeSigma', None)
            battery_life_min = battery_life_mu - (2 * battery_life_sigma)
            battery_life_max = battery_life_mu + (2 * battery_life_sigma)
            battery_life = random.normalvariate(battery_life_mu, battery_life_sigma)
            self.battery_life = max(min(battery_life, battery_life_min), battery_life_max)
        else:
            self.battery_life = get_interval('batteryLife', 'PT5M')
        self.battery_auto_replace = conf.get('batteryAutoReplace', False)
        self.engine.register_event_in(self.battery_decay, self.battery_life / 100)

        # setup button press counter
        self.button_press_count = 0
        self.engine.register_event_in(self.press_button, 0)

        # setup light measurement
        self.longitude = conf.get('longitude', 0)
        self.latitude = conf.get('latitude', 0)
        self.is_light = False
        self.engine.register_event_in(self.measure_light, pendulum.interval(hours=1))

        self.client.add_device(self)  # TODO: sim time; serial here.

    def press_button(self):
        if self.battery > 0:
            self.button_press_count += 1
            self.client.update_device(self)  # TODO: sim time; serial here.
            next_press_interval = 1  # TODO: timewave?
            # timewave
            # .next_usage_time
            # synth.simulation.sim.get_time(),
            # ["Mon", "Tue", "Wed", "Thu", "Fri"], "06:00-09:00"
            logger.info("{id}: Pressed button for the {nth} time.".format(
                id=self.id,
                nth=as_ordinal(self.button_press_count),
            ))
            self.engine.register_event_in(self.press_button, next_press_interval)

    def battery_decay(self):
        self.battery -= 1

        if self.battery <= 0 and self.battery_auto_replace:
            logger.info("{id}: Auto-replacing battery.".format(id=self.id))
            self.battery = 100

        logger.info("{id}: Battery decayed to {battery}".format(id=self.id, battery=self.battery))
        self.client.update_device(self)  # TODO: sim time; serial here.

        if self.battery > 0:
            self.engine.register_event_in(self.battery_decay, self.battery_life / 100)

    def measure_light(self):
        if self.battery > 0:
            self.is_light = True  # TODO: all the light things.

            self.client.update_device(self)  # TODO: sim time; serial here.
            self.engine.register_event_in(self.measure_light, 1)  # TODO: Pendulum hourly
