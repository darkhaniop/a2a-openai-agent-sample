# A2A + OpenAI-Agents SDK Sample

A sample agent (CurrencyAgent) utilizing the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) and served via the A2A protocol.

---

**This is code is not meant to be used in production. Furthermore, at the time of making this example the A2A protocol spec is being actively developed.**

## Prerequisites

- Python 3.13
- uv

## Running

1. Clone the repository:
   ```bash
   git clone https://github.com/darkhaniop/a2a-openai-agent-sample.git
   ```

2. Navigate to `a2a-openai-agent-sample` and install dependencies:
   ```bash
   cd a2a-openai-agent-sample
   uv sync
   ```

   `uv sync` will install the `openai-agents` with its dependencies and the `a2a-samples` package from GitHub.

3. Make sure the environment variable `OPENAI_API_KEY` is set, or alternatively, create a `.env` file with the key:
   ```
   OPENAI_API_KEY="your-OPENAI-key"
   ```

4. Start the server (by defult it will listen on `localhost:10101`):
   ```bash
   uv run python -m a2a_openai_agent_sample
   ```
   or specify a custom port:
   ```bash
   uv run python -m a2a_openai_agent_sample --port 23232
   ```

5. In another terminal, run one of the sample clients according to the instructions in `a2a-samples` [README](https://github.com/google/A2A/blob/72b60eb6e6f28284a1d7b3723f4f59057153e7c4/samples/python/README.md). For example, navigate to the directory with your local copy of `A2A` and launch the CLI client:
   ```bash
   cd A2A
   cd samples/python
   uv run hosts/cli --agent http://localhost:10101
   ```

## Example prompts

#### Test 1:

- *User*: what is the USD to JPY rate?
- *Agent*: The current exchange rate from USD to JPY is 142.84.
- *User*: What was the exchange rate for the same pair on March 1, 2025?
- *Agent*: The exchange rate from USD to JPY on March 1, 2025, was 150.76.
- *User*: How are the markets doing today?
- *Agent*: I can only assist with currency-related queries and cannot provide information on market conditions.

#### Test 2:

- *User*: What was the exchange rate from USD to British pounds on March 1, 2021?
- *Agent*: The exchange rate from USD to British pounds on March 1, 2021, was 0.71814 GBP for 1 USD.
- *User*: What was the conversion rate the other way around?
- *Agent*: The exchange rate from British pounds to USD on March 1, 2021, was 1.3925 USD for 1 GBP.

## Authors

The code in this repository is meant to reproduce the functionality of the `langchain` agent from the [`a2a-samples`](https://github.com/google/A2A) project and is largely derived from scripts in that repository. It uses `task_manager.py` and `__main__.py` (from `agents/langchain`) with only adjusted import statements. A copy of the original LICENSE file from `a2a-samples` is in [original-a2a-samples-LICENSE.txt](./original-a2a-samples-LICENSE.txt).
