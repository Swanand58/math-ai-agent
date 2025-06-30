# Math AI Agent

A simple math agent built using Agno that converts natural language mathematical expressions into MathJS and LaTeX representations.

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set up your API key:
   - Copy the env.example file to .env:
     ```
     cp env.example .env
     ```
   - Edit the .env file with your API key:
     - You can use GROQ API key (default)
     ```
     GROQ_API_KEY=your_api_key_here
     ```

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
