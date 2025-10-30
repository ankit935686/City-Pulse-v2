from django.db import models

# Create your models here.

class Project(models.Model):
    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Delayed', 'Delayed'),
    ]
    
    SECTOR_CHOICES = [
        ('Roads', 'Roads'),
        ('Metro', 'Metro'),
        ('Bridges', 'Bridges'),
        ('Smart City', 'Smart City'),
        ('Beautification', 'Beautification'),
        ('Redevelopment', 'Redevelopment'),
        ('Waste Management', 'Waste Management'),
        ('Water Supply', 'Water Supply'),
        ('Green Spaces', 'Green Spaces'),
        ('Transport', 'Transport'),
        ('Railways', 'Railways'),
        ('Eco-Tourism', 'Eco-Tourism'),
        ('Ports', 'Ports'),
        ('Airport', 'Airport'),
    ]
    
    project_id = models.CharField(max_length=20, unique=True)
    project_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateField()
    expected_completion_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)  # in crores
    contractor = models.CharField(max_length=200)
    progress = models.IntegerField()  # percentage
    description = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.project_id} - {self.project_name}"
    
    @property
    def budget_formatted(self):
        return f"₹{self.budget} Cr"
    
    @property
    def progress_color(self):
        if self.status == 'Completed':
            return '#10B981'  # Green
        elif self.status == 'Delayed':
            return '#EF4444'  # Red
        else:
            return '#3B82F6'  # Blue


class RoadDevelopmentPlan(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('Under Construction', 'Under Construction'),
        ('Completed', 'Completed'),
        ('Delayed', 'Delayed'),
    ]
    
    project_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    road_length = models.DecimalField(max_digits=8, decimal_places=2)  # in km
    budget = models.DecimalField(max_digits=10, decimal_places=2)  # in crores
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    contractor = models.CharField(max_length=200)
    priority_level = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_year']
    
    def __str__(self):
        return f"{self.project_name} - {self.city}"
    
    @property
    def budget_formatted(self):
        return f"₹{self.budget} Cr"
    
    @property
    def duration_years(self):
        return self.end_year - self.start_year


class ProjectBottleneck(models.Model):
    SEVERITY_CHOICES = [
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Pending', 'Pending'),
    ]
    
    bottleneck_id = models.CharField(max_length=20, unique=True)
    project_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    bottleneck_type = models.CharField(max_length=100)
    severity_level = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    reported_date = models.DateField()
    expected_resolution_date = models.DateField()
    responsible_department = models.CharField(max_length=100)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    impact_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-reported_date']
    
    def __str__(self):
        return f"{self.bottleneck_id} - {self.project_name}"
    
    @property
    def severity_color(self):
        if self.severity_level == 'Critical':
            return '#EF4444'  # Red
        elif self.severity_level == 'High':
            return '#F59E0B'  # Amber
        elif self.severity_level == 'Medium':
            return '#3B82F6'  # Blue
        else:
            return '#10B981'  # Green


class MetroConstructionUpdate(models.Model):
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('Under Construction', 'Under Construction'),
        ('Completed', 'Completed'),
        ('Delayed', 'Delayed'),
    ]
    
    project_id = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=100)
    project_name = models.CharField(max_length=200)
    length = models.DecimalField(max_digits=8, decimal_places=2)  # in km
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    estimated_completion = models.DateField()
    current_progress = models.CharField(max_length=10)  # percentage
    budget = models.DecimalField(max_digits=10, decimal_places=2)  # in crores
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-estimated_completion']
    
    def __str__(self):
        return f"{self.project_id} - {self.project_name}"
    
    @property
    def budget_formatted(self):
        return f"₹{self.budget} Cr"
    
    @property
    def progress_color(self):
        if self.status == 'Completed':
            return '#10B981'  # Green
        elif self.status == 'Delayed':
            return '#EF4444'  # Red
        elif self.status == 'Under Construction':
            return '#3B82F6'  # Blue
        else:
            return '#6B7280'  # Gray
