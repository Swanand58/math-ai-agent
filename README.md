# Math AI Agent

A simple math agent built using Agno that converts natural language mathematical expressions into MathJS and LaTeX representations.

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set up your API key:
   - Edit the .env file with your API key:
     - You can use GROQ API key (default)
     ```
     GROQ_API_KEY=your_api_key_here
     ```
     - You can use any other LLM API key by making the appropriate changes in the code (see "Customizing the LLM Provider" section below)

## Usage

Run the math agent:

```
python math_agent.py
```

The agent uses Llama 3 (70B) via the GROQ API.

Enter mathematical expressions in natural language, and the agent will return:

- Original query (for reference)
- MathJS representation
- LaTeX representation
- SymPy rendered expression (when possible)
- Response time (in seconds)

## Customizing the LLM Provider

To use a different LLM provider instead of GROQ:

1. Add the appropriate API key to your `.env` file, for example:

   ```
   # GROQ_API_KEY=your_groq_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   # OPENAI_API_KEY=your_openai_key_here
   ```

2. Modify the `math_agent.py` file to use the desired provider:

   - Uncomment the appropriate import at the top of the file

   ```python
   from agno.models.groq import Groq
   from agno.models.anthropic import Claude  # Uncomment this line for Claude
   from agno.models.openai import OpenAI     # Uncomment this line for OpenAI
   ```

   - Update the `__init__` method in the `MathAgent` class:

   ```python
   def __init__(self, model_provider="claude"):  # Change default here
       """Initialize the math agent with Agno"""
       # Configure the model based on provider
       if model_provider.lower() == "claude":
           model = Claude(id="claude-sonnet-4-20250514")  # Uncomment and modify as needed
       elif model_provider.lower() == "openai":
           model = OpenAI(id="gpt-4o")  # Uncomment and modify as needed
       elif model_provider.lower() == "groq":
           model = Groq(id="llama3-70b-8192")
       else:
           raise ValueError(f"Unsupported model provider: {model_provider}")
   ```

   - Modify the `main()` function to check for your chosen API key:

   ```python
   def main():
       """Main function to run the math agent"""
       # Check for your API key here
       if not os.getenv("ANTHROPIC_API_KEY"):  # Change to your API key
           print("API key not found")
           exit(1)

       print(f"Using Claude as the model provider.")  # Update provider name
       math_agent = MathAgent(model_provider="claude")  # Change provider
   ```

3. The code is designed to work with various LLM providers through Agno's unified interface, but some providers may respond differently, so testing is recommended.

### Commands

The following commands are available:

- `save [filename]` - Save the last expression to a file (in the expressions directory)
- `load <filename>` - Load an expression from a file
- `list` - List all saved expressions
- `debug` - Toggle debug mode to see raw model responses
- `raw` - Show the raw response from the last query
- `help`, `?` - Show help message
- `exit`, `quit` - Exit the program

Example:

```
Enter a math expression or command: integrate x squared

Mathematical Expression:
Query: integrate x squared
MathJS: integrate(x^2, x)
LaTeX:  \int x^2 dx

SymPy representation:
 3
x
──
3

Response time: 1.512 seconds

Enter a math expression or command: save
Expression saved to: expressions/expr_integrate(x^2,_x)_20230815_123456.txt
```

### Features

- Converts natural language to mathematical expressions
- Returns both MathJS and LaTeX formats
- Displays response time for performance monitoring
- Renders expressions using SymPy's pretty printing in the console
- Save expressions to files for later use with full context (including original query)
- Load previously saved expressions
- Debug mode for inspecting raw model responses
- Supports a wide range of mathematical operations

### Tool Calls and Response Processing

The math agent leverages Agno's structured output capabilities and tool calls:

1. **ReasoningTools**: The agent uses Agno's ReasoningTools to enhance its ability to analyze and solve mathematical expressions. These tools help the agent understand the structure and intent behind natural language queries.

2. **Response Processing**: When the agent receives a response from the LLM:

   - Structured JSON is extracted from the raw response
   - Thinking steps and explanations are automatically filtered out
   - The MathJS and LaTeX representations are identified and extracted
   - SymPy attempts to render the expression in a readable format
   - Response time is measured and recorded

3. **File Operations**: The MathTools class provides tools for:

   - Saving expressions to text files with both human-readable and machine-readable formats
   - Loading previously saved expressions
   - Listing available saved expressions

4. **Error Handling**: The agent includes robust error handling to:
   - Clean up inconsistent LLM outputs
   - Extract valid JSON even from verbose responses
   - Provide fallback mechanisms when responses don't match expected formats

This architecture allows the math agent to process a wide range of mathematical expressions reliably, while providing detailed debugging information when needed.

### Saved File Format

When you save an expression, the following information is stored:

1. The original user query
2. The MathJS representation
3. The LaTeX representation
4. The SymPy representation (if available)
5. The response time

Each file contains both a human-readable format and a machine-readable JSON format to facilitate programmatic access.

### Examples

| Natural Language Input                    | MathJS Output        | LaTeX Output        |
| ----------------------------------------- | -------------------- | ------------------- |
| "Summation of x and y"                    | `x + y`              | `x + y`             |
| "Square root of x squared plus y squared" | `sqrt(x^2 + y^2)`    | `\sqrt{x^2 + y^2}`  |
| "Derivative of x squared"                 | `derivative(x^2, x)` | `\frac{d}{dx}(x^2)` |
| "Integrate x squared"                     | `integrate(x^2, x)`  | `\int x^2 dx`       |

Type 'exit' to quit the program.
