from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Discussion, Comment
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

@login_required
def discussions_view(request):
    discussions = Discussion.objects.all().order_by('-created_at')
    return render(request, 'discussion/discussions.html', {'discussions': discussions})

@login_required
@csrf_exempt
def create_discussion(request):
    if request.method == 'POST':
        try:
            # Safely extract and normalize inputs
            title = (request.POST.get('title') or '').strip()
            content = (request.POST.get('content') or '').strip()
            raw_latitude = request.POST.get('latitude')
            raw_longitude = request.POST.get('longitude')
            # CharField is not nullable in DB, default to empty string if missing
            location_name = (request.POST.get('location_name') or '').strip()

            def to_float(value):
                try:
                    if value in (None, ''):
                        return None
                    return float(value)
                except (TypeError, ValueError):
                    return None

            latitude = to_float(raw_latitude)
            longitude = to_float(raw_longitude)
            
            discussion = Discussion.objects.create(
                user=request.user,
                title=title,
                content=content,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name
            )

            if 'image' in request.FILES:
                discussion.image = request.FILES['image']
                discussion.save()

            return JsonResponse({'success': True, 'discussion_id': discussion.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def add_comment(request, discussion_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            discussion = get_object_or_404(Discussion, id=discussion_id)
            
            comment = Comment.objects.create(
                user=request.user,
                discussion=discussion,
                content=content
            )

            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'username': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime("%B %d, %Y %I:%M %p")
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@csrf_exempt
def toggle_upvote(request, discussion_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        discussion = get_object_or_404(Discussion, id=discussion_id)
        user = request.user

        if discussion.likes.filter(id=user.id).exists():
            discussion.likes.remove(user)
            upvoted = False
        else:
            discussion.likes.add(user)
            upvoted = True

        return JsonResponse({
            'success': True,
            'upvoted': upvoted,
            'upvotes_count': discussion.likes.count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def delete_discussion(request, discussion_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    discussion = get_object_or_404(Discussion, id=discussion_id)
    if not (request.user.is_staff or request.user == discussion.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        discussion.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_comments(request, discussion_id):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        discussion = get_object_or_404(Discussion, id=discussion_id)
        comments = discussion.comments.all().order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment.id,
                'username': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%b %d, %Y')
            })
        
        return JsonResponse({
            'success': True,
            'comments': comments_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})