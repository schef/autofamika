from typing import Optional, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import typer
from dataclasses import dataclass
import sys
import re

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

import time


@dataclass
class Credentials:
    username: Optional[str] = None
    password: Optional[str] = None


creds = Credentials()
try:
    import credentials

    creds.username = credentials.username
    creds.password = credentials.password
except Exception as e:
    print(f"No credentials file error with {e}")
    sys.exit()

app = typer.Typer(help="Awesome CLI epapre acep.")
driver: Optional[webdriver.Firefox] = None


class Biolectric:
    SITE = "https://app.biolectric.be/en/machines/index"
    LOGIN_USER_ID = "login"
    LOGIN_PASS_ID = "password"
    LOGIN_BUTTON_CLASS_NAME = "btn.btn-lg.btn-block"
    ONLINE_CLASS_NAME = "online"
    ONLINE_TAG_NAME = "td"
    ONLINE_TRUE_CLASS_NAME = "fa.fa-check"
    ID_CLASS_NAME = "action.detail"
    ID_TAG_NAME = "td"
    ID_DATA_TAG_NAME = "a"
    ENGINE_TAG_NAME = "td"
    ENGINE_TEXT = "Engine state"
    ENGINE_DATA_CLASS_NAME = "readable-status"


@dataclass
class Engine:
    name: str = ""
    power_in_w: int = -1
    set_power: int = -1
    servo_position_percent: int = -1
    engine_state: str = ""
    motor_error: str = ""
    produced_green_energy_in_kwh: int = -1
    engine_hours_run: int = -1
    engine_total_hours_run: int = -1
    gas_consumption_in_m3: int = -1
    service_in_h: int = -1
    reset_hours_to_service: Any = None
    battery_voltage_in_vdc: float = -1.0
    water_pressure_in_the_cold_water_circuit_in_mbar: int = -1

    def __str__(self):
        string = ""
        string += f"Engine: {self.name}" + "\n"
        string += f"  power= {self.power_in_w} W" + "\n"
        return string


def login(driver):
    username = driver.find_element(by=By.ID, value=Biolectric.LOGIN_USER_ID)
    username.send_keys(creds.username)
    password = driver.find_element(by=By.ID, value=Biolectric.LOGIN_PASS_ID)
    password.send_keys(creds.password)
    button = driver.find_element(by=By.CLASS_NAME, value=Biolectric.LOGIN_BUTTON_CLASS_NAME)
    button.click()


def getDriver():
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox()
    return driver


def is_online(driver):
    elements = driver.find_elements(by=By.CLASS_NAME, value=Biolectric.ONLINE_CLASS_NAME)
    for element in elements:
        if element.tag_name == Biolectric.ONLINE_TAG_NAME:
            if len(element.find_elements(By.CLASS_NAME, value=Biolectric.ONLINE_TRUE_CLASS_NAME)) >= 1:
                return True
            else:
                return False
    return None


def click_machine_id(driver):
    elements = driver.find_elements(by=By.CLASS_NAME, value=Biolectric.ID_CLASS_NAME)
    for element in elements:
        if element.tag_name == Biolectric.ID_TAG_NAME:
            element.click()
            return True
    return False


def get_web_element_attribute_names(web_element):
    """Get all attribute names of a web element"""
    # get element html
    html = web_element.get_attribute("outerHTML")
    # find all with regex
    pattern = """([a-z]+-?[a-z]+_?)='?"?"""
    return re.findall(pattern, html)


def print_element(element):
    print(element)
    print(f"  tag_name[{element.tag_name}]")
    print(f"  text[{element.text}]")
    for a in get_web_element_attribute_names(element):
        print(f"  {a}[{element.get_attribute(a)}]")


def def_table_field_text(table, xpath):
    return WebDriverWait(table.find_element(by=By.XPATH, value=xpath), 10, 1, None).until(lambda x: len(x.text) > 0, "No text")


def wait_for_table_to_load(table):
    WebDriverWait(table.find_element(by=By.XPATH, value="tbody/tr[3]/td[2]/span"), 10, 1, None).until(lambda x: len(x.text) > 0, "No text")


def get_table_element(table, xpath):
    return table.find_element(by=By.XPATH, value=xpath).text


def get_engine_data(driver):
    engine_1 = Engine()
    engine_2 = Engine()
    table = driver.find_element(by=By.CLASS_NAME, value="table")
    wait_for_table_to_load(table)

    engine_1.name = get_table_element(table, "thead/tr/th[2]")
    engine_2.name = get_table_element(table, "thead/tr/th[4]")

    print(engine_1)
    print(engine_2)
    return [engine_1, engine_2]


@app.command()
def repl():
    import readline
    import rlcompleter
    import code

    # TODO: repl does not see classes

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())


@app.command()
def test():
    driver.get(Biolectric.SITE)
    login(driver)
    click_machine_id(driver)
    get_engine_data(driver)


@app.command()
def status():
    driver.get(Biolectric.SITE)
    login(driver)
    online = is_online(driver)
    print(f"ONLINE: {online}")


@app.callback()
def main():
    global driver
    driver = getDriver()


if __name__ == "__main__":
    app()
