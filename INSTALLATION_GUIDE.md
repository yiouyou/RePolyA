# Installation Guide for RePolyA (Research PolyAgents)

Welcome to the RePolyA installation guide. This guide will walk you through the steps to get RePolyA set up on your machine.

## Prerequisites

Before beginning the installation, make sure you have:

- Python (version 3.6 or later)
- Git
- Pip (typically included with Python installations)

## Step-by-Step Installation

1. **Clone the Repository**

   Begin by cloning the RePolyA repository to your local machine:

   ```bash
   git clone https://github.com/yiouyou/RePolyA.git
   cd RePolyA
   ```

2. **Setting Up a Virtual Environment**

   It's advisable to use a virtual environment to manage dependencies and avoid potential conflicts:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   With the virtual environment activated, you can install the required packages:

   ```bash
   pip install -r requirements.txt
   pip install torch==2.0.1+cpu torchvision==0.15.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
   pip install -r repolya/paper/requirements.txt
   ```

4. **Install Node/Chromium/Mermaid**

   Node:

   ```bash
   curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
   sudo apt install nodejs
   ```

   Chromium:

   ```bash
   sudo apt-get install chromium-browser
   ```

   Mermaid:

   ```bash
   npm install puppeteer
   npm install @mermaid-js/mermaid-cli
   ```

   Edit ~/.bashrc

   ```bash
   alias mmdc='~/node_modules/.bin/mmdc'
   export PUPPETEER_EXECUTABLE_PATH=/snap/bin/chromium
   ```

   Test Mermaid

   ```bash
   mmdc -i test.mmd -o test.png
   ```

5. **Set Up SSL**

   ```
   mkdir ssl
   cd ssl
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes
   > ssl/key.pem, ssl/cert.pem
   ```

6. **Configuration** (If required)

   Certain modules or functionalities might need additional configuration or setup, such as setting environment variables or configuring external services. Refer to the [Configuration Guide](https://github.com/yiouyou/RePolyA/blob/main/CONFIGURATION_GUIDE.md) for more specifics.

7. **Verify Installation**

   Run preliminary tests or launch the application to verify the setup:

   ```bash
   python run.py
   ```

## Troubleshooting

If you run into any problems:

- Double-check all prerequisites are installed correctly.
- Reconfirm the installation steps.
- Consult the project's FAQ or open an issue in the repository.

## Staying Updated

To ensure your local RePolyA version is up-to-date with the main repository:

```bash
git pull origin main  # or 'master', based on the default branch name
pip install -r requirements.txt  # to install new dependencies, if any
```

Thank you for installing RePolyA. Dive in and happy researching!
