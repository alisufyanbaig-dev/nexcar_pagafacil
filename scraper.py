"""
Scraper module for Paga Fácil vehicle tax information.
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging
from captcha_solver import CaptchaSolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PagaFacilScraper:
    """Scraper for Paga Fácil vehicle tax website."""
    
    def __init__(self, proxy_host: str, proxy_port: int, proxy_username: str, proxy_password: str):
        """
        Initialize the scraper with proxy configuration.
        
        Args:
            proxy_host: Proxy server hostname
            proxy_port: Proxy server port
            proxy_username: Proxy authentication username
            proxy_password: Proxy authentication password
        """
        self.base_url = "https://www.pagafacil.gob.mx/pagafacilv2/epago/cv/"
        self.form_url = "control_vehicular_25.php"
        
        # Configure proxy
        self.proxies = {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
        }
        
        # Configure session
        self.session = requests.Session()
        self.session.proxies = self.proxies
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Initialize captcha solver
        self.captcha_solver = CaptchaSolver()

    def get_form_data(self) -> tuple:
        """
        Get the initial form data including any hidden fields or tokens, and solve captcha.
        
        Returns:
            Tuple of (form data dictionary, captcha image path)
        """
        try:
            url = urljoin(self.base_url, self.form_url)
            logger.info(f"Fetching form data from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Handle BOM and encoding issues
            content = response.content.decode('utf-8-sig', errors='ignore')
            # Try lxml parser which is more robust
            try:
                soup = BeautifulSoup(content, 'lxml')
            except:
                soup = BeautifulSoup(content, 'html.parser')
            
            # Debug: log page content size and forms found
            logger.info(f"Page size: {len(response.text)} characters")
            all_forms = soup.find_all('form')
            logger.info(f"Total forms found: {len(all_forms)}")
            
            # Find the main form (the one with plate and VIN inputs)
            form = soup.find('form', id='pide_placa')
            if not form:
                form = soup.find('form', class_='codigo')
            if not form:
                # Fallback: find any form with plate/VIN fields
                for f in all_forms:
                    if f.find('input', attrs={'name': re.compile(r'placa|vin|niv|numserie')}):
                        form = f
                        logger.info("Found form using fallback method")
                        break
                
            if not form:
                # Final debug: show what forms we did find
                for i, f in enumerate(all_forms):
                    logger.info(f"Form {i+1}: id={f.get('id')}, class={f.get('class')}")
                raise ValueError("Could not find vehicle form on page")
            
            form_data = {}
            captcha_image_path = None
            
            # Extract hidden fields
            for hidden_input in form.find_all('input', type='hidden'):
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
            
            # Extract other input fields with default values
            for input_field in form.find_all('input'):
                name = input_field.get('name')
                value = input_field.get('value', '')
                input_type = input_field.get('type', 'text')
                
                if name and input_type not in ['submit', 'button', 'reset']:
                    if name not in form_data:  # Don't override hidden fields
                        form_data[name] = value
            
            # Extract select fields
            for select_field in form.find_all('select'):
                name = select_field.get('name')
                if name:
                    selected_option = select_field.find('option', selected=True)
                    if selected_option:
                        form_data[name] = selected_option.get('value', '')
                    else:
                        # Get first option if none selected
                        first_option = select_field.find('option')
                        if first_option:
                            form_data[name] = first_option.get('value', '')
            
            # Look for captcha image
            captcha_imgs = soup.find_all('img', src=lambda x: x and ('captcha' in x.lower() or 'imagebuilder' in x.lower()))
            if captcha_imgs:
                captcha_image_path = captcha_imgs[0].get('src')
                logger.info(f"Found captcha image: {captcha_image_path}")
                
                # Also get the captcha hidden field from the captcha form
                captcha_form = soup.find('form', id='captcha_gen')
                if captcha_form:
                    captcha_hidden = captcha_form.find('input', attrs={'name': 'codigo_gen'})
                    if captcha_hidden:
                        form_data['codigo_gen'] = captcha_hidden.get('value', '')
                        logger.info("Added captcha hidden field to form data")
            
            logger.info(f"Form data extracted: {list(form_data.keys())}")
            return form_data, captcha_image_path
            
        except Exception as e:
            logger.error(f"Error getting form data: {str(e)}")
            raise

    def submit_vehicle_query(self, plate: str, vin: str) -> str:
        """
        Submit vehicle query to the form with captcha solving.
        
        Args:
            plate: License plate number
            vin: Vehicle Identification Number
            
        Returns:
            HTML response content
        """
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_attempts} to submit query for plate: {plate}, VIN: {vin}")
                
                # Get initial form data and captcha image path
                form_data, captcha_image_path = self.get_form_data()
                
                # Solve captcha if present
                if captcha_image_path:
                    logger.info("Captcha detected, attempting to solve...")
                    captcha_text = self.captcha_solver.get_multiple_attempts(
                        self.session, self.base_url, captcha_image_path, max_attempts=2
                    )
                    
                    if not captcha_text:
                        logger.warning(f"Failed to solve captcha on attempt {attempt + 1}")
                        if attempt < max_attempts - 1:
                            continue
                        else:
                            raise ValueError("Unable to solve captcha after multiple attempts")
                    
                    # Add captcha text to form data
                    form_data['codigo_usr'] = captcha_text
                    logger.info(f"Using captcha solution: {captcha_text}")
                else:
                    logger.info("No captcha detected")
                
                # Update form data with vehicle information
                # Based on the actual form fields found
                plate_fields = ['placa', 'placas', 'plate', 'license_plate', 'matricula']
                vin_fields = ['numserie', 'vin', 'niv', 'numero_identificacion', 'serie']
                
                # Try to find the correct field names
                plate_set = False
                for field in plate_fields:
                    if field in form_data:
                        form_data[field] = plate
                        plate_set = True
                        break
                
                if not plate_set:
                    # If no matching field found, try common patterns
                    form_data['placa'] = plate
                
                vin_set = False
                for field in vin_fields:
                    if field in form_data:
                        form_data[field] = vin
                        vin_set = True
                        break
                
                if not vin_set:
                    # If no matching field found, try common patterns - based on form analysis, use 'numserie'
                    form_data['numserie'] = vin
                    form_data['niv'] = vin
                
                # Submit form
                url = urljoin(self.base_url, self.form_url)
                response = self.session.post(url, data=form_data, timeout=30)
                response.raise_for_status()
                
                # Check if submission was successful (not a captcha error)
                response_text = response.text.lower()
                captcha_error_indicators = [
                    'codigo de seguridad incorrecto',
                    'captcha incorrecto',
                    'codigo incorrecto',
                    'verifique el codigo'
                ]
                
                if any(indicator in response_text for indicator in captcha_error_indicators):
                    logger.warning(f"Captcha validation failed on attempt {attempt + 1}")
                    if attempt < max_attempts - 1:
                        continue
                    else:
                        logger.error("All captcha attempts failed")
                        # Return the response anyway for error handling
                        return response.text
                
                logger.info(f"Successfully submitted form on attempt {attempt + 1}")
                return response.text
                
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    raise

    def parse_vehicle_info(self, html_content: str) -> Dict[str, Any]:
        """
        Parse vehicle information from HTML response.
        
        Args:
            html_content: HTML response from the form submission
            
        Returns:
            Dictionary containing parsed vehicle information
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for error messages
            error_patterns = [
                "no se encontró registro",
                "verifique los datos",
                "error",
                "no existe",
                "datos incorrectos"
            ]
            
            page_text = soup.get_text().lower()
            for pattern in error_patterns:
                if pattern in page_text:
                    return {
                        "codigo": "error",
                        "info": None,
                        "error": {
                            "mensaje": "Verifique los datos que ingreso, no se encontró registro de este vehículo."
                        }
                    }
            
            # Initialize result structure
            result = {
                "codigo": "ok",
                "info": [],
                "vehicle_info": {
                    "vin": "",
                    "make": "",
                    "model": "",
                    "description": "",
                    "year": "",
                    "color": ""
                }
            }
            
            # Parse vehicle information
            self._parse_vehicle_details(soup, result["vehicle_info"])
            
            # Parse tax information
            tax_info = self._parse_tax_info(soup)
            result["info"] = tax_info
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing vehicle info: {str(e)}")
            return {
                "codigo": "error",
                "info": None,
                "error": {
                    "mensaje": f"Error parsing response: {str(e)}"
                }
            }

    def _parse_vehicle_details(self, soup: BeautifulSoup, vehicle_info: Dict[str, str]) -> None:
        """Parse vehicle details from soup."""
        # Look for common patterns in vehicle information display
        
        # Try to find VIN
        vin_patterns = [r'VIN[:\s]*([A-Z0-9]{17})', r'NIV[:\s]*([A-Z0-9]{17})', r'SERIE[:\s]*([A-Z0-9]{17})']
        text_content = soup.get_text()
        
        for pattern in vin_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                vehicle_info["vin"] = match.group(1).strip()
                break
        
        # Look for year pattern
        year_match = re.search(r'\b(19|20)\d{2}\b', text_content)
        if year_match:
            vehicle_info["year"] = year_match.group(0)
            vehicle_info["model"] = year_match.group(0)
        
        # Look for vehicle description in tables or specific divs
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    header = cells[0].get_text().strip().lower()
                    value = cells[1].get_text().strip()
                    
                    if 'descripción' in header or 'vehiculo' in header or 'tipo' in header:
                        vehicle_info["description"] = value
                    elif 'marca' in header:
                        vehicle_info["make"] = value
                    elif 'color' in header:
                        vehicle_info["color"] = value
                    elif 'modelo' in header and not vehicle_info["model"]:
                        vehicle_info["model"] = value

    def _parse_tax_info(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse tax information from soup."""
        tax_info = []
        
        # Look for tax tables
        tables = soup.find_all('table')
        
        for table in tables:
            headers = []
            header_row = table.find('thead') or table.find('tr')
            if header_row:
                headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
            
            # Skip if this doesn't look like a tax table
            if not any(keyword in ' '.join(headers) for keyword in ['período', 'tenencia', 'refrendo', 'total', 'ejercicio']):
                continue
            
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                
                try:
                    # Extract period (year)
                    period_text = cells[0].get_text().strip()
                    period_match = re.search(r'\b(19|20)\d{2}\b', period_text)
                    if not period_match:
                        continue
                    
                    period = int(period_match.group(0))
                    
                    # Extract amounts
                    tenencia = 0.0
                    refrendo = 0.0
                    total = 0.0
                    
                    for i, cell in enumerate(cells[1:], 1):
                        amount_text = cell.get_text().strip()
                        amount_match = re.search(r'[\d,]+\.?\d*', amount_text.replace(',', ''))
                        if amount_match:
                            amount = float(amount_match.group(0))
                            
                            # Try to identify which column this is based on position or header
                            if i < len(headers):
                                header = headers[i].lower()
                                if 'tenencia' in header:
                                    tenencia = amount
                                elif 'refrendo' in header:
                                    refrendo = amount
                                elif 'total' in header:
                                    total = amount
                            else:
                                # Fallback: assume order is tenencia, refrendo, total
                                if i == 1:
                                    tenencia = amount
                                elif i == 2:
                                    refrendo = amount
                                elif i == 3:
                                    total = amount
                    
                    # Calculate total if not provided
                    if total == 0.0 and (tenencia > 0 or refrendo > 0):
                        total = tenencia + refrendo
                    
                    tax_entry = {
                        "periodo": period,
                        "tenencia": tenencia,
                        "refrendo": refrendo,
                        "total": total
                    }
                    
                    tax_info.append(tax_entry)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing tax row: {e}")
                    continue
        
        # Sort by period (most recent first)
        tax_info.sort(key=lambda x: x["periodo"], reverse=True)
        
        return tax_info

    def get_vehicle_info(self, plate: str, vin: str) -> Dict[str, Any]:
        """
        Get complete vehicle information including taxes.
        
        Args:
            plate: License plate number
            vin: Vehicle Identification Number
            
        Returns:
            Dictionary containing vehicle information and taxes
        """
        try:
            # Clean inputs
            plate = plate.strip().upper()
            vin = vin.strip().upper()
            
            logger.info(f"Getting vehicle info for plate: {plate}, VIN: {vin}")
            
            # Submit query and get response
            html_content = self.submit_vehicle_query(plate, vin)
            
            # Parse the response
            result = self.parse_vehicle_info(html_content)
            
            logger.info(f"Query result: {result['codigo']}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting vehicle info: {str(e)}")
            return {
                "codigo": "error",
                "info": None,
                "error": {
                    "mensaje": f"Error processing request: {str(e)}"
                }
            }