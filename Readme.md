# Bank Statement Analyzer

This repository provides a tool to analyze business bank statements in PDF format. Given a bank statement, it will:

1. Determine if it's a valid business bank statement
2. Extract business details from it
3. Validate if the reported transactions make sense by reconciling the opening and closing balances

## Setup

1. Clone the repository
2. Run the setup script to create a virtual environment using Poetry:

```bash
bash setup.sh
cd main
```

3. Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your_api_key_here
```

Alternatively, you can create a `.env` file in the root directory with:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the analyzer with a PDF bank statement:

```bash
python3 app.py path/to/bank_statement.pdf
```

The tool will analyze the document and output the results, including:
- Whether it's a valid business bank statement
- Business information (name and address)
- Balance analysis (opening and closing balances)
- Printing some example transactions

## Sample Documents

Two sample documents are included in the `docs` folder for testing purposes.

## Assumptions

The analyzer makes a few assumptions:
- All transactions are in the same currency
- PDF is max 1000 pages
- Maximum of 24,000 transactions per document

## Format the code

To format the code:

```bash
bash format.sh
```
