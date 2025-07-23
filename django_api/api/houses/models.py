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

class Photo(models.Model):
    house = models.ForeignKey('House', on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Photo for {self.house.name} ({self.image_url})"

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
