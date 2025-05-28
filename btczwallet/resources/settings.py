
import os
import json

from toga import App


class Settings():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_config = self.app.paths.config

        if not os.path.exists(self.app_config):
            os.makedirs(self.app_config)

        self.settings_path = os.path.join(self.app_config, 'settings.json')
        if not os.path.exists(self.settings_path):
            with open(self.settings_path, 'w') as file:
                json.dump({}, file)


    def update_settings(self, setting_key, setting_value):
        with open(self.settings_path, 'r') as f:
                settings = json.load(f)
        settings[setting_key] = setting_value
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=4)


    def notification_txs(self):
         with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'notifications_txs' not in settings:
                return False
            else:
                return settings['notifications_txs']
            
    
    def notification_messages(self):
         with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'notifications_messages' not in settings:
                return False
            else:
                return settings['notifications_messages']
            

    def startup(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'startup' not in settings:
                return False
            else:
                return settings['startup']
            

    def currency(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'currency' not in settings:
                return "usd"
            else:
                return settings['currency']
            
    def symbol(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'symbol' not in settings:
                return "$"
            else:
                return settings['symbol']
            

    def minimize_to_tray(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'minimize' not in settings:
                return False
            else:
                return settings['minimize']
            

    def tor_network(self):
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
            if 'tor_network' not in settings:
                return None
            else:
                return settings['tor_network']