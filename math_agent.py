from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.reasoning import ReasoningTools
import os
import time
from dotenv import load_dotenv

from models import MathExpression
from tools import MathTools

# Load environment variables from .env file
load_dotenv()

# Debug flag
DEBUG = False

class MathAgent:
    def __init__(self, model_provider="groq"):
        """Initialize the math agent with Agno
        
        Args:
            model_provider (str): The model provider to use, 'groq' for now
        """
        # Configure the model based on provider
        if model_provider.lower() == "groq":
            model = Groq(id="llama3-70b-8192")
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")
        
        self.agent = Agent(
            model=model,
            tools=[ReasoningTools(add_instructions=True)],
            instructions="""
            You are a math expression parser that converts natural language to mathematical expressions.
            
            Given a natural language input describing a mathematical expression, you must:
            1. Understand what mathematical operation/expression the user is describing
            2. Output ONLY a JSON object with two fields:
               - mathjs: the expression in MathJS format
               - latex: the same expression in LaTeX format
            
            IMPORTANT: DO NOT include any reasoning, thinking steps, or explanations in your response.
            DO NOT include <think> tags or any other tags.
            Just return the raw JSON object and nothing else.
            
            Example input: "I want the summation of x and y"
            Example output: {"mathjs": "x + y", "latex": "x + y"}
            
            Example input: "What is the square root of x squared plus y squared"
            Example output: {"mathjs": "sqrt(x^2 + y^2)", "latex": "\\sqrt{x^2 + y^2}"}
            
            Example input: "Calculate the derivative of x squared"
            Example output: {"mathjs": "derivative(x^2, x)", "latex": "\\frac{d}{dx}(x^2)"}
            
            Be precise and do not include any explanations or thinking steps, just return the JSON object.
            """,
            structured_outputs=True,
            use_json_mode=True,
        )
        # Initialize the tools
        self.math_tools = MathTools()
        # Store last raw response for debugging
        self.last_raw_response = None
    
    def process_expression(self, user_input):
        """Process a natural language math expression and return a MathExpression
        
        Args:
            user_input (str): User's natural language math query
            
        Returns:
            MathExpression: The parsed mathematical expression
        """
        # Save the original user input
        original_input = user_input
        
        # Add explicit instruction to return only JSON to prevent thinking steps
        enhanced_input = f"""
        Convert this math expression to MathJS and LaTeX formats:
        "{user_input}"
        
        Return ONLY a JSON object with mathjs and latex fields, without any explanations or thinking steps.
        """
        
        # Measure response time
        start_time = time.time()
        response = self.agent.run(enhanced_input)
        end_time = time.time()
        response_time = end_time - start_time
        
        # Store raw response for debugging
        self.last_raw_response = response
        
        # Parse the response into our MathExpression model
        math_expr = MathExpression.from_response(
            response, 
            response_time=response_time,
            user_input=original_input
        )
        
        # Try to render it with SymPy
        math_expr.render_sympy()
        
        return math_expr
    
    def get_last_raw_response(self):
        """Get the last raw response from the agent
        
        Returns:
            The last raw response
        """
        return self.last_raw_response
    
    def save_expression(self, math_expr, filename=None):
        """Save a math expression to a file
        
        Args:
            math_expr (MathExpression): The expression to save
            filename (str, optional): A filename to save to
            
        Returns:
            str: The path to the saved file
        """
        return self.math_tools.save_to_file(math_expr, filename)

def handle_command(user_input, math_agent, last_expression=None):
    """Handle special commands from the user
    
    Args:
        user_input (str): The user's input
        math_agent (MathAgent): The math agent instance
        last_expression (MathExpression, optional): The last processed expression
        
    Returns:
        tuple: (bool, MathExpression) - (whether the input was a command, the last expression)
    """
    cmd = user_input.lower().strip()
    
    if cmd in ['exit', 'quit']:
        print("Goodbye!")
        exit(0)
    
    if cmd.startswith('save'):
        if last_expression is None:
            print("No expression to save. Process an expression first.")
            return True, last_expression
        
        parts = cmd.split(' ', 1)
        filename = parts[1].strip() if len(parts) > 1 else None
        
        saved_path = math_agent.save_expression(last_expression, filename)
        print(f"\nExpression saved to: {saved_path}")
        return True, last_expression
    
    if cmd == 'list':
        expressions = MathTools.list_saved_expressions()
        if expressions:
            print("\nSaved expressions:")
            for i, expr in enumerate(expressions, 1):
                print(f"{i}. {expr}")
        else:
            print("\nNo saved expressions found.")
        return True, last_expression
    
    if cmd.startswith('load'):
        parts = cmd.split(' ', 1)
        if len(parts) < 2:
            print("Please specify a filename to load.")
            return True, last_expression
        
        filename = parts[1].strip()
        try:
            loaded_expr = MathTools.load_from_file(filename)
            print("\nLoaded expression:")
            print(loaded_expr.display())
            return True, loaded_expr
        except Exception as e:
            print(f"Error loading expression: {e}")
            return True, last_expression
    
    if cmd == 'debug':
        # Toggle debug mode
        global DEBUG
        DEBUG = not DEBUG
        print(f"\nDebug mode {'enabled' if DEBUG else 'disabled'}")
        return True, last_expression
    
    if cmd == 'raw':
        # Show the raw response from the last query
        if math_agent.get_last_raw_response() is None:
            print("\nNo previous response to show")
        else:
            print("\n--- Raw Response ---")
            # Try to get the content
            raw_resp = math_agent.get_last_raw_response()
            if hasattr(raw_resp, 'content'):
                print(raw_resp.content)
            else:
                print(str(raw_resp))
            print("-------------------")
        return True, last_expression
    
    if cmd in ['help', '?']:
        print("\nAvailable commands:")
        print("  save [filename] - Save the last expression to a file")
        print("  load <filename> - Load an expression from a file")
        print("  list - List all saved expressions")
        print("  debug - Toggle debug mode")
        print("  raw - Show raw response from the last query")
        print("  help, ? - Show this help message")
        print("  exit, quit - Exit the program")
        print("\nAny other input will be treated as a math expression to process.")
        return True, last_expression
    
    # Not a command
    return False, last_expression

def main():
    """Main function to run the math agent"""
    if not os.getenv("GROQ_API_KEY"):
        print("api key not found")
        exit(1)
    
    print(f"Using Groq as the model provider.")
    math_agent = MathAgent(model_provider="groq")
    
    print("\n Math Expression Parser (type 'help' for commands, 'exit' to quit)")
    print("-------------------------------------------------------------------")
    
    last_expression = None
    
    while True:
        user_input = input("\nEnter a math expression or command: ")
        
        is_command, last_expression = handle_command(user_input, math_agent, last_expression)
        if is_command:
            continue
        
        try:
            # Add a loading indicator
            print("Processing expression...", end="\r")
            
            math_expr = math_agent.process_expression(user_input)
            last_expression = math_expr
            
            # Clear the loading indicator and display results
            print(" " * 25, end="\r")  # Clear the loading text
            print("\n" + math_expr.display())
            
            # Print debug info if enabled
            if DEBUG:
                print("\nDEBUG - Raw response:")
                raw_resp = math_agent.get_last_raw_response()
                if hasattr(raw_resp, 'content'):
                    print(raw_resp.content)
                else:
                    print(str(raw_resp))
            
        except Exception as e:
            print(f"Error processing expression: {e}")
            print("Try a simpler math expression or check your API key configuration.")

if __name__ == "__main__":
    main() 