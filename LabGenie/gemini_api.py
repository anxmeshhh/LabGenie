import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_lab_record(experiment_description, readings_data):
    # Configure Gemini API with the key from .env
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise Exception("GEMINI_API_KEY not found in .env file")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Using more stable model
    
    # Format readings as a readable string
    readings_str = "; ".join([f"({x}, {y})" for x, y in readings_data])
    
    prompt = f"""
    Generate a lab record for the experiment described as '{experiment_description}' with readings: {readings_str}

    Create a lab record with these sections:
    - Aim: State the objective (1-2 sentences)
    - Theory: Explain the scientific principle (150-200 words)
    - Procedure: List the steps (numbered format)
    - Result: Summarize findings (2-3 sentences)
    - x_label: Describe what the x-axis represents (1 sentence)
    - y_label: Describe what the y-axis represents (1 sentence)

    IMPORTANT: Return ONLY a valid JSON object with no additional text, markdown, or formatting. Format exactly like this:

    {{"aim": "Your aim text here", "theory": "Your theory text here", "procedure": "1. Step one\\n2. Step two\\n3. Step three", "result": "Your result text here", "x_label": "Your x-axis description", "y_label": "Your y-axis description"}}
    """
    
    try:
        # Configure generation parameters for more reliable output
        generation_config = {
            "temperature": 0.3,  # Lower temperature for more consistent output
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        response = model.generate_content(
            prompt, 
            generation_config=generation_config
        )
        
        if not response or not response.text:
            raise Exception("Empty response from Gemini API")
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown code blocks if present
        response_text = re.sub(r'^```json\s*', '', response_text, flags=re.MULTILINE)
        response_text = re.sub(r'^```\s*$', '', response_text, flags=re.MULTILINE)
        response_text = response_text.strip()
        
        # Try to extract JSON if it's embedded in other text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        print(f"Cleaned API response: {response_text}")  # Debug logging
        
        # Parse the JSON string into a dictionary
        lab_record = json.loads(response_text)
        
        # Validate required keys
        required_keys = {'aim', 'theory', 'procedure', 'result', 'x_label', 'y_label'}
        if not all(key in lab_record for key in required_keys):
            missing_keys = required_keys - set(lab_record.keys())
            raise Exception(f"Missing required keys in API response: {missing_keys}")
        
        return lab_record
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error. Raw response: '{response.text if response else 'No response'}'")
        # Fallback: create a basic lab record if JSON parsing fails
        return create_fallback_record(experiment_description, readings_data)
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        # Fallback: create a basic lab record if API fails
        return create_fallback_record(experiment_description, readings_data)

def create_fallback_record(experiment_description, readings_data):
    """Create a basic lab record when API fails"""
    # Analyze readings for basic insights
    x_values = [x for x, y in readings_data]
    y_values = [y for x, y in readings_data]
    
    # Determine if it's linear relationship
    is_linear = len(set(round(y/x, 2) if x != 0 else 0 for x, y in readings_data if x != 0)) <= 2
    
    return {
        "aim": f"To conduct the {experiment_description} experiment and analyze the relationship between the measured variables.",
        "theory": f"This experiment involves measuring two variables to understand their relationship. Based on the data pattern, this appears to be studying {'a linear relationship' if is_linear else 'a non-linear relationship'} between the independent and dependent variables. The theoretical foundation depends on the specific nature of the experiment being conducted.",
        "procedure": f"1. Set up the experimental apparatus for {experiment_description}\n2. Take initial measurements and record baseline values\n3. Vary the independent variable systematically\n4. Record corresponding dependent variable values\n5. Repeat measurements for accuracy\n6. Plot the data and analyze the relationship",
        "result": f"The experiment yielded {len(readings_data)} data points ranging from ({min(x_values)}, {min(y_values)}) to ({max(x_values)}, {max(y_values)}). The data shows {'a linear trend' if is_linear else 'a curved relationship'} between the variables.",
        "x_label": "Independent variable (X)",
        "y_label": "Dependent variable (Y)"
    }