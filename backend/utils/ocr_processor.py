import pytesseract
from PIL import Image
import re
import json
from datetime import datetime
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure OpenAI client for OpenRouter
print(f"🔑 API Key loaded: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"🌐 Base URL: {os.getenv('OPENAI_API_BASE')}")

client = openai.OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv("OPENAI_API_BASE"),
    default_headers={
        "HTTP-Referer": "https://localhost:8001",  # Required for some OpenRouter models
        "X-Title": "Invoice Chain Agent"  # Optional app identification
    }
)

def extract_text_from_image(image_file):
    """Extract text from uploaded image using OCR"""
    try:
        print(f"🔍 Starting OCR processing for file: {getattr(image_file, 'filename', 'unknown')}")
        
        # Open and process the image
        image = Image.open(image_file)
        print(f"📷 Image loaded successfully: {image.size} pixels, mode: {image.mode}")
        
        # Convert to RGB if necessary for better OCR
        if image.mode != 'RGB':
            image = image.convert('RGB')
            print("🔄 Converted image to RGB mode")
        
        # Perform OCR
        print("🤖 Running Tesseract OCR...")
        text = pytesseract.image_to_string(image)
        
        print(f"✅ OCR completed successfully. Extracted {len(text)} characters")
        print(f"📝 First 200 characters: {text[:200]}...")
        
        return text.strip()
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_invoice_data_with_gpt(text):
    """Use GPT-4 to intelligently extract invoice data from OCR text"""
    try:
        print("🤖 Using GPT-4 for intelligent invoice data extraction...")
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE')
        
        print(f"🔑 Debug - API Key exists: {bool(api_key)}")
        print(f"🔑 Debug - API Key prefix: {api_key[:10] if api_key else 'None'}...")
        print(f"🌐 Debug - Base URL: {base_url}")
        print(f"📋 Debug - Client config: {type(client)}")
        
        prompt = f"""
You are an expert at extracting invoice data from OCR text. Please analyze the following text and extract the key invoice information. The text might be messy from OCR, so use your intelligence to identify the correct values.

OCR Text:
{text}

Please extract and return ONLY a JSON object with these fields:
- invoice_id: The actual invoice number/ID (like "GALT-009", "INV-2023-001", etc.) - NOT words like "invoice" or "bill"
- vendor_name: The company/vendor name issuing the invoice
- amount: The total amount as a number (without $ symbol)
- date: The invoice date in YYYY-MM-DD format
- tax_id: Tax ID or EIN if present

Important rules:
1. For invoice_id: Look for actual ID numbers, not labels like "invoice" or "bill"
2. Return empty string "" if a field cannot be found
3. For amount: Only the numeric value, no currency symbols
4. For date: Convert to YYYY-MM-DD format
5. Return ONLY the JSON object, no explanations

Example format:
{{"invoice_id": "GALT-009", "vendor_name": "Fountainhead A+E", "amount": "11812.50", "date": "2013-08-01", "tax_id": ""}}
"""
        
        # Create a fresh client to ensure proper auth
        fresh_client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://localhost:8001",
                "X-Title": "Invoice Chain Agent"
            }
        )
        
        response = fresh_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert invoice data extraction assistant. Extract data accurately and return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        gpt_response = response.choices[0].message.content.strip()
        print(f"🧠 GPT-4 raw response: {gpt_response}")
        
        # Parse the JSON response
        try:
            # Clean up the response to extract just the JSON
            if '```json' in gpt_response:
                json_start = gpt_response.find('```json') + 7
                json_end = gpt_response.find('```', json_start)
                gpt_response = gpt_response[json_start:json_end].strip()
            elif '```' in gpt_response:
                json_start = gpt_response.find('```') + 3
                json_end = gpt_response.find('```', json_start)
                gpt_response = gpt_response[json_start:json_end].strip()
            
            extracted_data = json.loads(gpt_response)
            print(f"✅ GPT-4 extracted data: {extracted_data}")
            return extracted_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse GPT-4 JSON response: {e}")
            print(f"Raw response: {gpt_response}")
            return None
            
    except Exception as e:
        print(f"❌ GPT-4 extraction error: {e}")
        return None
def parse_invoice_from_text(text):
    """Parse invoice data from OCR text using GPT-4 first, then regex fallback"""
    print(f"🔍 Starting invoice data parsing...")
    
    # First try GPT-4 extraction
    gpt_data = extract_invoice_data_with_gpt(text)
    if gpt_data:
        # Validate GPT data and fill defaults
        invoice_data = {
            'invoice_id': gpt_data.get('invoice_id', ''),
            'vendor_name': gpt_data.get('vendor_name', ''),
            'tax_id': gpt_data.get('tax_id', ''),
            'amount': gpt_data.get('amount', ''),
            'date': gpt_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        }
        
        print(f"🤖 GPT-4 successfully extracted invoice data!")
        print(f"🎯 Final parsed data: {invoice_data}")
        return invoice_data
    
    # Fallback to regex-based extraction
    print("⚠️ GPT-4 extraction failed, falling back to regex patterns...")
    
    invoice_data = {
        'invoice_id': '',
        'vendor_name': '',
        'tax_id': '',
        'amount': '',
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    if not text:
        return invoice_data
    
    # Patterns for different invoice fields
    patterns = {
        'invoice_id': [
            # High-priority specific patterns
            r'invoice\s*#?\s*:?\s*([A-Z0-9\-_]+)',
            r'inv\s*#?\s*:?\s*([A-Z0-9\-_]+)',
            r'bill\s*#?\s*:?\s*([A-Z0-9\-_]+)',
            r'reference\s*#?\s*:?\s*([A-Z0-9\-_]+)',
            r'ref\s*#?\s*:?\s*([A-Z0-9\-_]+)',
            r'invoice\s+number\s*:?\s*([A-Z0-9\-_]+)',
            r'#\s*([A-Z0-9\-_]{3,})',
            # Medium-priority pattern-based detection
            r'([A-Z]{2,}[-_]\d+)',  # GALT-009, INV-123, COMP_001
            r'(\d{4}-\d{4})',  # 2012-0001
            r'([A-Z]+\d+[A-Z]*)',  # ABC123, INV001A (but only if 4+ chars)
        ],
        'amount': [
            r'\$\s*([0-9,]+\.?\d*)',
            r'total\s*:?\s*\$?\s*([0-9,]+\.?\d*)',
            r'amount\s*:?\s*\$?\s*([0-9,]+\.?\d*)',
            r'invoice\s+total\s*:?\s*\$?\s*([0-9,]+\.?\d*)',
            r'account\s+balance\s*:?\s*\$?\s*([0-9,]+\.?\d*)',
            r'balance\s+due\s*:?\s*\$?\s*([0-9,]+\.?\d*)',
            r'([0-9,]+\.\d{2})'
        ],
        'date': [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})',
            r'date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'invoice\s+date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(aug\s+\d{1,2},?\s+\d{4})',  # Aug 31, 2013 format
            r'(sep\s+\d{1,2},?\s+\d{4})',  # Sep 30, 2013 format
        ],
        'tax_id': [
            r'tax\s*id\s*:?\s*([0-9\-]+)',
            r'ein\s*:?\s*([0-9\-]+)',
            r'federal\s*id\s*:?\s*([0-9\-]+)'
        ]
    }
    
    # Extract vendor name (usually appears early in the text)
    lines = text.split('\n')
    for i, line in enumerate(lines[:10]):  # Check first 10 lines
        line = line.strip()
        if line and len(line) > 3 and not re.search(r'^\d+$', line):
            # Skip common header words
            skip_words = ['invoice', 'bill', 'receipt', 'date', 'amount', 'total', 'monthly', 'bill to', 'project']
            if not any(word in line.lower() for word in skip_words):
                # Check if it looks like a company name
                if any(indicator in line.lower() for indicator in ['inc', 'corp', 'ltd', 'llc', 'a+e', '&']):
                    invoice_data['vendor_name'] = line
                    break
                elif i == 0:  # First line fallback
                    invoice_data['vendor_name'] = line
                    break
    
    print(f"🏢 Extracted vendor name: '{invoice_data['vendor_name']}'")
    
    # Extract other fields using patterns
    text_lower = text.lower()
    
    for field, field_patterns in patterns.items():
        print(f"🔍 Searching for {field}...")
        
        if field == 'invoice_id':
            # Special handling for invoice ID - look for labels first
            found_id = None
            best_score = 0
            
            # Look for invoice ID labels and extract the value that follows
            invoice_labels = [
                r'invoice\s*#\s*:?\s*([A-Z0-9\-_]+)',
                r'invoice\s*id\s*:?\s*([A-Z0-9\-_]+)',
                r'invoice\s*number\s*:?\s*([A-Z0-9\-_]+)',
                r'inv\s*#\s*:?\s*([A-Z0-9\-_]+)',
                r'bill\s*#\s*:?\s*([A-Z0-9\-_]+)',
                r'reference\s*#\s*:?\s*([A-Z0-9\-_]+)',
                r'ref\s*#\s*:?\s*([A-Z0-9\-_]+)',
            ]
            
            # First try label-based detection (highest priority)
            for label_pattern in invoice_labels:
                match = re.search(label_pattern, text_lower, re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip()
                    print(f"   🎯 Found invoice ID by label: '{candidate}' using pattern '{label_pattern}'")
                    
                    # Skip obvious non-IDs
                    skip_words = ['billto', 'shipto', 'mailto', 'payto', 'from', 'to', 'date', 'amount', 'total']
                    if not any(skip in candidate.lower() for skip in skip_words):
                        found_id = candidate
                        best_score = 100  # Highest score for label-based matches
                        break
            
            # If no label-based match, try positional detection
            if not found_id:
                # Look for "invoice" followed by potential ID on next line or nearby
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    line_lower = line.lower().strip()
                    if any(keyword in line_lower for keyword in ['invoice id', 'invoice number', 'invoice #', 'inv #']):
                        # Check current line first
                        after_label = re.sub(r'.*(invoice\s*(id|number|#)|inv\s*#)\s*:?\s*', '', line_lower, flags=re.IGNORECASE)
                        if after_label and len(after_label.strip()) > 0:
                            potential_id = re.search(r'([A-Z0-9\-_]+)', after_label, re.IGNORECASE)
                            if potential_id:
                                found_id = potential_id.group(1).strip()
                                best_score = 90
                                print(f"   🎯 Found invoice ID on same line: '{found_id}'")
                                break
                        
                        # Check next line
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            potential_id = re.search(r'([A-Z0-9\-_]{3,})', next_line, re.IGNORECASE)
                            if potential_id:
                                candidate = potential_id.group(1).strip()
                                skip_words = ['billto', 'shipto', 'date', 'amount', 'total', 'from', 'to']
                                if not any(skip in candidate.lower() for skip in skip_words):
                                    found_id = candidate
                                    best_score = 85
                                    print(f"   🎯 Found invoice ID on next line: '{found_id}'")
                                    break
            
            # Fallback to pattern-based detection if still nothing found
            if not found_id:
                fallback_patterns = [
                    r'([A-Z]{2,}[-_]\d+)',  # GALT-009, INV-123
                    r'(\d{4}-\d{4})',       # 2012-0001
                ]
                
                for pattern in fallback_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        candidate = match.group(1).strip()
                        
                        # Basic validation
                        if 3 <= len(candidate) <= 15:
                            # Check context for invoice-related keywords
                            context_start = max(0, match.start() - 100)
                            context_end = min(len(text), match.end() + 100)
                            context = text[context_start:context_end].lower()
                            
                            if any(keyword in context for keyword in ['invoice', 'bill', 'receipt']):
                                found_id = candidate
                                best_score = 70
                                print(f"   🎯 Found invoice ID by pattern: '{found_id}'")
                                break
                    if found_id:
                        break
            
            if found_id:
                invoice_data[field] = found_id
                print(f"   ✅ Final invoice ID: '{found_id}' (score: {best_score})")
            else:
                print(f"   ❌ No valid invoice ID found")
            continue
        
        # Handle other fields normally
        for pattern in field_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                print(f"   ✅ Found {field}: '{value}' using pattern '{pattern}'")
                
                # Clean up the value
                if field == 'amount':
                    value = value.replace(',', '').replace('$', '')
                    try:
                        float(value)  # Validate it's a number
                        invoice_data[field] = value
                        print(f"   💰 Set {field} to: {value}")
                        break
                    except ValueError:
                        print(f"   ❌ Invalid number format: {value}")
                        continue
                elif field == 'date':
                    # Try to normalize date format
                    try:
                        # Convert to standard format
                        if '/' in value:
                            parts = value.split('/')
                        else:
                            parts = value.split('-')
                        
                        if len(parts) == 3:
                            if len(parts[2]) == 2:
                                parts[2] = '20' + parts[2]  # Assume 20xx for 2-digit years
                            
                            # Assume MM/DD/YYYY or DD/MM/YYYY format
                            if int(parts[0]) > 12:  # DD/MM/YYYY
                                normalized_date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                            else:  # MM/DD/YYYY
                                normalized_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                            
                            invoice_data[field] = normalized_date
                            print(f"   📅 Set {field} to: {normalized_date}")
                            break
                    except:
                        print(f"   ❌ Date parsing failed for: {value}")
                        continue
                else:
                    invoice_data[field] = value
                    print(f"   ✅ Set {field} to: {value}")
                    break
    
    print(f"🎯 Final parsed data: {invoice_data}")
    return invoice_data

def process_uploaded_invoice(image_file):
    """Complete pipeline: OCR + GPT-4 parsing"""
    try:
        print(f"🚀 Starting complete invoice processing pipeline with GPT-4...")
        
        # Extract text from image
        text = extract_text_from_image(image_file)
        
        if not text:
            return {
                'success': False,
                'error': 'Could not extract text from image'
            }
        
        print(f"📄 Full extracted text:\n{text}\n" + "="*60)
        
        # Parse invoice data (GPT-4 first, regex fallback)
        invoice_data = parse_invoice_from_text(text)
        
        print(f"🔍 Final parsed invoice data: {invoice_data}")
        
        # Check if we got meaningful data
        meaningful_fields = sum(1 for v in invoice_data.values() if v and str(v).strip())
        confidence = 'high' if meaningful_fields >= 4 else 'medium' if meaningful_fields >= 2 else 'low'
        
        print(f"✅ Processing complete. Meaningful fields: {meaningful_fields}, Confidence: {confidence}")
        
        return {
            'success': True,
            'extracted_text': text,
            'invoice_data': invoice_data,
            'confidence': confidence,
            'extraction_method': 'GPT-4 + OCR'
        }
        
    except Exception as e:
        print(f"❌ Complete pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }
