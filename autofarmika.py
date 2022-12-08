from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import typer
from dataclasses import dataclass
import sys


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


def login(driver):
    username = driver.find_element(by=By.ID, value=Biolectric.LOGIN_USER_ID)
    username.sendKeys(creds.username)
    password = driver.find_element(by=By.ID, value=Biolectric.LOGIN_PASS_ID)
    password.sendKeys(creds.password)


def getDriver():
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox()
    return driver


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
    site = driver.get(Biolectric.SITE)
    login(site)


@app.callback()
def main():
    global driver
    driver = getDriver()


if __name__ == "__main__":
    app()
