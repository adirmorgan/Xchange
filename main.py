from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.settings import SettingsWithSidebar
from kivy.config import ConfigParser

import requests
import json
import time
import RatesLogic
import os, sys

        
class MainApp(App):
    use_kivy_settings = False
    def build(self):
        self.main_layout = BoxLayout(orientation="vertical")

        self.config = ConfigParser()
        self.config.read('main.ini')

        self.operators = ["/", "*", "+", "-"]
        self.last_was_operator = None
        self.last_button = None
        self.last_was_error = False

        latest_rates_api_endpoint = r'http://api.exchangeratesapi.io/v1/latest'

        self.base_currency, self.rates_dict = RatesLogic.load_from_server(latest_rates_api_endpoint)
        self.used_currency = 'ILS'

        
        app_layout = BoxLayout(orientation="horizontal")
        self.rate = {}


        self.colorplat = {'used_currency':[0.5,1,0,0.5], 'unused':[1,1,1,1]}

        

        # # settings button
        # settings_button = Button(text = "settings", halign="center", font_size=20)
        # settings_button.bind(on_press=self.show_settings)
        # rates_layout.add_widget(settings_button)
        rates_layout = self.build_rates()
        calc_layout = BoxLayout(orientation="vertical")
        self.solution = TextInput(
            multiline=False, readonly=True, halign="right", font_size=55
        )
        calc_layout.add_widget(self.solution)
        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            [".", "0", "C", "+"],
        ]
        for row in buttons:
            h_layout = BoxLayout()
            for label in row:
                button = Button(
                    text=label,
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                )
                button.bind(on_press=self.on_button_press)
                h_layout.add_widget(button)
            calc_layout.add_widget(h_layout)

        equals_button = Button(
            text="=", pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        equals_button.bind(on_press=self.on_solution)
        calc_layout.add_widget(equals_button)

        app_layout.add_widget(rates_layout)
        app_layout.add_widget(calc_layout)

        self.present_layout = app_layout
        return self.present_layout

    def build_rates(self):
        rates_layout = BoxLayout(orientation="vertical")

        all_supported_currencies = ["ILS","USD","EUR","GBP","PLN","KRW"] 
        flag_code = {
            "ILS":'\U0001F1EE',
            "USD":'\U0001F1FA',
            "EUR":'\U0001F1EA',
            "GBP":'\U0001F1EC',
            "PLN":'\U0001F1F5',
            "KRW":'\U0001F1F0'
        }
        self.currencies_to_display = [curr for curr in all_supported_currencies if 
                                        self.config.get('Currencies',curr) == '1']
        
        for curr in self.currencies_to_display:
            self.rate[curr] = Button(halign="left", font_size=20)
            if curr == self.used_currency:
                self.rate[curr].background_color = self.colorplat['used_currency']
            self.rate[curr].text = f'{flag_code[curr]} {curr}='
            self.rate[curr].bind(on_press=self.on_currency_press)
            rates_layout.add_widget(self.rate[curr])

        return rates_layout

    def on_button_press(self, instance):
        if self.last_was_error:
            self.solution.text = ""
        self.last_was_error = False

        current = self.solution.text
        button_text = instance.text

        if button_text == "C":
            # Clear the solution widget
            self.solution.text = "0"
            self.on_solution(instance)
            self.solution.text = ""
        else:
            if current and (
                self.last_was_operator and button_text in self.operators):
                # Don't add two operators right after each other
                return
            elif current == "" and button_text in self.operators:
                # First character cannot be an operator
                return
            else:
                new_text = current + button_text
                self.solution.text = new_text
        self.last_button = button_text
        self.last_was_operator = self.last_button in self.operators

    def on_solution(self, instance):
        eq_to_eval = self.solution.text
        if eq_to_eval:
            try:
                solution = str(eval(eq_to_eval))
            except:
                solution = 'Error!'
                self.last_was_error = True
            self.solution.text = solution
            if not self.last_was_error:
                conv_values = RatesLogic.convValue(float(solution), self.used_currency, self.base_currency, self.rates_dict, 
                                                    self.currencies_to_display)
                for curr in self.currencies_to_display:
                    self.rate[curr].text = f'{curr}={conv_values[curr]:.2f}'

    def on_currency_press(self, instance):
        self.used_currency = instance.text[:3]
        for curr_button in self.rate.values():
            curr_button.background_color = self.colorplat['unused']
        instance.background_color = self.colorplat['used_currency']
        self.on_solution(instance)

    def build_config(self, config):
        config.setdefaults('Currencies', {
            'USD': 1,
            'ILS': 1,
            'EUR': 0,
            'GBP': 0,
            'PLN': 0,
            'KRW': 0})

    def build_settings(self, settings):
        settings.add_json_panel('Currencies', self.config, 'config.json')

    def on_config_change(self, config, section, key, value):
        self.present_layout.remove_widget(self.present_layout.children[0])
        self.present_layout.add_widget(self.build_rates())

if __name__ == "__main__":
    app = MainApp()
    app.run()
    