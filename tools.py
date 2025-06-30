import os
import json
from datetime import datetime
from typing import Optional
from models import MathExpression

class MathTools:
    """Tools for working with mathematical expressions"""
    
    @staticmethod
    def save_to_file(math_expr: MathExpression, filename: Optional[str] = None) -> str:
        """Save a mathematical expression to a file
        
        Args:
            math_expr: The mathematical expression to save
            filename: Optional filename to save to. If not provided, 
                      a timestamped file will be created.
                      
        Returns:
            str: Path to the saved file
        """
        # Create expressions directory if it doesn't exist
        os.makedirs('expressions', exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_mathjs = math_expr.mathjs.replace(" ", "_").replace("/", "_").replace("\\", "_")[:20]
            filename = f"expressions/expr_{clean_mathjs}_{timestamp}.txt"
        elif not filename.startswith('expressions/'):
            filename = f"expressions/{filename}"
            
        # Ensure the filename has a .txt extension
        if not filename.endswith('.txt'):
            filename = f"{filename}.txt"
            
        # Write the expression to the file
        with open(filename, 'w') as f:
            # First write the formatted display
            f.write(math_expr.display())
            f.write("\n\n")
            
            # Then write the JSON representation for machine readability
            f.write("JSON Representation:\n")
            json_data = {
                "mathjs": math_expr.mathjs,
                "latex": math_expr.latex,
                "sympy_repr": math_expr.sympy_repr
            }
            
            # Include response time if available
            if math_expr.response_time is not None:
                json_data["response_time"] = math_expr.response_time
            
            # Include user input if available
            if math_expr.user_input is not None:
                json_data["user_input"] = math_expr.user_input
                
            f.write(json.dumps(json_data, indent=2))
            
        return filename
    
    @staticmethod
    def load_from_file(filename: str) -> MathExpression:
        """Load a mathematical expression from a file
        
        Args:
            filename: Path to the file to load from
            
        Returns:
            MathExpression: The loaded mathematical expression
        """
        # If the file doesn't start with expressions/, add it
        if not filename.startswith('expressions/'):
            filename = f"expressions/{filename}"
            
        # Ensure the filename has a .txt extension
        if not filename.endswith('.txt'):
            filename = f"{filename}.txt"
            
        # Check if file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} not found")
            
        # Read the file and look for the JSON representation
        with open(filename, 'r') as f:
            content = f.read()
            
        # Extract the JSON part (between the last "JSON Representation:" and the end of file)
        json_start = content.rfind("JSON Representation:")
        if json_start != -1:
            json_str = content[json_start + len("JSON Representation:"):]
            try:
                json_data = json.loads(json_str.strip())
                return MathExpression(**json_data)
            except json.JSONDecodeError:
                pass
        
        # If we couldn't extract the JSON, try to parse the whole file
        try:
            return MathExpression.from_response(content)
        except Exception as e:
            raise ValueError(f"Could not parse file {filename}: {e}")
    
    @staticmethod
    def list_saved_expressions() -> list[str]:
        """List all saved mathematical expressions
        
        Returns:
            list[str]: List of filenames
        """
        # Create expressions directory if it doesn't exist
        os.makedirs('expressions', exist_ok=True)
        
        # Get all .txt files in the expressions directory
        filenames = [f for f in os.listdir('expressions') if f.endswith('.txt')]
        
        # Sort by modification time (newest first)
        filenames.sort(key=lambda f: os.path.getmtime(os.path.join('expressions', f)), reverse=True)
        
        return filenames 