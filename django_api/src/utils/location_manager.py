import requests
from unidecode import unidecode
import logging
from fuzzywuzzy import fuzz

# Fallback data in case API fails
FALLBACK_MUNICIPIOS = [
    "Lisboa", "Amadora", "Cascais", "Loures", 
    "Odivelas", "Oeiras", "Sintra"
]

class LocationManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.freguesias = []
            self.municipios = []
            self.freguesias_normalized = []
            self.municipios_normalized = []
            self._initialize_location_data()
            LocationManager._initialized = True

    def _initialize_location_data(self):
        """Initialize freguesia and município data from GeoAPI"""
        try:
            # Fetch data from GeoAPI with timeout
            freguesias_response = requests.get('https://json.geoapi.pt/distrito/lisboa/freguesias', timeout=10)
            
            if freguesias_response.ok:
                response_data = freguesias_response.json()
                
                # Extract freguesias and municipios from the correct response structure
                self.freguesias = []
                self.municipios = set()
                
                # Extract freguesias directly from the response_data['freguesias']
                if 'freguesias' in response_data and response_data['freguesias']:
                    self.freguesias = response_data['freguesias']
                else:
                    self.logger.warning("No freguesias found in API response, using empty list")
                
                # Extract municipios from the response_data['municipios'] 
                if 'municipios' in response_data and response_data['municipios']:
                    for municipio in response_data['municipios']:
                        if isinstance(municipio, dict):
                            municipio_name = municipio.get('nome', '')
                            if municipio_name:
                                self.municipios.add(municipio_name)
                
                # If no municipios found, use fallback data
                if not self.municipios:
                    self.logger.warning("No municipios found in API response, using fallback data")
                    self.municipios = set(FALLBACK_MUNICIPIOS)
                
                # Convert municipios set to sorted list
                self.municipios = sorted(list(self.municipios))
                
                # Create normalized lists for matching
                try:
                    self.freguesias_normalized = [unidecode(str(f).lower()) for f in self.freguesias]
                    self.municipios_normalized = [unidecode(str(m).lower()) for m in self.municipios]
                except Exception as e:
                    self.logger.error(f"Error during normalization: {str(e)}")
                    raise
                
                self.logger.info(f"Successfully loaded {len(self.freguesias)} freguesias and {len(self.municipios)} municipios")
                
            else:
                self.logger.error(f"API request failed with status code: {freguesias_response.status_code}")
                self.logger.error(f"API response content: {freguesias_response.text}")
                self.logger.warning("Using fallback data for municipios")
                self.municipios = FALLBACK_MUNICIPIOS
                self.municipios_normalized = [unidecode(str(m).lower()) for m in self.municipios]
                
        except (requests.RequestException, Exception) as e:
            self.logger.error(f"Error initializing location data: {str(e)}", exc_info=True)
            self.logger.warning("Using fallback data for municipios")
            self.municipios = FALLBACK_MUNICIPIOS
            self.municipios_normalized = [unidecode(str(m).lower()) for m in self.municipios]
            self.freguesias = []
            self.freguesias_normalized = []

    def extract_location(self, location_str):
        """
        Extract freguesia and município from a location string
        Returns tuple (freguesia, município)
        """
        try:
            if not location_str or location_str.strip() in ["N/A", "-"]:
                return None, None
                
            # Normalize and split the input string
            location_parts = [
                part.strip() 
                for part in unidecode(location_str.lower()).split(',')
                if not part.strip().startswith('rua')
            ]
            
            best_freguesia = None
            best_municipio = None
            
            # Try to match each part from left to right
            for part in location_parts:
                # Try freguesia match first
                if not best_freguesia:
                    for idx, freguesia in enumerate(self.freguesias_normalized):
                        ratio = fuzz.partial_ratio(part, freguesia)
                        if ratio > 85:
                            best_freguesia = self.freguesias[idx]
                            break
                            
                # Try municipio match if no freguesia found yet
                if not best_municipio:
                    for idx, municipio in enumerate(self.municipios_normalized):
                        ratio = fuzz.partial_ratio(part, municipio)
                        if ratio > 85:
                            best_municipio = self.municipios[idx]
                            break
                            
                if best_freguesia and best_municipio:
                    break
                    
            self.logger.debug(f"Location match for '{location_str}': Freguesia='{best_freguesia}', Município='{best_municipio}'")
            
            return best_freguesia, best_municipio
            
        except Exception as e:
            self.logger.error(f"Error extracting location data: {str(e)}", exc_info=True)
            return None, None

    def get_location_data(self):
        """Get the location data"""
        return {
            'freguesias': self.freguesias,
            'municipios': list(self.municipios),
            'freguesias_normalized': self.freguesias_normalized,
            'municipios_normalized': self.municipios_normalized
        } 