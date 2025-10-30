from django.contrib import admin
from .models import Project, RoadDevelopmentPlan, ProjectBottleneck, MetroConstructionUpdate

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'project_name', 'location', 'sector', 'status', 'budget', 'progress', 'start_date', 'expected_completion_date')
    list_filter = ('status', 'sector', 'start_date')
    search_fields = ('project_name', 'location', 'contractor')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

class RoadDevelopmentPlanAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'city', 'road_length', 'budget', 'start_year', 'end_year', 'current_status', 'priority_level')
    list_filter = ('current_status', 'priority_level', 'city', 'start_year')
    search_fields = ('project_name', 'city', 'contractor')
    readonly_fields = ('created_at',)
    list_per_page = 25

class ProjectBottleneckAdmin(admin.ModelAdmin):
    list_display = ('bottleneck_id', 'project_name', 'location', 'bottleneck_type', 'severity_level', 'current_status', 'responsible_department')
    list_filter = ('severity_level', 'current_status', 'bottleneck_type', 'responsible_department')
    search_fields = ('project_name', 'location', 'bottleneck_type')
    readonly_fields = ('created_at',)
    list_per_page = 25

class MetroConstructionUpdateAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'project_name', 'city', 'length', 'status', 'current_progress', 'budget', 'estimated_completion')
    list_filter = ('status', 'city', 'estimated_completion')
    search_fields = ('project_name', 'city')
    readonly_fields = ('created_at',)
    list_per_page = 25

admin.site.register(Project, ProjectAdmin)
admin.site.register(RoadDevelopmentPlan, RoadDevelopmentPlanAdmin)
admin.site.register(ProjectBottleneck, ProjectBottleneckAdmin)
admin.site.register(MetroConstructionUpdate, MetroConstructionUpdateAdmin)
