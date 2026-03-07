"""Provider factory and registry."""
from typing import Dict, Optional, List
from app.services.providers.base_provider import BaseProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProviderRegistry:
    """Registry for managing sports data providers."""
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize enabled providers based on settings."""
        if settings.ENABLE_SOFASCORE:
            try:
                # Import lazily so optional provider deps don't crash app startup.
                from app.services.providers.sofascore_provider import SofascoreProvider
                self.register_provider(SofascoreProvider())
                logger.info("Sofascore provider registered")
            except Exception as e:
                logger.error(f"Failed to register Sofascore provider: {e}")
        
        # Future providers can be added here
        # if settings.ENABLE_FBREF:
        #     self.register_provider(FBrefProvider())
    
    def register_provider(self, provider: BaseProvider):
        """Register a new provider."""
        self._providers[provider.name] = provider
        logger.info(f"Provider registered: {provider.name}")
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get provider by name."""
        return self._providers.get(name)
    
    def get_all_providers(self) -> List[BaseProvider]:
        """Get all registered providers."""
        return list(self._providers.values())
    
    def get_providers_for_sport(self, sport: str) -> List[BaseProvider]:
        """Get all providers that support a given sport."""
        return [
            provider for provider in self._providers.values()
            if sport in provider.supported_sports
        ]


# Global provider registry instance
provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry."""
    return provider_registry
