"""
Domain Suggestion Service

Generates intelligent domain suggestions based on business data.
"""

import re
from typing import Optional
from unidecode import unidecode

from app.models.schemas import DomainSuggestion
from app.services.supabase_client import SupabaseService


class DomainSuggestionService:
    """Service for generating domain suggestions"""

    def __init__(self):
        self.db = SupabaseService()

    def clean_domain_name(self, name: str) -> str:
        """
        Clean and normalize domain name

        Args:
            name: Raw business name

        Returns:
            Cleaned domain name (lowercase, ASCII, hyphens)
        """
        # Convert to ASCII (ä -> a, ö -> o, etc.)
        name = unidecode(name)

        # Lowercase
        name = name.lower()

        # Remove common business suffixes
        name = re.sub(r'\b(gmbh|ag|kg|ohg|gbr|e\.?v\.?|ug|mbh)\b', '', name, flags=re.IGNORECASE)

        # Remove special characters, keep letters, numbers, spaces, hyphens
        name = re.sub(r'[^a-z0-9\s-]', '', name)

        # Replace multiple spaces/hyphens with single hyphen
        name = re.sub(r'[\s-]+', '-', name)

        # Remove leading/trailing hyphens
        name = name.strip('-')

        return name

    def generate_variations(self, base: str, branche: Optional[str] = None) -> list[str]:
        """
        Generate domain name variations

        Args:
            base: Base domain name
            branche: Industry sector (optional)

        Returns:
            List of domain variations
        """
        variations = [base]

        # Add industry-specific keywords
        if branche:
            branche_keywords = {
                "handwerker": ["handwerk", "meister", "service"],
                "haendler": ["shop", "store", "markt"],
                "dienstleister": ["service", "pro", "experte"],
            }

            keywords = branche_keywords.get(branche, [])
            for keyword in keywords:
                variations.append(f"{base}-{keyword}")
                variations.append(f"{keyword}-{base}")

        # Add generic variations
        variations.extend([
            f"{base}-online",
            f"mein-{base}",
            f"{base}-24",
        ])

        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for v in variations:
            if v not in seen:
                seen.add(v)
                unique_variations.append(v)

        return unique_variations

    def generate_suggestions(
        self,
        wunschdomain_basis: str,
        land: str,
        branche: Optional[str] = None,
        max_suggestions: int = 10
    ) -> list[DomainSuggestion]:
        """
        Generate domain suggestions

        Args:
            wunschdomain_basis: Base domain name (cleaned)
            land: Country code (ISO 3166-1 alpha-2)
            branche: Industry sector
            max_suggestions: Maximum number of suggestions

        Returns:
            List of domain suggestions with pricing and priority
        """
        # Clean the base domain
        clean_base = self.clean_domain_name(wunschdomain_basis)

        # Generate variations
        variations = self.generate_variations(clean_base, branche)

        # Get recommended TLDs for country
        tlds = self.db.get_tlds_for_country(land, limit=10)

        # Generate suggestions
        suggestions = []

        for variation in variations[:5]:  # Limit variations
            for tld_data in tlds:
                if len(suggestions) >= max_suggestions:
                    break

                domain = f"{variation}.{tld_data['tld']}"

                suggestion = DomainSuggestion(
                    domain=domain,
                    tld=tld_data['tld'],
                    verfuegbar=None,  # Will be checked via INWX
                    preis_eur=tld_data['vk_eur'],
                    prio=tld_data['prio'],
                    empfohlen=(variation == clean_base and tld_data['prio'] >= 90)
                )

                suggestions.append(suggestion)

            if len(suggestions) >= max_suggestions:
                break

        # Sort by priority (descending) and recommended first
        suggestions.sort(key=lambda s: (not s.empfohlen, -s.prio))

        return suggestions[:max_suggestions]
