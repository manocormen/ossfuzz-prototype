# DEMO: OSS-Fuzz-Research (Prototype)

## Requirements

- Python 3.11

## Usage

After cloning:

- Create and activate a virtual environment.
- Run `pip install -r requirements.txt`.
- Run: `jupyter notebook`.
- Open `Demo.ipynb`.

## Data

For convenience, the notebook defaults to simulating data fetching by loading from disk. However, if you want to run the notebook more realistically, you can generate a GitHub token [here](https://github.com/settings/personal-access-tokens/new) and add it to a `.env` file at the root of the project in the following format:

`GITHUB_TOKEN=<insert-your-generated-token-here>`

Then, in the notebook, click: **Kernel > Restart & Run All**.

Whether you're simulating or doing real requests, the API will offer the same functionality (listing, filtering, matching...) and behave the same, except that initial caching will take some time when doing real requests.
