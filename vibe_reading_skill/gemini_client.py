"""
Gemini API Client Wrapper
Provides interface for interacting with Google Gemini API

Features:
- Auto retry mechanism: Automatically retry up to 5 times when encountering 429 quota limit errors
- Smart wait time: Extract suggested wait time from error messages, or use predefined sequence (90/120/150/180/210 seconds)
- Proxy support: Support proxy configuration via HTTP_PROXY and HTTPS_PROXY environment variables
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

class GeminiClient:
    """Gemini API Client"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, proxy: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API Key, if not provided will read from environment variable
            model: Model name to use, if not provided will read from environment variable, default gemini-2.5-pro
            proxy: Proxy server address (format: http://host:port or https://host:port), used to resolve geographic restrictions
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file or pass as parameter.")
        
        # Supported model list
        self.available_models = [
            "gemini-3-pro",        # Gemini 3 flagship model (latest, strongest)
            "gemini-3",            # Gemini 3 standard model
            "gemini-2.5-pro",      # Gemini 2.5 flagship model
            "gemini-2.5-flash",    # Gemini 2.5 fast model
            "gemini-2.0-flash-exp", # Experimental version
            "gemini-1.5-pro",      # Stable version
            "gemini-1.5-flash",    # Fast version
            "gemini-pro",          # Old version
        ]
        
        # Get model name: parameter > environment variable > default value
        # Default use gemini-2.5-pro (stable and reliable)
        default_model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        self.model_name = model or default_model
        
        # Verify if model is in supported list (allow users to use other models)
        if self.model_name not in self.available_models:
            print(f"⚠️  Warning: Model '{self.model_name}' is not in recommended list, but will continue to try using it")
            print(f"   Recommended models: {', '.join(self.available_models[:3])}")
        
        # Configure proxy (if provided)
        proxy_url = proxy or os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        if proxy_url:
            print(f"🌐 Using proxy: {proxy_url}")
            # Set environment variables to let google-generativeai use proxy
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content (with smart retry mechanism)
        
        When encountering API quota limits (429 error), will automatically retry:
        - Retry up to 5 times
        - Wait time: 90 → 120 → 150 → 180 → 210 seconds (if no suggested time in error message)
        - If error message contains suggested wait time, will prioritize using that time + 5 second buffer
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Temperature parameter
            max_output_tokens: Maximum output token count
        
        Returns:
            AI-generated text content
        
        Raises:
            Exception: If maximum retry count is reached and still fails, will raise exception
        """
        generation_config = {
            "temperature": temperature,
        }
        if max_output_tokens:
            generation_config["max_output_tokens"] = max_output_tokens
        
        # If there's a system instruction, create a new model instance
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model
        
        import time
        max_retries_per_error = 5  # Retry 5 times each time an error is encountered
        # Retry delay sequence: 90, 120, 150, 180, 210 seconds
        retry_delays = [90, 120, 150, 180, 210]
        
        attempt = 0
        while attempt < max_retries_per_error:
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                # Print complete error information for debugging
                if attempt == 0:  # Only print complete error on first failure
                    print(f"  🔍 Complete error information: {error_str[:500]}...")  # Only print first 500 characters
                
                # Check if it's a quota limit error (429)
                if "429" in error_str or "Resource has been exhausted" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries_per_error - 1:
                        # Try to extract retry delay time from error message (multiple formats)
                        import re
                        retry_delay = None
                        
                        # Format 1: "retry in 13.429413162s"
                        delay_match = re.search(r'retry in ([\d.]+)\s*s', error_str, re.IGNORECASE)
                        if delay_match:
                            retry_delay = int(float(delay_match.group(1))) + 5  # Add 5 second buffer
                            print(f"  📋 Extracted suggested wait time from error message: {delay_match.group(1)} seconds")
                        
                        # Format 2: "Please retry in 13.429413162s"
                        if not retry_delay:
                            delay_match = re.search(r'Please retry in ([\d.]+)\s*s', error_str, re.IGNORECASE)
                            if delay_match:
                                retry_delay = int(float(delay_match.group(1))) + 5
                                print(f"  📋 Extracted suggested wait time from error message: {delay_match.group(1)} seconds")
                        
                        # Format 3: Check exception object attributes (Google API may store information here)
                        if not retry_delay and hasattr(e, 'retry_delay'):
                            retry_delay = int(e.retry_delay) + 5
                            print(f"  📋 Extracted wait time from exception object: {e.retry_delay} seconds")
                        
                        # If none extracted, use predefined delay sequence
                        if not retry_delay:
                            retry_delay = retry_delays[attempt]  # 90, 120, 150, 180, 210 seconds
                            print(f"  📋 No suggested wait time found, using predefined delay: {retry_delay} seconds")
                        
                        # Ensure wait time is at least the minimum in the sequence
                        retry_delay = max(retry_delay, retry_delays[0])
                        
                        print(f"  ⚠️  API quota limit, waiting {retry_delay} seconds before retry ({attempt + 1}/{max_retries_per_error})...")
                        time.sleep(retry_delay)
                        attempt += 1
                        continue
                    else:
                        # Reached maximum retry count, raise exception (let upper layer handle, may call this function again)
                        raise Exception(f"Error generating content: {error_str}\nReached maximum retry count ({max_retries_per_error} times), please try again later or check API quota.")
                else:
                    # Other errors directly raise
                    raise Exception(f"Error generating content: {error_str}")
    
    def generate_content_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Stream generate content (for long text output)
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Temperature parameter
        
        Yields:
            AI-generated text chunks
        """
        generation_config = {
            "temperature": temperature,
        }
        
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}")
    
    def analyze_document_structure(self, document_content: str) -> Dict:
        """
        Analyze document structure (chapter identification)
        
        Args:
            document_content: Document content
        
        Returns:
            Dictionary containing chapter information
        """
        prompt = f"""Please analyze the chapter structure of the following document.

Document content:
{document_content[:50000]}  # Limit length to avoid exceeding context window

Please return chapter information in JSON format, containing:
- chapters: Chapter list, each chapter contains number, title, start_line, end_line, filename, confidence

If the document is too long, please analyze the first part first, then I can continue providing subsequent content."""
        
        response = self.generate_content(prompt, temperature=0.3)
        return response
    
    def decide_breakdown_strategy(self, chapter_content: str, chapter_info: Dict) -> Dict:
        """
        Decide if chapter needs further breakdown
        
        Args:
            chapter_content: Chapter content
            chapter_info: Chapter information
        
        Returns:
            Breakdown decision and strategy
        """
        prompt = f"""Please evaluate if the following chapter needs further breakdown.

Chapter information:
{chapter_info}

Chapter content (first 10000 characters):
{chapter_content[:10000]}

Please consider:
1. Content complexity and density
2. Semantic integrity
3. Analysis quality requirements
4. Context window limitations

Return JSON format:
{{
    "needs_breakdown": true/false,
    "reason": "reason",
    "breakdown_points": [breakdown point list],
    "parts": [part list]
}}"""
        
        response = self.generate_content(prompt, temperature=0.3)
        return response
    
    def analyze_chapter(
        self,
        chapter_content: str,
        previous_summary: Optional[str] = None,
        chapter_metadata: Optional[Dict] = None
    ) -> str:
        """
        Analyze chapter and generate summary
        
        Args:
            chapter_content: Chapter content
            previous_summary: Previous chapter summary (optional)
            chapter_metadata: Chapter metadata (optional)
        
        Returns:
            Chapter summary in Markdown format
        """
        # Build context
        context = ""
        if previous_summary:
            context += f"Previous chapter summary:\n{previous_summary}\n\n"
        if chapter_metadata:
            context += f"Chapter information:\n{chapter_metadata}\n\n"
        
        prompt = f"""{context}

Please deeply analyze the following chapter content and generate a detailed summary.

Chapter content:
{chapter_content}

Please generate a summary in Markdown format, containing:
1. Executive Summary (chapter abstract)
2. Detailed Analysis
3. Key Takeaways
4. Connection to Previous Chapter
5. Notable Quotes

Please ensure the analysis is deep, accurate, and coherent with previous chapters."""
        
        response = self.generate_content(prompt, temperature=0.7)
        return response
