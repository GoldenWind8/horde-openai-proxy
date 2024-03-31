# OpenAI-Compatible API

This is an OpenAI-compatible API that provides a seamless interface for interacting with language models. It supports chat completions and text completions, similar to the OpenAI API, while leveraging the power of the Kobold API behind the scenes.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- FastAPI
- python-dotenv

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/openai-compatible-api.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   - Create a `.env` file in the project root directory.
   - Define the following variables in the `.env` file:
     ```
     API_KEY=your_api_key
     BASE_URL=https://api.aipowergrid.io
     ```
   - Replace `your_api_key` with your actual API key.

### Usage

1. Start the API server:
   ```
   uvicorn main:app --reload
   ```

2. The API will be accessible at `http://localhost:8000`.

## API Endpoints

### Chat Completions

- Endpoint: `/v1/chat/completions`
- Method: POST
- Description: Generates a chat completion based on the provided conversation context.
- Documentation: [OpenAI Chat Completion API](https://platform.openai.com/docs/api-reference/chat)

### Text Completions

- Endpoint: `/v1/completions`
- Method: POST
- Description: Generates a text completion based on the provided prompt.
- Documentation: [OpenAI Completion API](https://platform.openai.com/docs/api-reference/completions)

## Configuration

The API can be configured using environment variables defined in the `.env` file:

- `API_KEY`: The API key for authentication. Defaults to `"0000000000"` if not provided.
- `BASE_URL`: The base URL for the Horde Compatible API. Defaults to an empty string if not provided.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](link_to_license_file).