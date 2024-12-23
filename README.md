# Home Information Retriever

A Python program that retrieves detailed information about properties, including property details, nearby schools, and an AI-generated overview using OpenAI's GPT API.

## Setup Instructions

1. **Clone the Repository** `bash
git clone https://github.com/aaron-cho/homeInfoRetriever.git
cd [repository-name]   `

2. **Create Virtual Environment** `bash
python -m venv .venv   `

   Activate the virtual environment:

   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`

3. **Install Dependencies** `bash
pip install openai python-dotenv   `

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here  `

   To get an API key:

   1. Go to [OpenAI's website](https://platform.openai.com/api-keys)
   2. Create an account or sign in
   3. Generate a new API key
   4. Copy the key to your `.env` file

5. **Run the Program** `bash
python home_info.py   `

## Usage

Follow the prompts to enter:

- Street address
- City
- State (2-letter code)
- ZIP code

The program will return:

- Property overview
- Property details (square footage, bedrooms, bathrooms, etc.)
- Information about nearby schools

## Note

This program uses OpenAI's API which may incur charges based on your usage.
