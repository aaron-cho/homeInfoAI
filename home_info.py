import os
from dataclasses import dataclass
from typing import List, Optional
from openai import OpenAI
import re
from dotenv import load_dotenv

@dataclass
class School:
    name: str
    distance: float
    rating: Optional[float]
    type: str  # elementary, middle, high

@dataclass
class PropertyDetails:
    square_feet: Optional[float]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    estimated_value: Optional[float]
    year_built: Optional[int]

@dataclass
class HomeInformation:
    address: str
    overview: str
    details: PropertyDetails
    nearby_schools: List[School]

class AddressValidator:
    @staticmethod
    def validate_street(street: str) -> bool:
        """Validates street address format"""
        if not street or len(street.strip()) < 5 or len(street) > 100:
            return False
        pattern = r'\d+.*\b[A-Za-z]+\b.*(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr)\b.*'
        return bool(re.match(pattern, street.lower()))
    
    @staticmethod
    def validate_city(city: str) -> bool:
        """Validates city name"""
        return bool(city and len(city) <= 50 and all(c.isalpha() or c.isspace() for c in city))
    
    @staticmethod
    def validate_state(state: str) -> bool:
        """Validates US state code"""
        valid_states = {'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                       'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
                       'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
                       'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
                       'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'}
        return bool(state and len(state) == 2 and state.isalpha() and state.upper() in valid_states)
    
    @staticmethod
    def validate_zipcode(zipcode: str) -> bool:
        """Validates US ZIP code"""
        return bool(re.match(r'^\d{5}(?:-\d{4})?$', zipcode))

class HomeInfoRetriever:
    def __init__(self):
        """Initialize the HomeInfoRetriever with OpenAI API key from .env file"""
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.client = OpenAI(api_key=api_key)

    def get_home_information(self, address: str) -> HomeInformation:
        """Retrieve comprehensive information about the home address"""
        try:
            overview = self._get_property_overview(address)
            details = self._get_property_details(address)
            schools = self._get_nearby_schools(address)
            
            return HomeInformation(
                address=address,
                overview=overview,
                details=details,
                nearby_schools=schools
            )
        except Exception as e:
            raise Exception(f"Error retrieving home information: {str(e)}")

    def _get_property_overview(self, address: str) -> str:
        """Get an AI-generated overview of the property"""
        prompt = f"Provide a brief overview of the property at {address}. Include notable features and characteristics."
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a knowledgeable real estate expert."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _get_property_details(self, address: str) -> PropertyDetails:
        """Get detailed property information"""
        try:
            prompt = f"Provide detailed information about the property at {address} in the following format:\n"
            prompt += "Square Feet: [number]\nBedrooms: [number]\nBathrooms: [number]\n"
            prompt += "Estimated Value: [number in USD]\nYear Built: [year]"

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "You are a real estate database. Respond with only the requested format."},
                    {"role": "user", "content": prompt}
                ]
            )

            details_text = response.choices[0].message.content

            square_feet = float(re.search(r'Square\s*Feet:?\s*(\d[\d,]*)', details_text, re.IGNORECASE).group(1).replace(',', ''))
            bedrooms = int(re.search(r'Bedrooms?:?\s*(\d+)', details_text, re.IGNORECASE).group(1))
            bathrooms = float(re.search(r'Bathrooms?:?\s*(\d+\.?\d*)', details_text, re.IGNORECASE).group(1))
            estimated_value = float(re.search(r'Estimated\s*Value:?\s*\$?\s*(\d[\d,]*)', details_text, re.IGNORECASE).group(1).replace(',', ''))
            year_built = int(re.search(r'Year\s*Built:?\s*(\d{4})', details_text, re.IGNORECASE).group(1))

            return PropertyDetails(
                square_feet=square_feet,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                estimated_value=estimated_value,
                year_built=year_built
            )
        except (AttributeError, ValueError):
            return PropertyDetails(
                square_feet=None,
                bedrooms=None,
                bathrooms=None,
                estimated_value=None,
                year_built=None
            )

    def _get_nearby_schools(self, address: str) -> List[School]:
        """Get information about nearby schools"""
        try:
            prompt = f"List 3 nearby schools for {address}. For each school, provide:\n"
            prompt += "Name: [school name]\nDistance: [number] miles\nRating: [number]/10\nType: [elementary school/middle school/high school]"

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "You are a school information database. List exactly 3 schools in the exact format specified."},
                    {"role": "user", "content": prompt}
                ]
            )

            schools = []
            school_text = response.choices[0].message.content
            
            school_entries = [entry.strip() for entry in school_text.split('\n\n') if entry.strip()]
            
            for entry in school_entries:
                try:
                    name_match = re.search(r'Name:\s*([^\n]+)', entry, re.IGNORECASE)
                    distance_match = re.search(r'Distance:\s*(\d+\.?\d*)', entry, re.IGNORECASE)
                    rating_match = re.search(r'Rating:\s*(\d+\.?\d*)', entry, re.IGNORECASE)
                    type_match = re.search(r'Type:\s*(elementary school|middle school|high school)', entry, re.IGNORECASE)

                    if all([name_match, distance_match, rating_match, type_match]):
                        schools.append(School(
                            name=name_match.group(1).strip(),
                            distance=float(distance_match.group(1)),
                            rating=float(rating_match.group(1)),
                            type=type_match.group(1).lower()
                        ))
                except (AttributeError, ValueError):
                    continue

            return schools or []
        except Exception:
            return []

def main():
    """Main function to execute program"""
    try:
        retriever = HomeInfoRetriever()
        
        while True:
            street = input("Enter street address (e.g., 123 Main Street): ").strip()
            if AddressValidator.validate_street(street):
                break
            print("Invalid street address format. Please try again.")
        
        while True:
            city = input("Enter city: ").strip()
            if AddressValidator.validate_city(city):
                break
            print("Invalid city name. Please try again.")
        
        while True:
            state = input("Enter state (2-letter code): ").strip().upper()
            if AddressValidator.validate_state(state):
                break
            print("Invalid state code. Please enter a valid US state code (e.g., CA).")
        
        while True:
            zipcode = input("Enter ZIP code: ").strip()
            if AddressValidator.validate_zipcode(zipcode):
                break
            print("Invalid ZIP code. Please enter a 5-digit ZIP code.")
        
        full_address = f"{street}, {city}, {state} {zipcode}"
        
        home_info = retriever.get_home_information(full_address)
        
        print("\nProperty Overview:")
        print(home_info.overview)
        
        print("\nProperty Details:")
        print(f"Square Feet: {home_info.details.square_feet}")
        print(f"Bedrooms: {home_info.details.bedrooms}")
        print(f"Bathrooms: {home_info.details.bathrooms}")
        print(f"Estimated Value: ${home_info.details.estimated_value:,.2f}")
        print(f"Year Built: {home_info.details.year_built}")
        
        print("\nNearby Schools:")
        for school in home_info.nearby_schools:
            print(f"{school.name} ({school.type})")
            print(f"  Distance: {school.distance} miles")
            print(f"  Rating: {school.rating}/10")
            print()

    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()