name: Update flight prices

on:
  workflow_dispatch:
  schedule:
    - cron: "7,22,37,52 * * * *"

permissions:
  contents: write

jobs:
  update-prices:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python -m playwright install chromium

      - name: Update prices
        run: python scripts/update_prices.py

      - name: Commit updated JSON
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/prices.json
          git commit -m "Update prices.json" || echo "No changes to commit"
          git push
