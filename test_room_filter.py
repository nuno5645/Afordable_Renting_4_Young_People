#!/usr/bin/env python
# coding: utf-8

import logging
from config.settings import (
    ROOM_RENTAL_TITLE_TERMS,
    ROOM_RENTAL_DESCRIPTION_TERMS
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_room_filter():
    """Test the room rental filtering logic"""
    try:
        logger.info("Testing room rental filtering...")
        
        # Test cases - titles that should be filtered
        room_titles = [
            "QUARTO em Lisboa para estudante",
            "Room for rent in Lisbon",
            "Aluga-se quarto em apartamento T3",
            "ALUGO QUARTO em Arroios",
            "Quarto para alugar em Benfica"
        ]
        
        # Test cases - titles that should NOT be filtered
        apartment_titles = [
            "Apartamento T1 em Lisboa",
            "T2 em Arroios com varanda",
            "Estúdio mobilado no centro",
            "Moradia T3 em Benfica",
            "Loft moderno em Alfama"
        ]
        
        # Test cases - descriptions that should be filtered
        room_descriptions = [
            "Apartamento com quarto em apartamento partilhado",
            "Alugam-se quartos em apartamento renovado",
            "Shared room in a modern apartment",
            "Quarto partilhado com casa de banho privativa",
            "Room in apartment near university"
        ]
        
        # Test cases - descriptions that should NOT be filtered
        apartment_descriptions = [
            "Apartamento com 2 quartos e sala",
            "Moradia com jardim e garagem",
            "Estúdio renovado com cozinha equipada",
            "T1 com varanda e vista para o rio",
            "Loft com mezanino e ar condicionado"
        ]
        
        # Test title filtering
        logger.info("Testing title filtering...")
        for title in room_titles:
            title_upper = title.upper()
            is_room = any(title_upper.startswith(term) for term in ROOM_RENTAL_TITLE_TERMS)
            result = "FILTERED" if is_room else "NOT FILTERED"
            logger.info(f"Title: '{title}' - {result}")
            if not is_room:
                logger.warning(f"FAILED: Room title '{title}' was not filtered!")
        
        for title in apartment_titles:
            title_upper = title.upper()
            is_room = any(title_upper.startswith(term) for term in ROOM_RENTAL_TITLE_TERMS)
            result = "FILTERED" if is_room else "NOT FILTERED"
            logger.info(f"Title: '{title}' - {result}")
            if is_room:
                logger.warning(f"FAILED: Apartment title '{title}' was incorrectly filtered!")
        
        # Test description filtering
        logger.info("\nTesting description filtering...")
        for desc in room_descriptions:
            desc_upper = desc.upper()
            is_room = any(term in desc_upper for term in ROOM_RENTAL_DESCRIPTION_TERMS)
            result = "FILTERED" if is_room else "NOT FILTERED"
            logger.info(f"Description: '{desc}' - {result}")
            if not is_room:
                logger.warning(f"FAILED: Room description '{desc}' was not filtered!")
        
        for desc in apartment_descriptions:
            desc_upper = desc.upper()
            is_room = any(term in desc_upper for term in ROOM_RENTAL_DESCRIPTION_TERMS)
            result = "FILTERED" if is_room else "NOT FILTERED"
            logger.info(f"Description: '{desc}' - {result}")
            if is_room:
                logger.warning(f"FAILED: Apartment description '{desc}' was incorrectly filtered!")
        
        logger.info("Room rental filtering test completed")
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_room_filter() 