# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 22:55:36 2019

@author: jroeh

Wrapper module for selenium.webdriver.Firefox
"""


from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common import exceptions
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait

BY_OPTIONS = [
      "class name",
      "css selector",
      "id",
      "link text",
      "name",
      "partial link text",
      "tag name",
      "xpath"
      ]


class FirefoxDriver(Firefox):
    """wrapper for selenium.webdriver.Firefox"""
    
    def __init__(self, headless=True, executable_path="geckodriver", timeout=10):
        """
        Parameters
        ----------
        headless : bool
            If false, browser window will be opened
        executable_path : str
            Path to geckodriver
        timeout : int
            Timeout for loading browser when calling wait_for_element
        """
        opt = Options()
        opt.headless = headless
        Firefox.__init__(self, options=opt, executable_path=executable_path)
        self.timeout = timeout
    
    def _find_element(self, value, by, high_priority=True):
        """
        Wrapper for 'find_element'
        
        Parameters
        ----------
        value : str
            Attribute value of element
        by : str
            Attribute name
        high_priority : bool
            If true error will be raise when element not located
        
        Returns
        -------
        Element, if element was found
        None, if no element was found and high_priority==False
        If more than one element was found, the first will be returned
        """
        if by == "text":
            value = "//*[contains(text(), '%s')]" % value
            by = "xpath"
        elif by not in BY_OPTIONS:
            # search for attribute with by as attribute name and value as value
            value = "//*[@%s='%s']" % (by, value)
            by = "xpath"
        
        elements = self.find_elements(by=by,value=value)
        if len(elements) == 0:
            if high_priority:
                raise IOError("No element was located!")
            else:
                return None
        if len(elements) > 1:
            print("Warning: More than one element encountered!")
        return elements[0]
    
    def wait_for_element(self, value, by="id", high_priority=True):
        """
        Waits until element is loaded
        
        Parameters
        ----------
        value : str
            Attribute value of element, can also be xpath
        by : str
            Attribute name
        high_priority : bool
            If true, error will be raised when timed out, else it will return
            false
        
        Returns
        -------
        True, if element was found before timeout
        False, if element was not found
        """
        try:
            element_present = presence_of_element_located((by, value))
            WebDriverWait(self, self.timeout).until(element_present)
            return True
        except exceptions.TimeoutException:
            if high_priority:
                self.close()
                raise IOError("Timed out waiting for page to load!")
            else:
                return False
    
    def fill_in_form(self, value, by, keys):
        """
        Locates element and fills in keys
        
        Parameters
        ----------
        value : str
            Attribute value of element, can also be xpath
        by : str
            Attribute name
        keys : str
            Keys to fill in
        
        Returns
        -------
        True, if element was found, else False
        """
        search_form = self._find_element(value, by)
        if search_form == None:
            return False
        search_form.clear()
        search_form.send_keys(keys)
        return True
    
    def select_dropdown(self, value, by, option_text):
        """
        Locates element and selects dropdown option
        
        Parameters
        ----------
        value : str
            Attribute value of element, can also be xpath
        by : str
            Attribute name
        option_text : str
            Text of option which should be selected
        
        Returns
        -------
        True, if option was found and selected
        False, if option was not found
        """
        search_form = self._find_element(value, by)
        for option in search_form.find_elements_by_tag_name("option"):
            if option.text == option_text:
                option.click()
                return True
        print("option %s not found!" % option_text)
        return False
    
    def click_element(self, value, by="id", high_priority=True):
        """
        Locates and clicks element or calls url if element not clickable
        
        Parameters
        ----------
        value : str
            Attribute value of element, can also be xpath
        by : str
            Attribute name
        high_priority : bool
            If true, error will be raised if not clickable or else
        
        Returns
        -------
        True, if element was found and clicked, else false
        """
        element = self._find_element(value, by, high_priority)
        if element == None:
            return False
        
        try:
            element.click()
        except exceptions.ElementClickInterceptedException:
            # if element not clickable, new page will be opened by href
            url = element.get_attribute("href")
            if url == None:
                if high_priority:
                    raise IOError("element not clickable and no href!")
                else:
                    return False
            self.get(url)
        return True


if __name__ == "__main__":
    url = "https://www.wikipedia.org/"
    driver = FirefoxDriver(False)
    driver.get(url)
    driver.select_dropdown("searchLanguage", "id", "English")
    driver.fill_in_form("searchInput", "id", "Selenium")
    driver.click_element("search-input-button", "data-jsl10n")