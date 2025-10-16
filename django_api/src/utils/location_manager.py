import logging
from fuzzywuzzy import fuzz
from unidecode import unidecode

# Note: For simplification terms of our app, the district is always Lisboa
DEFAULT_DISTRICT = "Lisboa"

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
            self.parishes = []
            self.counties = []
            self.districts = []
            self._initialize_location_data()
            LocationManager._initialized = True

    def _initialize_location_data(self):
        """Initialize parish, county and district data from database models"""
        try:
            # Import Django models here to avoid circular imports
            from houses.models import District, County, Parish
            
            # Get Lisboa district (our default district)
            self.districts = [{"id": None, "name": unidecode(DEFAULT_DISTRICT.lower())}]
            try:
                lisboa_district = District.objects.get(name=DEFAULT_DISTRICT)
                self.districts = [{"id": lisboa_district.id, "name": unidecode(str(lisboa_district.name).lower())}]
            except District.DoesNotExist:
                pass
            
            # Get all counties in Lisboa district
            counties = County.objects.filter(district__name=DEFAULT_DISTRICT).values('id', 'name')
            self.counties = [{"id": c['id'], "name": unidecode(str(c['name']).lower())} for c in counties]
            
            # Get all parishes in Lisboa district counties
            parishes = Parish.objects.filter(county__district__name=DEFAULT_DISTRICT).values('id', 'name')
            self.parishes = [{"id": p['id'], "name": unidecode(str(p['name']).lower())} for p in parishes]
            
            self.logger.info(f"Successfully loaded {len(self.parishes)} parishes and {len(self.counties)} counties from database")
            
        except ImportError as e:
            self.logger.error(f"Error importing Django models: {str(e)}")
            self.parishes = []
            self.counties = []
            self.districts = [{"id": None, "name": unidecode(DEFAULT_DISTRICT.lower())}]
            
        except Exception as e:
            self.logger.error(f"Error initializing location data from database: {str(e)}", exc_info=True)
            self.parishes = []
            self.counties = []
            self.districts = [{"id": None, "name": unidecode(DEFAULT_DISTRICT.lower())}]

    def extract_location(self, location_str):
        """
        Extract parish, county and district IDs from a location string
        Returns tuple (parish_id, county_id, district_id)
        Note: For simplification, district is always Lisboa
        """
        try:
            ## log the input location string
            self.logger.info(f"Extracting location from string: '{location_str}'")
            if not location_str or location_str.strip() in ["N/A", "-"]:
                district_id = self.districts[0]["id"] if self.districts else None
                return None, None, district_id
                
            # Normalize and split the input string
            location_parts = [
                part.strip() 
                for part in unidecode(location_str.lower()).split(',')
                if not part.strip().startswith('rua')
            ]
            
            best_parish_id = None
            best_county_id = None
            
            # Try to match each part from left to right
            for part in location_parts:
                # Try parish match first
                if not best_parish_id:
                    for parish in self.parishes:
                        ratio = fuzz.partial_ratio(part, parish["name"])
                        if ratio > 85:
                            best_parish_id = parish["id"]
                            break
                            
                # Try county match if no parish found yet
                if not best_county_id:
                    for county in self.counties:
                        ratio = fuzz.partial_ratio(part, county["name"])
                        if ratio > 85:
                            best_county_id = county["id"]
                            break
                            
                if best_parish_id and best_county_id:
                    break
            
            district_id = self.districts[0]["id"] if self.districts else None
            self.logger.debug(f"Location match for '{location_str}': Parish_ID='{best_parish_id}', County_ID='{best_county_id}', District_ID='{district_id}'")
            
            return best_parish_id, best_county_id, district_id
            
        except Exception as e:
            self.logger.error(f"Error extracting location data: {str(e)}", exc_info=True)
            district_id = self.districts[0]["id"] if self.districts else None
            return None, None, district_id

    def get_location_data(self):
        """Get the location data"""
        return {
            'parishes': self.parishes,
            'counties': self.counties,
            'districts': self.districts
        } 