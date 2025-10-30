from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Avg, Sum
from django.db.models.functions import ExtractYear, ExtractMonth
import json
import csv
import os
from datetime import datetime, timedelta
from .models import Project, RoadDevelopmentPlan, ProjectBottleneck, MetroConstructionUpdate

def projects_overview(request):
    """Main view for projects overview dashboard"""
    return render(request, 'logistics/projects_overview.html')

def officials_dashboard(request):
    """Main Officials' Dashboard landing page"""
    return render(request, 'logistics/officials_dashboard.html')

def trends_analysis(request):
    """View for trends analysis and analytics"""
    return render(request, 'logistics/trends_analysis.html')

def bottlenecks_view(request):
    """View for bottlenecks and issues analysis"""
    return render(request, 'logistics/bottlenecks_view.html')

def road_development_analytics(request):
    """View for road development analytics and planning insights"""
    return render(request, 'logistics/road_development_analytics.html')

@csrf_exempt
def get_projects_data(request):
    """API endpoint to get all projects data"""
    try:
        projects = Project.objects.all()
        projects_data = []
        
        for project in projects:
            projects_data.append({
                'id': project.project_id,
                'name': project.project_name,
                'location': project.location,
                'sector': project.sector,
                'status': project.status,
                'start_date': project.start_date.strftime('%d-%m-%Y'),
                'end_date': project.expected_completion_date.strftime('%d-%m-%Y'),
                'budget': float(project.budget),
                'contractor': project.contractor,
                'progress': project.progress,
                'description': project.description,
                'latitude': float(project.latitude) if project.latitude else None,
                'longitude': float(project.longitude) if project.longitude else None,
                'progress_color': project.progress_color,
            })
        
        return JsonResponse({'success': True, 'data': projects_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def filter_projects(request):
    """API endpoint to filter projects by status and search term"""
    try:
        data = json.loads(request.body)
        status_filter = data.get('status', '')
        search_term = data.get('search', '')
        
        projects = Project.objects.all()
        
        # Apply status filter
        if status_filter and status_filter != 'All':
            projects = projects.filter(status=status_filter)
        
        # Apply search filter
        if search_term:
            projects = projects.filter(
                Q(project_name__icontains=search_term) |
                Q(location__icontains=search_term) |
                Q(sector__icontains=search_term) |
                Q(contractor__icontains=search_term)
            )
        
        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.project_id,
                'name': project.project_name,
                'location': project.location,
                'sector': project.sector,
                'status': project.status,
                'start_date': project.start_date.strftime('%d-%m-%Y'),
                'end_date': project.expected_completion_date.strftime('%d-%m-%Y'),
                'budget': float(project.budget),
                'contractor': project.contractor,
                'progress': project.progress,
                'description': project.description,
                'latitude': float(project.latitude) if project.latitude else None,
                'longitude': float(project.longitude) if project.longitude else None,
                'progress_color': project.progress_color,
            })
        
        return JsonResponse({'success': True, 'data': projects_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_trends_data(request):
    """API endpoint to get trends data for analytics"""
    try:
        # Project status distribution
        status_distribution = Project.objects.values('status').annotate(count=Count('id'))
        
        # Budget by sector
        budget_by_sector = Project.objects.values('sector').annotate(
            total_budget=Sum('budget'),
            avg_budget=Avg('budget'),
            count=Count('id')
        )
        
        # Completion trends by year
        completion_trends = Project.objects.annotate(
            year=ExtractYear('start_date')
        ).values('year', 'status').annotate(count=Count('id'))
        
        # Monthly project starts
        monthly_starts = Project.objects.annotate(
            year=ExtractYear('start_date'),
            month=ExtractMonth('start_date')
        ).values('year', 'month').annotate(count=Count('id'))
        
        # Progress by status
        progress_by_status = Project.objects.values('status').annotate(
            avg_progress=Avg('progress'),
            count=Count('id')
        )
        
        trends_data = {
            'status_distribution': list(status_distribution),
            'budget_by_sector': list(budget_by_sector),
            'completion_trends': list(completion_trends),
            'monthly_starts': list(monthly_starts),
            'progress_by_status': list(progress_by_status),
        }
        
        return JsonResponse({'success': True, 'data': trends_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_bottlenecks_data(request):
    """API endpoint to get bottlenecks data"""
    try:
        # Bottleneck statistics
        severity_stats = ProjectBottleneck.objects.values('severity_level').annotate(count=Count('id'))
        status_stats = ProjectBottleneck.objects.values('current_status').annotate(count=Count('id'))
        type_stats = ProjectBottleneck.objects.values('bottleneck_type').annotate(count=Count('id'))
        department_stats = ProjectBottleneck.objects.values('responsible_department').annotate(count=Count('id'))
        
        # All bottlenecks
        bottlenecks = ProjectBottleneck.objects.all()
        bottlenecks_data = []
        
        for bottleneck in bottlenecks:
            bottlenecks_data.append({
                'id': bottleneck.bottleneck_id,
                'project_name': bottleneck.project_name,
                'location': bottleneck.location,
                'type': bottleneck.bottleneck_type,
                'severity': bottleneck.severity_level,
                'department': bottleneck.responsible_department,
                'status': bottleneck.current_status,
                'description': bottleneck.impact_description,
                'reported_date': bottleneck.reported_date.strftime('%d-%m-%Y'),
                'expected_resolution': bottleneck.expected_resolution_date.strftime('%d-%m-%Y'),
                'severity_color': bottleneck.severity_color,
            })
        
        bottlenecks_data = {
            'severity_stats': list(severity_stats),
            'status_stats': list(status_stats),
            'type_stats': list(type_stats),
            'department_stats': list(department_stats),
            'bottlenecks': bottlenecks_data,
        }
        
        return JsonResponse({'success': True, 'data': bottlenecks_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_road_development_data(request):
    """API endpoint to get road development analytics data"""
    try:
        # Get all road development plans
        road_plans = RoadDevelopmentPlan.objects.all()
        
        # Basic statistics
        total_projects = road_plans.count()
        total_budget = road_plans.aggregate(total=Sum('budget'))['total'] or 0
        total_road_length = road_plans.aggregate(total=Sum('road_length'))['total'] or 0
        
        # Status distribution
        status_counts = road_plans.values('current_status').annotate(count=Count('id'))
        status_data = {item['current_status']: item['count'] for item in status_counts}
        
        # Priority distribution
        priority_counts = road_plans.values('priority_level').annotate(count=Count('id'))
        priority_data = {item['priority_level']: item['count'] for item in priority_counts}
        
        # City-wise distribution
        city_counts = road_plans.values('city').annotate(count=Count('id'))
        city_data = {item['city']: item['count'] for item in city_counts}
        
        # Budget analysis by status
        budget_by_status = {}
        for status in ['Planning', 'Under Construction', 'Completed', 'Delayed']:
            status_projects = road_plans.filter(current_status=status)
            total_status_budget = status_projects.aggregate(total=Sum('budget'))['total'] or 0
            budget_by_status[status] = float(total_status_budget)
        
        # Road length analysis by priority
        length_by_priority = {}
        for priority in ['High', 'Medium', 'Low']:
            priority_projects = road_plans.filter(priority_level=priority)
            total_priority_length = priority_projects.aggregate(total=Sum('road_length'))['total'] or 0
            length_by_priority[priority] = float(total_priority_length)
        
        # Year-wise project starts
        year_starts = road_plans.values('start_year').annotate(count=Count('id'))
        year_data = {str(item['start_year']): item['count'] for item in year_starts}
        
        # Contractor analysis
        contractor_counts = road_plans.values('contractor').annotate(count=Count('id'))
        top_contractors = sorted(contractor_counts, key=lambda x: x['count'], reverse=True)[:10]
        contractor_data = {item['contractor']: item['count'] for item in top_contractors}
        
        # Project duration analysis
        duration_stats = []
        for plan in road_plans:
            if plan.start_year and plan.end_year:
                duration = plan.duration_years
                duration_stats.append({
                    'project_name': plan.project_name,
                    'city': plan.city,
                    'duration': duration,
                    'budget': float(plan.budget),
                    'road_length': float(plan.road_length),
                    'status': plan.current_status,
                    'priority': plan.priority_level
                })
        
        # Sort by duration
        duration_stats.sort(key=lambda x: x['duration'], reverse=True)
        
        # Budget efficiency (budget per km)
        efficiency_stats = []
        for plan in road_plans:
            if plan.road_length > 0:
                efficiency = float(plan.budget) / float(plan.road_length)
                efficiency_stats.append({
                    'project_name': plan.project_name,
                    'city': plan.city,
                    'efficiency': round(efficiency, 2),
                    'budget': float(plan.budget),
                    'road_length': float(plan.road_length),
                    'status': plan.current_status,
                    'priority': plan.priority_level
                })
        
        # Sort by efficiency (lower is better)
        efficiency_stats.sort(key=lambda x: x['efficiency'])
        
        data = {
            'total_projects': total_projects,
            'total_budget': float(total_budget),
            'total_road_length': float(total_road_length),
            'status_data': status_data,
            'priority_data': priority_data,
            'city_data': city_data,
            'budget_by_status': budget_by_status,
            'length_by_priority': length_by_priority,
            'year_data': year_data,
            'contractor_data': contractor_data,
            'duration_stats': duration_stats[:10],  # Top 10 longest projects
            'efficiency_stats': efficiency_stats[:10]  # Top 10 most efficient projects
        }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def load_csv_data(request):
    """Load CSV data into the database (for initial setup)"""
    try:
        csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mumbai_infrastructure_projects.csv')
        
        if not os.path.exists(csv_file_path):
            return JsonResponse({'success': False, 'error': 'CSV file not found'})
        
        # Clear existing data
        Project.objects.all().delete()
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Parse dates
                start_date = datetime.strptime(row['Start Date'], '%d-%m-%Y').date()
                end_date = datetime.strptime(row['Expected Completion Date'], '%d-%m-%Y').date()
                
                # Create project with default coordinates (Mumbai center)
                project = Project.objects.create(
                    project_id=row['Project ID'],
                    project_name=row['Project Name'],
                    location=row['Location'],
                    sector=row['Sector'],
                    status=row['Status'],
                    start_date=start_date,
                    expected_completion_date=end_date,
                    budget=float(row['Budget (₹ Crores)']),
                    contractor=row['Contractor'],
                    progress=int(row['Progress (%)']),
                    description=row['Description'],
                    latitude=19.0760,  # Default Mumbai coordinates
                    longitude=72.8777,
                )
        
        return JsonResponse({'success': True, 'message': f'Loaded {Project.objects.count()} projects'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def load_road_development_csv(request):
    """Load road development plans CSV data"""
    try:
        csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'road_development_plans.csv')
        
        if not os.path.exists(csv_file_path):
            return JsonResponse({'success': False, 'error': 'CSV file not found'})
        
        # Clear existing data
        RoadDevelopmentPlan.objects.all().delete()
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                RoadDevelopmentPlan.objects.create(
                    project_name=row['Project Name'],
                    city=row['City'],
                    road_length=float(row['Road Length (km)']),
                    budget=float(row['Budget (₹ Crores)']),
                    start_year=int(row['Start Year']),
                    end_year=int(row['End Year']),
                    current_status=row['Current Status'],
                    contractor=row['Contractor'],
                    priority_level=row['Priority Level'],
                )
        
        return JsonResponse({'success': True, 'message': f'Loaded {RoadDevelopmentPlan.objects.count()} road development plans'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def load_bottlenecks_csv(request):
    """Load project bottlenecks CSV data"""
    try:
        csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mumbai_project_bottlenecks.csv')
        
        if not os.path.exists(csv_file_path):
            return JsonResponse({'success': False, 'error': 'CSV file not found'})
        
        # Clear existing data
        ProjectBottleneck.objects.all().delete()
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Parse dates
                reported_date = datetime.strptime(row['Reported_Date'], '%Y-%m-%d').date()
                expected_resolution = datetime.strptime(row['Expected_Resolution_Date'], '%Y-%m-%d').date()
                
                ProjectBottleneck.objects.create(
                    bottleneck_id=row['Bottleneck_ID'],
                    project_name=row['Project_Name'],
                    location=row['Location'],
                    bottleneck_type=row['Bottleneck_Type'],
                    severity_level=row['Severity_Level'],
                    reported_date=reported_date,
                    expected_resolution_date=expected_resolution,
                    responsible_department=row['Responsible_Department'],
                    current_status=row['Current_Status'],
                    impact_description=row['Impact_Description'],
                )
        
        return JsonResponse({'success': True, 'message': f'Loaded {ProjectBottleneck.objects.count()} bottlenecks'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def load_metro_csv(request):
    """Load metro construction updates CSV data"""
    try:
        csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'metro_construction_updates.csv')
        
        if not os.path.exists(csv_file_path):
            return JsonResponse({'success': False, 'error': 'CSV file not found'})
        
        # Clear existing data
        MetroConstructionUpdate.objects.all().delete()
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Parse date
                estimated_completion = datetime.strptime(row['Estimated_Completion'], '%Y-%m-%d').date()
                
                MetroConstructionUpdate.objects.create(
                    project_id=row['Project_ID'],
                    city=row['City'],
                    project_name=row['Project_Name'],
                    length=float(row['Length']),
                    status=row['Status'],
                    estimated_completion=estimated_completion,
                    current_progress=row['Current_Progress'],
                    budget=float(row['Budget']),
                )
        
        return JsonResponse({'success': True, 'message': f'Loaded {MetroConstructionUpdate.objects.count()} metro updates'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
