from django.db import models
from django.conf import settings

# Create your models here.

class House(models.Model):
    name = models.CharField(max_length=255)
    zone = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField(max_length=500)
    bedrooms = models.CharField(max_length=50)  # Using CharField as it might contain text like "T2"
    area = models.DecimalField(max_digits=8, decimal_places=2)
    area_str = models.CharField(max_length=50, null=True, blank=True)
    floor = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField()
    freguesia = models.CharField(max_length=100)
    concelho = models.CharField(max_length=100)
    source = models.CharField(max_length=50)
    scraped_at = models.DateTimeField()
    image_urls = models.TextField(null=True, blank=True)  # Store as simple string with separator
    house_id = models.CharField(max_length=100, unique=True)
    
    # User relationships
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_houses',
        blank=True
    )
    contacted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='contacted_houses',
        blank=True
    )
    discarded_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='discarded_houses',
        blank=True
    )

    class Meta:
        db_table = 'houses'
        ordering = ['-scraped_at']

    def __str__(self):
        return f"{self.name} - {self.zone} ({self.price}€)"

    def save(self, *args, **kwargs):
        import logging
        #logger = logging.getLogger('house_scrapers')
        
        # Only process image URLs if this is a new house (not yet saved)
        if not self.pk and hasattr(self, '_image_urls_to_save') and self._image_urls_to_save:
            #logger.debug(f"[IMAGE_DEBUG] Converting _image_urls_to_save to string: {self._image_urls_to_save}")
            
            # If it's a list, join with separator
            if isinstance(self._image_urls_to_save, list):
                self.image_urls = "|||".join(self._image_urls_to_save)
            # If it's already a string, use it directly
            elif isinstance(self._image_urls_to_save, str):
                self.image_urls = self._image_urls_to_save
            
            #logger.debug(f"[IMAGE_DEBUG] Converted to string: {self.image_urls}")
        
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Log after save
        #logger.debug(f"[IMAGE_DEBUG] House.save() - After save - House ID: {self.id}, URL: {self.url}")
        
    def get_image_urls_list(self):
        """Get image URLs as a list"""
        if not self.image_urls:
            return []
        return self.image_urls.split("|||")

class MainRun(models.Model):
    STATUS_CHOICES = [
        ('initialized', 'Initialized'),
        ('running', 'Running'), 
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)  # Store execution time in seconds
    total_houses = models.IntegerField(default=0)  # Total houses across all scrapers
    new_houses = models.IntegerField(default=0)    # Total new houses across all scrapers
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'main_runs'
        ordering = ['-start_time']

    def __str__(self):
        return f"Main Run - {self.start_time} ({self.status})"

class ScraperRun(models.Model):
    STATUS_CHOICES = [
        ('initialized', 'Initialized'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    main_run = models.ForeignKey(MainRun, on_delete=models.CASCADE, related_name='scraper_runs')
    scraper = models.CharField(max_length=50)  # Store scraper name directly
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)  # Store execution time in seconds
    total_houses = models.IntegerField(default=0)  # Total houses seen on the page
    new_houses = models.IntegerField(default=0)    # New houses found
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'scraper_runs'
        ordering = ['-start_time']
        
    def __str__(self):
        return f"{self.scraper} - {self.start_time} ({self.status})"
