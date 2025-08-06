# ICP Blockchain Integration Module
import subprocess
import json
import asyncio
import os
import time
import hashlib
from typing import Dict, Any, Optional

class BlockchainIntegration:
    """
    ICP Canister integration for invoice validation and storage.
    Real integration only - no simulation data.
    """
    
    def __init__(self):
        self.canister_id = os.getenv("CANISTER_ID", "uxrrr-q7777-77774-qaaaq-cai")
        self.network = os.getenv("ICP_NETWORK", "local")
        self.dfx_path = os.getenv("DFX_PATH", "dfx")
        
        print(f"🔧 BlockchainIntegration initialized:")
        print(f"   Canister ID: {self.canister_id}")
        print(f"   Network: {self.network}")
        print(f"   DFX Path: {self.dfx_path}")
    
    def log_invoice(self, audit_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log invoice to ICP blockchain with enhanced validation data
        """
        try:
            # Extract invoice data
            invoice_data = audit_record.get('invoice_data', {})
            validation_result = audit_record.get('validation_result', {})
            status = audit_record.get('status', 'unknown')
            explanation = audit_record.get('explanation', 'No explanation provided')
            
            # Calculate enhanced metrics for chat agent
            validation_score = validation_result.get('score', 0)
            risk_score = self._calculate_risk_score(validation_result)
            fraud_risk = self._assess_fraud_level(validation_result)
            
            print(f"🚀 Logging invoice {invoice_data.get('invoice_id')} to ICP...")
            
            result = self._call_canister_dfx(
                "storeInvoice",
                {
                    "id": invoice_data.get("invoice_id", ""),
                    "vendor_name": invoice_data.get("vendor_name", ""),
                    "tax_id": invoice_data.get("tax_id", ""),
                    "amount": float(invoice_data.get("amount", 0)),
                    "date": invoice_data.get("date", ""),
                    "status": status,
                    "explanation": explanation,
                    "blockchain_hash": None,
                    "riskScore": risk_score,
                    "validationScore": validation_score,
                    "fraudRisk": fraud_risk
                }
            )
            
            print(f"🔍 Canister Call Result: {result}")
            
            if result.get('success'):
                # Verify the invoice was stored
                verification = self._verify_invoice_stored(invoice_data.get('invoice_id'))
                return {
                    "success": True,
                    "message": f"Invoice {invoice_data.get('invoice_id')} logged to ICP canister",
                    "canister_id": self.canister_id,
                    "network": self.network,
                    "verification": verification,
                    "response": result.get('response')
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown error'),
                    "message": "Failed to log invoice to ICP canister"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _call_canister_dfx(self, method: str, invoice_data: dict) -> Dict[str, Any]:
        """
        Call ICP canister using dfx CLI
        """
        try:
            # Build the proper Candid arguments based on method
            if method == "storeInvoice":
                # Sanitize explanation text to avoid bash issues
                explanation = invoice_data.get("explanation", "").replace('"', '\\"').replace('\n', ' ').replace(')', '\\)')
                explanation = explanation[:200]  # Truncate to avoid command line length issues
                
                # Extract validation data with defaults
                risk_score = invoice_data.get("riskScore", invoice_data.get("risk_score", 0))
                validation_score = invoice_data.get("validationScore", invoice_data.get("validation_score", 0))
                fraud_risk = invoice_data.get("fraudRisk", invoice_data.get("fraud_risk", "UNKNOWN"))
                
                # All 10 required parameters for storeInvoice
                candid_args = f'("{invoice_data.get("id", "")}", "{invoice_data.get("vendor_name", "")}", "{invoice_data.get("tax_id", "")}", {invoice_data.get("amount", 0)}, "{invoice_data.get("date", "")}", "{invoice_data.get("status", "")}", "{explanation}", null, {risk_score}, {validation_score}, "{fraud_risk}")'
            elif method == "getAllInvoices":
                candid_args = "()"
            elif method == "getInvoice":
                candid_args = f'("{invoice_data.get("id", "")}")'
            else:
                # For other methods, use generic format
                candid_args = f'("{invoice_data.get("id", "")}")'
            
            # Build the dfx command for WSL using proper bash syntax
            cmd = [
                "wsl", "bash", "-c", 
                f"source ~/.local/share/dfx/env && cd /mnt/c/Users/User/Documents/GitHub/invoice-chain-agent/canister && dfx canister call --network {self.network} {self.canister_id} {method} '{candid_args}'"
            ]
            
            print(f"🔗 Calling ICP canister via dfx: {method}")
            print(f"🔧 Command: {' '.join(cmd)}")
            
            # Execute the command - remove the cwd parameter since we're using absolute paths in the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print(f"📤 Return code: {result.returncode}")
            print(f"📝 STDOUT: '{result.stdout}'")
            print(f"📝 STDOUT length: {len(result.stdout)}")
            if result.stderr:
                print(f"⚠️ STDERR: '{result.stderr}'")
            
            if result.returncode == 0:
                response_content = result.stdout.strip()
                print(f"🔍 Cleaned response: '{response_content}'")
                print(f"🔍 Response length after strip: {len(response_content)}")
                
                return {
                    "success": True,
                    "response": response_content,
                    "method": "dfx_local",
                    "canister_output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"dfx call failed: {result.stderr}",
                    "return_code": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "dfx call timed out (30s)"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "dfx command not found - please install dfx CLI"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _verify_invoice_stored(self, invoice_id: str) -> str:
        """
        Verify that an invoice was actually stored in the canister
        """
        try:
            # Add delay to allow for blockchain state propagation
            time.sleep(1.5)
            
            # Use getAllInvoices to verify storage using the corrected format
            cmd = [
                "wsl", "bash", "-c", 
                f"source ~/.local/share/dfx/env && cd /mnt/c/Users/User/Documents/GitHub/invoice-chain-agent/canister && dfx canister call --network {self.network} {self.canister_id} getAllInvoices '()'"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                # Check if our invoice ID appears in the output
                if f'id = "{invoice_id}"' in output:
                    return "✅ verified_in_canister"
                else:
                    return f"⚠️ not_found_in_canister_list (searched for: {invoice_id})"
            else:
                return f"⚠️ verification_cmd_failed: rc={result.returncode}, stderr={result.stderr}"
                
        except Exception as e:
            return f"⚠️ verification_failed: {str(e)}"
    
    def get_invoice_by_id(self, invoice_id: str) -> Dict[str, Any]:
        """Get specific invoice from ICP canister"""
        try:
            print(f"🔍 Querying ICP canister for invoice: {invoice_id}")
            
            # Call the canister
            result = self._call_canister_dfx("getInvoice", {"id": invoice_id})
            
            if result.get("success") and result.get("response"):
                # Parse the canister response
                invoice_data = self._parse_canister_invoice_response(result["response"])
                if invoice_data:
                    return {
                        "success": True,
                        "invoice": invoice_data,
                        "source": "icp_canister"
                    }
            
            return {"success": False, "error": "Invoice not found in canister"}
            
        except Exception as e:
            print(f"❌ Error querying invoice {invoice_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_all_invoices(self) -> Dict[str, Any]:
        """Get all invoices from ICP canister"""
        try:
            print("📊 Querying ICP canister for all invoices...")
            
            result = self._call_canister_dfx("getAllInvoices", {})
            
            print(f"🔍 Canister call result: {result}")
            
            if result.get("success") and result.get("response"):
                print(f"🔍 Got successful response, parsing...")
                invoices = self._parse_canister_invoices_response(result["response"])
                print(f"🔍 Parsed {len(invoices)} invoices")
                return {
                    "success": True,
                    "invoices": invoices,
                    "count": len(invoices),
                    "source": "icp_canister"
                }
            
            print(f"❌ Call failed or empty response: success={result.get('success')}, response='{result.get('response')}'")
            return {"success": False, "error": f"Failed to retrieve invoices from canister: {result.get('error', 'Unknown error')}"}
            
        except Exception as e:
            print(f"❌ Error querying all invoices: {e}")
            return {"success": False, "error": str(e)}

    def _parse_canister_invoice_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse canister response for single invoice"""
        try:
            print(f"📥 Raw canister response for single invoice: {response}")
            
            # Handle both opt record and direct record formats
            if "opt record {" in response:
                # Extract the record content from opt record format
                start = response.find("opt record {") + len("opt record {")
                brace_count = 1
                record_end = start
                
                for i, char in enumerate(response[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            record_end = i
                            break
                
                if record_end > start:
                    record_content = response[start:record_end]
                    invoice = self._parse_invoice_fields(record_content)
                    if invoice.get('id'):
                        return invoice
                        
            elif "record {" in response:
                # Direct record format (same as list parsing)
                start = response.find("record {") + len("record {")
                brace_count = 1
                record_end = start
                
                for i, char in enumerate(response[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            record_end = i
                            break
                
                if record_end > start:
                    record_content = response[start:record_end]
                    invoice = self._parse_invoice_fields(record_content)
                    if invoice.get('id'):
                        return invoice
            
            print("❌ No parseable record found in response")
            return None
            
        except Exception as e:
            print(f"❌ Error parsing single invoice response: {e}")
            return None

    def _parse_invoice_fields(self, record_content: str) -> Dict[str, Any]:
        """Parse individual invoice fields from record content"""
        import re
        
        invoice = {}
        
        # Parse individual fields with improved patterns
        field_patterns = {
            'id': r'id\s*=\s*"([^"]+)"',
            'status': r'status\s*=\s*"([^"]+)"',
            'vendor_name': r'vendor_name\s*=\s*"([^"]*)"',
            'validationScore': r'validationScore\s*=\s*(\d+)',
            'riskScore': r'riskScore\s*=\s*(\d+)',
            'fraudRisk': r'fraudRisk\s*=\s*"([^"]*)"',
            'amount': r'amount\s*=\s*([0-9.]+)',
            'timestamp': r'timestamp\s*=\s*([0-9_]+)',
            'date': r'date\s*=\s*"([^"]*)"',
            'tax_id': r'tax_id\s*=\s*"([^"]*)"'
        }
        
        for field, pattern in field_patterns.items():
            match = re.search(pattern, record_content)
            if match:
                value = match.group(1)
                # Convert numeric fields
                if field in ['validationScore', 'riskScore']:
                    invoice[field] = int(value) if value else 0
                elif field == 'amount':
                    invoice[field] = float(value) if value else 0.0
                elif field == 'timestamp':
                    # Remove underscores from Motoko Int format
                    clean_timestamp = value.replace('_', '') if value else '0'
                    invoice[field] = int(clean_timestamp)
                else:
                    invoice[field] = value
        
        print(f"✅ Parsed invoice fields: {invoice}")
        return invoice

    def _parse_canister_invoices_response(self, response: str) -> list:
        """Parse canister response for invoice list"""
        try:
            print(f"📥 Raw canister response: {response}")
            
            # Basic parsing for Motoko response format
            # The response contains 'vec { record { ... } }' format
            invoices = []
            
            if "vec {" in response:
                # Much simpler approach - split by record boundaries
                import re
                
                # Find all individual records more reliably
                # Look for patterns like: record { ... } (handling nested braces)
                parts = response.split('record {')
                
                for i, part in enumerate(parts):
                    if i == 0:  # Skip the first part (before first record)
                        continue
                        
                    # Find the end of this record by counting braces
                    brace_count = 1
                    record_end = 0
                    
                    for j, char in enumerate(part):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                record_end = j
                                break
                    
                    if record_end > 0:
                        record_content = part[:record_end]
                        invoice = {}
                        
                        # Parse individual fields with simpler patterns
                        field_patterns = {
                            'id': r'id\s*=\s*"([^"]+)"',
                            'status': r'status\s*=\s*"([^"]+)"',
                            'vendor_name': r'vendor_name\s*=\s*"([^"]*)"',
                            'validationScore': r'validationScore\s*=\s*(\d+)',
                            'riskScore': r'riskScore\s*=\s*(\d+)',
                            'fraudRisk': r'fraudRisk\s*=\s*"([^"]*)"',
                            'amount': r'amount\s*=\s*([0-9.]+)',
                            'timestamp': r'timestamp\s*=\s*([0-9_]+)',
                            'date': r'date\s*=\s*"([^"]*)"',
                            'tax_id': r'tax_id\s*=\s*"([^"]*)"'
                        }
                        
                        for field, pattern in field_patterns.items():
                            match = re.search(pattern, record_content)
                            if match:
                                value = match.group(1)
                                # Convert numeric fields
                                if field in ['validationScore', 'riskScore']:
                                    invoice[field] = int(value) if value else 0
                                elif field == 'amount':
                                    invoice[field] = float(value) if value else 0.0
                                elif field == 'timestamp':
                                    # Remove underscores from Motoko Int format
                                    clean_timestamp = value.replace('_', '') if value else '0'
                                    invoice[field] = int(clean_timestamp)
                                else:
                                    invoice[field] = value
                        
                        # Only add if we got an ID
                        if invoice.get('id'):
                            invoices.append(invoice)
                            print(f"✅ Parsed invoice: {invoice.get('id')} - {invoice}")
            
            print(f"📊 Successfully parsed {len(invoices)} invoices")
            return invoices
            
        except Exception as e:
            print(f"❌ Error parsing canister response: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _calculate_risk_score(self, validation_result: Dict[str, Any]) -> int:
        """Calculate risk score (0-100) from validation result"""
        try:
            score = validation_result.get('score', 0)
            # Invert score for risk (high validation score = low risk score)
            risk_score = max(0, 100 - score)
            return min(100, risk_score)
        except:
            return 50  # Default medium risk

    def _assess_fraud_level(self, validation_result: Dict[str, Any]) -> str:
        """Assess fraud risk level based on validation result"""
        try:
            score = validation_result.get('score', 0)
            fraud_flags = validation_result.get('fraud_flags', [])
            
            if score < 50 or len(fraud_flags) >= 3:
                return "HIGH"
            elif score < 75 or len(fraud_flags) >= 1:
                return "MEDIUM"
            else:
                return "LOW"
        except:
            return "UNKNOWN"

    async def submit_to_blockchain(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit invoice to ICP Canister"""
        try:
            # Prepare the dfx command to call the canister
            cmd = [
                self.dfx_path,
                "canister",
                "call",
                "--network", self.network,
                self.canister_id,
                "storeInvoice",
                f'("{invoice_data.get("invoice_id", "")}", "{invoice_data.get("vendor_name", "")}", "{invoice_data.get("tax_id", "")}", {invoice_data.get("amount", 0)}, "{invoice_data.get("date", "")}", "approved", "Validated and approved", null)'
            ]
            
            # Execute the command
            result = await self._run_dfx_command(cmd)
            
            if result["success"]:
                return {
                    "success": True,
                    "canister_id": self.canister_id,
                    "network": self.network,
                    "message": "Invoice successfully stored on ICP",
                    "result": result["output"]
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "message": "Failed to store invoice on ICP"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error connecting to ICP Canister"
            }
    
    async def get_invoice_from_blockchain(self, invoice_id: str) -> Dict[str, Any]:
        """Retrieve invoice from ICP Canister"""
        try:
            cmd = [
                self.dfx_path,
                "canister",
                "call",
                "--network", self.network,
                self.canister_id,
                "getInvoice",
                f'("{invoice_id}")'
            ]
            
            result = await self._run_dfx_command(cmd)
            
            if result["success"]:
                return {
                    "success": True,
                    "invoice": result["output"],
                    "canister_id": self.canister_id
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_audit_logs(self, invoice_id: str) -> Dict[str, Any]:
        """Get audit logs for an invoice from ICP Canister"""
        try:
            cmd = [
                self.dfx_path,
                "canister",
                "call",
                "--network", self.network,
                self.canister_id,
                "getAuditLogs",
                f'("{invoice_id}")'
            ]
            
            result = await self._run_dfx_command(cmd)
            
            if result["success"]:
                return {
                    "success": True,
                    "logs": result["output"],
                    "canister_id": self.canister_id
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get invoice statistics from ICP Canister"""
        try:
            cmd = [
                self.dfx_path,
                "canister",
                "call",
                "--network", self.network,
                self.canister_id,
                "getStats"
            ]
            
            result = await self._run_dfx_command(cmd)
            
            if result["success"]:
                return {
                    "success": True,
                    "stats": result["output"],
                    "canister_id": self.canister_id
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the ICP Canister is healthy"""
        try:
            cmd = [
                self.dfx_path,
                "canister",
                "call",
                "--network", self.network,
                self.canister_id,
                "health"
            ]
            
            result = await self._run_dfx_command(cmd)
            
            if result["success"]:
                return {
                    "success": True,
                    "health": result["output"],
                    "canister_id": self.canister_id,
                    "network": self.network
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_dfx_command(self, cmd: list) -> Dict[str, Any]:
        """Run dfx command asynchronously"""
        try:
            # Change to canister directory if it exists
            canister_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "canister")
            if os.path.exists(canister_dir):
                original_dir = os.getcwd()
                os.chdir(canister_dir)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Restore original directory
            if os.path.exists(canister_dir):
                os.chdir(original_dir)
            
            if process.returncode == 0:
                output = stdout.decode().strip()
                return {"success": True, "output": output}
            else:
                error = stderr.decode().strip()
                return {"success": False, "error": error}
                
        except FileNotFoundError:
            return {
                "success": False, 
                "error": f"dfx not found. Please install dfx CLI from https://internetcomputer.org/docs/current/developer-docs/setup/install/"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
