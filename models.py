from pydantic import BaseModel, Field, field_validator
from typing import Optional
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re
import json


class MathExpression(BaseModel):
    """Pydantic model for mathematical expressions"""
    mathjs: str = Field(..., description="Expression in MathJS format")
    latex: str = Field(..., description="Expression in LaTeX format")
    sympy_repr: Optional[str] = Field(None, description="Sympy representation if available")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    user_input: Optional[str] = Field(None, description="Original user input query")
    
    @field_validator('mathjs')
    def validate_mathjs(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("MathJS expression must be a non-empty string")
        return v
    
    @field_validator('latex')
    def validate_latex(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("LaTeX expression must be a non-empty string")
        return v
    
    def render_sympy(self) -> bool:
        """Try to render the expression using SymPy and store the representation
        
        Returns:
            bool: True if rendering was successful, False otherwise
        """
        if not self.mathjs:
            return False
            
        try:
            # Configure transformations for parsing
            transformations = standard_transformations + (implicit_multiplication_application,)
            
            # Clean up the expression string (convert MathJS to SymPy-compatible syntax)
            clean_expr = self.mathjs.replace("^", "**")
            sympy_expr = parse_expr(clean_expr, transformations=transformations)
            
            # Store the pretty-printed version
            self.sympy_repr = str(sp.pretty(sympy_expr))
            return True
        except Exception:
            return False
    
    def display(self) -> str:
        """Format the expression for display
        
        Returns:
            str: Formatted string representation
        """
        output = [
            "Mathematical Expression:",
        ]
        
        if self.user_input:
            output.append(f"Query: {self.user_input}")
            
        output.extend([
            f"MathJS: {self.mathjs}",
            f"LaTeX:  {self.latex}"
        ])
        
        if self.sympy_repr:
            output.append("\nSymPy representation:")
            output.append(self.sympy_repr)
        
        if self.response_time is not None:
            output.append(f"\nResponse time: {self.response_time:.3f} seconds")
            
        return "\n".join(output)
    
    @staticmethod
    def extract_json_from_text(text):
        """Extract JSON from text that might contain thinking steps and other content
        
        Args:
            text: Text that might contain JSON
            
        Returns:
            dict: Extracted JSON object or None
        """
        # Try to find JSON objects with both mathjs and latex fields
        json_pattern = r'\{[\s\S]*?"mathjs"\s*:\s*"[^"]*"[\s\S]*?"latex"\s*:\s*"[^"]*"[\s\S]*?\}'
        match = re.search(json_pattern, text)
        
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        # If not found or invalid JSON, try to extract final values using regex
        mathjs_pattern = r'"mathjs"\s*:\s*"([^"]*)"'
        latex_pattern = r'"latex"\s*:\s*"([^"]*)"'
        
        mathjs_match = re.search(mathjs_pattern, text)
        latex_match = re.search(latex_pattern, text)
        
        if mathjs_match and latex_match:
            return {
                "mathjs": mathjs_match.group(1),
                "latex": latex_match.group(1)
            }
            
        return None

    @classmethod
    def clean_llm_output(cls, text):
        """Clean LLM output by removing thinking steps and instructions
        
        Args:
            text: Raw LLM output text
            
        Returns:
            str: Cleaned output text
        """
        # Remove <think>...</think> blocks
        text = re.sub(r'<think>[\s\S]*?</think>', '', text)
        
        # Remove lines with waiting instructions
        text = re.sub(r'/waiting for user to provide the result/', '', text)
        text = re.sub(r'Please provide the result of the .* tool call\.', '', text)
        
        # Remove other reasoning steps that don't contain JSON
        text = re.sub(r"I'll think about.*?\n", '', text)
        text = re.sub(r"I'll analyze.*?\n", '', text)
        text = re.sub(r"Now, I'll create.*?\n", '', text)
        
        return text.strip()
    
    @classmethod
    def from_response(cls, response, response_time=None, user_input=None):
        """Create a MathExpression from an Agno response
        
        Args:
            response: The response from the Agno agent
            response_time: Optional response time in seconds
            user_input: Original user query
            
        Returns:
            MathExpression: Parsed math expression
        """
        # Handle various response formats
        if hasattr(response, 'content'):
            content = response.content
            
            # If content is already a dict
            if isinstance(content, dict):
                if "mathjs" in content and "latex" in content:
                    return cls(**content, response_time=response_time, user_input=user_input)
            
            # If content is a string, clean it and try parsing
            if isinstance(content, str):
                # Clean the content to remove thinking steps
                cleaned_content = cls.clean_llm_output(content)
                
                # Try to extract JSON from the cleaned content
                json_data = cls.extract_json_from_text(cleaned_content)
                if json_data:
                    return cls(**json_data, response_time=response_time, user_input=user_input)
                
                # If all else fails, use the content itself
                parts = cleaned_content.split("\n")
                if len(parts) >= 2:
                    # Try to use the last two non-empty lines as mathjs and latex
                    non_empty = [p for p in parts if p.strip()]
                    if len(non_empty) >= 2:
                        return cls(mathjs=non_empty[-2], latex=non_empty[-1], response_time=response_time, user_input=user_input)
                
                return cls(mathjs=cleaned_content, latex=cleaned_content, response_time=response_time, user_input=user_input)
                
        # If response is a string
        elif isinstance(response, str):
            # Clean the response
            cleaned_response = cls.clean_llm_output(response)
            
            # Try to extract JSON
            json_data = cls.extract_json_from_text(cleaned_response)
            if json_data:
                return cls(**json_data, response_time=response_time, user_input=user_input)
            
            return cls(mathjs=cleaned_response, latex=cleaned_response, response_time=response_time, user_input=user_input)
                
        # If response is a different object with a text attribute
        elif hasattr(response, 'text'):
            text = response.text
            cleaned_text = cls.clean_llm_output(text)
            
            # Try to extract JSON
            json_data = cls.extract_json_from_text(cleaned_text)
            if json_data:
                return cls(**json_data, response_time=response_time, user_input=user_input)
            
            return cls(mathjs=cleaned_text, latex=cleaned_text, response_time=response_time, user_input=user_input)
                
        # Fallback
        return cls(mathjs=str(response), latex=str(response), response_time=response_time, user_input=user_input) 