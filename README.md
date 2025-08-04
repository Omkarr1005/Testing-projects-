# Selenium Form Automation Project

## Overview

This project automates the form submission at https://demoqa.com/automation-practice-form using Selenium WebDriver with Python.

## Features

- Page Object Model (POM) design pattern
- Data-driven testing with JSON input files
- Cross-browser support: Chrome and Firefox
- Explicit waits and exception handling
- Screenshot capture on test failures
- HTML test reports with `pytest-html`
- Configurable via JSON config file

## Setup

```bash
pip install -r requirements.txt
pytest --html=reports/report.html
