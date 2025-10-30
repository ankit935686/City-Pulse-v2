import requests
import json
import logging
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from .models import (
    RecyclingCenter, RecyclingRequest, WasteCategory, 
    RecyclingGuide, MultilingualContent, RecyclingTip, UserProgress
)
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.core.cache import cache
import google.generativeai as genai
import time

logger = logging.getLogger(__name__)

# OpenRouteService API configuration
OPENROUTE_API_KEY = os.getenv('OPENROUTE_API_KEY')
OPENROUTE_BASE_URL = 'https://api.openrouteservice.org/v2/directions'

# Gemini API configuration
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

def recycling_map_view(request):
    """Display the recycling map with centers"""
    centers = RecyclingCenter.objects.filter(is_active=True)
    if not centers.exists():
        centers_data = get_sample_centers()
    else:
        centers_data = []
        for center in centers:
            centers_data.append({
                'id': center.id,
                'name': center.name,
                'address': center.address,
                'latitude': float(center.latitude),
                'longitude': float(center.longitude),
                'phone': center.phone,
                'email': center.email,
                'website': center.website,
                'center_type': center.center_type,
                'accepted_materials': center.accepted_materials,
                'opening_hours': center.opening_hours,
                'description': center.description,
                'is_open_now': center.is_open_now,
            })
    
    context = {
        'centers': centers_data
    }
    return render(request, 'recycle/recycling_map.html', context)

def submit_recycling_request(request):
    """Handle recycling request submission"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            center = get_object_or_404(RecyclingCenter, id=data['center_id'])
            
            request_obj = RecyclingRequest.objects.create(
                user=request.user,
                center=center,
                waste_type=data['waste_type'],
                quantity=data['quantity'],
                description=data['description']
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Recycling request submitted successfully!',
                'request_id': request_obj.id
            })
        except Exception as e:
            logger.error(f"Error submitting recycling request: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to submit request. Please try again.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_route_directions(request):
    """Get route directions using OpenRouteService API"""
    try:
        start_lat = request.GET.get('start_lat')
        start_lng = request.GET.get('start_lng')
        end_lat = request.GET.get('end_lat')
        end_lng = request.GET.get('end_lng')
        
        if not all([start_lat, start_lng, end_lat, end_lng]):
            return JsonResponse({
                'success': False,
                'error': 'Missing coordinates'
            })
        
        # OpenRouteService API call
        url = f"{OPENROUTE_BASE_URL}/driving-car"
        headers = {
            'Authorization': f'Bearer {OPENROUTE_API_KEY}',
            'Content-Type': 'application/json'
        }
        params = {
            'start': f"{start_lng},{start_lat}",
            'end': f"{end_lng},{end_lat}"
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        route_data = response.json()
        
        return JsonResponse({
            'success': True,
            'route': route_data
        })
        
    except requests.RequestException as e:
        logger.error(f"OpenRouteService API error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to get route directions'
        })
    except Exception as e:
        logger.error(f"Error getting route directions: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while getting directions'
        })

def filter_centers(request):
    """Filter recycling centers based on criteria"""
    centers = RecyclingCenter.objects.filter(is_active=True)
    if not centers.exists():
        centers_data = get_sample_centers()
    else:
        centers_data = []
        for center in centers:
            centers_data.append({
                'id': center.id,
                'name': center.name,
                'address': center.address,
                'latitude': float(center.latitude),
                'longitude': float(center.longitude),
                'phone': center.phone,
                'email': center.email,
                'website': center.website,
                'center_type': center.center_type,
                'accepted_materials': center.accepted_materials,
                'opening_hours': center.opening_hours,
                'description': center.description,
                'is_open_now': center.is_open_now,
            })
    
    return JsonResponse({'centers': centers_data})

@login_required
def my_recycling_requests(request):
    """Display user's recycling requests"""
    requests = RecyclingRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'recycle/my_requests.html', {'requests': requests})

# New views for Recycling Guide feature

def recycling_guide_home(request):
    guides = RecyclingGuide.objects.all().order_by('-created_at')
    context = {
        'guides': guides
    }
    return render(request, 'recycle/guide_home.html', context)

def category_detail(request, category_slug):
    category = get_object_or_404(WasteCategory, slug=category_slug)
    guides = RecyclingGuide.objects.filter(category=category)
    
    context = {
        'category': category,
        'guides': guides,
    }
    return render(request, 'recycle/category_detail.html', context)

def guide_detail(request, guide_slug):
    guide = get_object_or_404(RecyclingGuide, slug=guide_slug)
    guide.views += 1
    guide.save()
    
    # Get related guides from same category
    related_guides = RecyclingGuide.objects.filter(
        category=guide.category
    ).exclude(id=guide.id)[:3]
    
    context = {
        'guide': guide,
        'related_guides': related_guides,
    }
    return render(request, 'recycle/guide_detail.html', context)

@require_POST
def generate_ai_content(request):
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt')
        language = data.get('language', 'en')

        # Check cache first
        cache_key = f"recycling_guide_{language}_{hash(prompt)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return JsonResponse({
                'success': True,
                'content': cached_response,
                'source': 'cache'
            })

        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        # Add recycling context to prompt
        language_contexts = {
            'en': 'As a recycling expert, provide guidance about: ',
            'hi': 'एक रीसाइक्लिंग विशेषज्ञ के रूप में, इस बारे में मार्गदर्शन प्रदान करें: ',
            'mr': 'एक रीसायकलिंग तज्ञ म्हणून, याबद्दल मार्गदर्शन करा: ',
            'gu': 'રીસાયક્લિંગ નિષ્ણાત તરીકે, આના વિશે માર્ગદર્શન આપો: '
        }

        formatted_prompt = f"{language_contexts.get(language, language_contexts['en'])}{prompt}"

        try:
            response = model.generate_content(formatted_prompt)
            
            if response.text:
                # Cache successful response
                cache.set(cache_key, response.text, 3600)  # Cache for 1 hour
                return JsonResponse({
                    'success': True,
                    'content': response.text
                })
            else:
                logger.warning("Empty response from Gemini API")
                # Fall back to pre-defined content
                return get_fallback_content(prompt, language)

        except Exception as api_error:
            logger.error(f"Gemini API error: {api_error}")
            # Fall back to pre-defined content
            return get_fallback_content(prompt, language)

    except Exception as e:
        logger.error(f"Error in generate_ai_content: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request'
        }, status=500)

def get_fallback_content(prompt, language):
    """Provides pre-defined responses when API is unavailable"""
    basic_recycling_guides = {
        'en': {
            'plastic': 'Separate plastic items by type (PET, HDPE, etc). Ensure they are clean and dry.\nRemove caps and labels when possible.\nFlatten bottles to save space.\nCheck local recycling guidelines for accepted plastic types.',
            'paper': 'Separate paper into categories: newspapers, cardboard, mixed paper.\nRemove any plastic wrapping or tape.\nFlatten cardboard boxes.\nKeep paper dry and clean.\nShred confidential documents before recycling.',
            'metal': 'Clean metal containers. Separate aluminum from steel cans.\nRemove labels when possible.\nFlatten cans to save space.\nKeep metal items dry to prevent rusting.\nCheck if your local center accepts scrap metal.',
            'glass': 'Sort glass by color: clear, green, and brown.\nRemove caps, lids, and corks.\nRinse containers thoroughly.\nDo not break glass before recycling.\nCheck if your local center accepts window glass or mirrors.',
            'e-waste': 'Never mix with regular waste. Take to authorized collection centers.\nRemove batteries before recycling electronics.\nErase personal data from devices.\nCheck manufacturer take-back programs.\nSome retailers offer e-waste collection services.',
            'organic': 'Compost fruit and vegetable scraps, coffee grounds, and eggshells.\nAvoid composting meat, dairy, and oily foods.\nMix green materials (food scraps) with brown materials (dry leaves).\nKeep compost moist but not wet.\nTurn compost regularly for faster decomposition.',
            'battery': 'Never dispose of batteries in regular trash.\nUse designated battery collection points.\nTape the terminals of lithium batteries before disposal.\nConsider rechargeable batteries to reduce waste.\nSome electronics stores offer battery recycling services.',
            'textile': 'Donate clean, wearable clothing to charity.\nRecycle worn-out textiles at specialized collection points.\nSome retailers offer textile recycling programs.\nConsider upcycling old clothes into new items.\nCheck if your local recycling center accepts textiles.',
            'general': 'Reduce waste by choosing products with less packaging.\nReuse items whenever possible before recycling.\nRinse containers before recycling.\nFollow local recycling guidelines.\nCompost organic waste to reduce landfill impact.'
        },
        'hi': {
            'plastic': 'प्लास्टिक वस्तुओं को प्रकार के अनुसार अलग करें (PET, HDPE, आदि)। सुनिश्चित करें कि वे साफ और सूखे हैं।\nजब संभव हो तो कैप और लेबल हटा दें।\nजगह बचाने के लिए बोतलों को चपटा करें।\nस्वीकृत प्लास्टिक प्रकारों के लिए स्थानीय रीसाइक्लिंग दिशानिर्देश जांचें।',
            'paper': 'कागज को श्रेणियों में अलग करें: अखबार, गत्ता, मिश्रित कागज।\nकिसी भी प्लास्टिक रैपिंग या टेप को हटा दें।\nगत्ते के डिब्बों को चपटा करें।\nकागज को सूखा और साफ रखें।\nरीसाइक्लिंग से पहले गोपनीय दस्तावेजों को श्रेड करें।',
            'metal': 'धातु के कंटेनरों को साफ करें। एल्युमीनियम को स्टील के डिब्बों से अलग करें।\nजब संभव हो तो लेबल हटा दें।\nजगह बचाने के लिए डिब्बों को चपटा करें।\nजंग लगने से रोकने के लिए धातु की वस्तुओं को सूखा रखें।\nजांचें कि क्या आपका स्थानीय केंद्र स्क्रैप मेटल स्वीकार करता है।',
            'glass': 'कांच को रंग के अनुसार अलग करें: साफ, हरा और भूरा।\nकैप, ढक्कन और कॉर्क हटा दें।\nकंटेनरों को अच्छी तरह से धोएं।\nरीसाइक्लिंग से पहले कांच को न तोड़ें।\nजांचें कि क्या आपका स्थानीय केंद्र विंडो ग्लास या मिरर स्वीकार करता है।',
            'e-waste': 'नियमित कचरे के साथ कभी न मिलाएं। अधिकृत संग्रह केंद्रों पर ले जाएं।\nइलेक्ट्रॉनिक्स को रीसायकल करने से पहले बैटरी निकाल दें।\nडिवाइस से व्यक्तिगत डेटा मिटा दें।\nनिर्माता टेक-बैक प्रोग्राम की जांच करें।\nकुछ रिटेलर्स ई-वेस्ट कलेक्शन सर्विस ऑफर करते हैं।',
            'organic': 'फल और सब्जी के छिलके, कॉफी ग्राउंड्स और अंडे के छिलके को कंपोस्ट करें।\nमांस, डेयरी और तैलीय खाद्य पदार्थों को कंपोस्ट करने से बचें।\nहरी सामग्री (खाद्य अवशेष) को भूरी सामग्री (सूखी पत्तियां) के साथ मिलाएं।\nकंपोस्ट को नम रखें लेकिन गीला न होने दें।\nतेजी से अपघटन के लिए कंपोस्ट को नियमित रूप से पलटें।',
            'general': 'कम पैकेजिंग वाले उत्पादों का चयन करके कचरे को कम करें।\nरीसाइक्लिंग से पहले जब भी संभव हो वस्तुओं का पुन: उपयोग करें।\nरीसाइक्लिंग से पहले कंटेनरों को धोएं।\nस्थानीय रीसाइक्लिंग दिशानिर्देशों का पालन करें।\nलैंडफिल प्रभाव को कम करने के लिए जैविक कचरे को कंपोस्ट करें।'
        },
        'mr': {
            'general': 'कमी पॅकेजिंग असलेल्या उत्पादनांची निवड करून कचरा कमी करा.\nरिसायकलिंग करण्यापूर्वी शक्य तितक्या वस्तूंचा पुनर्वापर करा.\nरिसायकलिंग करण्यापूर्वी कंटेनर्स धुवा.\nस्थानिक रिसायकलिंग मार्गदर्शक तत्त्वांचे पालन करा.\nलँडफिल प्रभाव कमी करण्यासाठी सेंद्रिय कचरा कंपोस्ट करा.'
        },
        'gu': {
            'general': 'ઓછી પેકેજિંગવાળા ઉત્પાદનો પસંદ કરીને કચરો ઘટાડો.\nરિસાયકલિંગ પહેલાં શક્ય હોય ત્યારે વસ્તુઓનો ફરીથી ઉપયોગ કરો.\nરિસાયકલિંગ પહેલાં કન્ટેનરો ધોવો.\nસ્થાનિક રિસાયકલિંગ માર્ગદર્શિકાઓનું પાલન કરો.\nલેન્ડફિલ અસરને ઘટાડવા માટે કાર્બનિક કચરાને ખાતર બનાવો.'
        }
    }

    # Simple keyword matching for fallback content
    content = []
    
    # Check for specific keywords in the prompt
    keywords = ['plastic', 'paper', 'metal', 'glass', 'e-waste', 'organic', 'battery', 'textile']
    found_match = False
    
    for key in keywords:
        if key.lower() in prompt.lower():
            guide = basic_recycling_guides.get(language, {}).get(key)
            if not guide and language != 'en':
                guide = basic_recycling_guides['en'].get(key)  # Fallback to English if translation not available
            if guide:
                content.append(guide)
                found_match = True
    
    # If no specific match found, provide general recycling tips
    if not found_match:
        general_guide = basic_recycling_guides.get(language, {}).get('general')
        if not general_guide and language != 'en':
            general_guide = basic_recycling_guides['en'].get('general')  # Fallback to English
        if general_guide:
            content.append(general_guide)
    
    # If still no content (unlikely), use a default message
    if not content:
        default_message = 'For proper recycling, clean and sort materials by type. Check local guidelines for specific instructions.'
        content = [default_message]

    return JsonResponse({
        'success': True,
        'content': '\n'.join(content),
        'source': 'fallback'
    })

@login_required
def save_user_progress(request):
    """Save user progress for a guide"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            guide_id = data.get('guide_id')
            completed = data.get('completed', False)
            time_spent = data.get('time_spent', 0)
            quiz_score = data.get('quiz_score')
            
            guide = get_object_or_404(RecyclingGuide, id=guide_id)
            
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                guide=guide
            )
            
            progress.completed = completed
            progress.time_spent = time_spent
            if quiz_score is not None:
                progress.quiz_score = quiz_score
            if completed:
                progress.completed_at = timezone.now()
            
            progress.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Progress saved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error saving user progress: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to save progress'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def search_guides(request):
    """Search recycling guides"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    guides = RecyclingGuide.objects.filter(is_active=True)
    
    if query:
        guides = guides.filter(title__icontains=query) | guides.filter(content__icontains=query)
    
    if category:
        guides = guides.filter(category__category_type=category)
    
    guides = guides[:20]  # Limit results
    
    results = []
    for guide in guides:
        results.append({
            'id': guide.id,
            'title': guide.title,
            'slug': guide.slug,
            'category': guide.category.name,
            'difficulty_level': guide.difficulty_level,
            'estimated_time': guide.estimated_time,
        })
    
    return JsonResponse({'results': results})

def sample_centers_api(request):
    """API endpoint to return sample recycling centers"""
    centers = get_sample_centers()
    return JsonResponse({
        'success': True,
        'centers': centers
    })

def get_sample_centers():
    """Return sample recycling centers for Mumbai area"""
    return [
        {
            'id': 1,
            'name': 'Mumbai E-Waste Collection Center',
            'address': 'Andheri West, Mumbai, Maharashtra 400058',
            'latitude': 19.1197,
            'longitude': 72.8464,
            'phone': '+91-22-2670-1234',
            'email': 'info@mumbaiecollect.com',
            'website': 'https://mumbaiecollect.com',
            'center_type': 'e_waste_collection',
            'accepted_materials': ['mobile_phones', 'laptops', 'computers', 'televisions', 'batteries'],
            'opening_hours': {
                'monday': '9:00 AM - 6:00 PM',
                'tuesday': '9:00 AM - 6:00 PM',
                'wednesday': '9:00 AM - 6:00 PM',
                'thursday': '9:00 AM - 6:00 PM',
                'friday': '9:00 AM - 6:00 PM',
                'saturday': '9:00 AM - 4:00 PM',
                'sunday': 'Closed'
            },
            'description': 'Professional e-waste collection and recycling services',
            'is_open_now': 'true'  # Use string 'true' for JavaScript
        },
        {
            'id': 2,
            'name': 'Green Earth Recycling Hub',
            'address': 'Bandra East, Mumbai, Maharashtra 400051',
            'latitude': 19.0596,
            'longitude': 72.8295,
            'phone': '+91-22-2640-5678',
            'email': 'contact@greenearthmumbai.com',
            'website': 'https://greenearthmumbai.com',
            'center_type': 'recycling_center',
            'accepted_materials': ['plastic', 'paper', 'glass', 'metal', 'textiles'],
            'opening_hours': {
                'monday': '8:00 AM - 7:00 PM',
                'tuesday': '8:00 AM - 7:00 PM',
                'wednesday': '8:00 AM - 7:00 PM',
                'thursday': '8:00 AM - 7:00 PM',
                'friday': '8:00 AM - 7:00 PM',
                'saturday': '8:00 AM - 5:00 PM',
                'sunday': '9:00 AM - 3:00 PM'
            },
            'description': 'Comprehensive recycling center for all types of waste',
            'is_open_now': 'true'
        },
        {
            'id': 3,
            'name': 'Juhu Beach Cleanup Station',
            'address': 'Juhu Beach Road, Mumbai, Maharashtra 400049',
            'latitude': 19.0996,
            'longitude': 72.8345,
            'phone': '+91-22-2660-9012',
            'email': 'cleanup@juhubeach.org',
            'website': 'https://juhubeach.org',
            'center_type': 'drop_off_center',
            'accepted_materials': ['plastic_bottles', 'paper_waste', 'glass_bottles', 'metal_cans'],
            'opening_hours': {
                'monday': '6:00 AM - 8:00 PM',
                'tuesday': '6:00 AM - 8:00 PM',
                'wednesday': '6:00 AM - 8:00 PM',
                'thursday': '6:00 AM - 8:00 PM',
                'friday': '6:00 AM - 8:00 PM',
                'saturday': '6:00 AM - 8:00 PM',
                'sunday': '6:00 AM - 8:00 PM'
            },
            'description': 'Beach cleanup and waste collection point',
            'is_open_now': 'true'
        },
        {
            'id': 4,
            'name': 'Worli Plastic Buyback Center',
            'address': 'Worli Naka, Mumbai, Maharashtra 400018',
            'latitude': 19.0179,
            'longitude': 72.8478,
            'phone': '+91-22-2490-3456',
            'email': 'buyback@worliplastic.com',
            'website': 'https://worliplastic.com',
            'center_type': 'buyback_center',
            'accepted_materials': ['plastic_bottles', 'plastic_bags', 'plastic_containers'],
            'opening_hours': {
                'monday': '7:00 AM - 6:00 PM',
                'tuesday': '7:00 AM - 6:00 PM',
                'wednesday': '7:00 AM - 6:00 PM',
                'thursday': '7:00 AM - 6:00 PM',
                'friday': '7:00 AM - 6:00 PM',
                'saturday': '7:00 AM - 5:00 PM',
                'sunday': 'Closed'
            },
            'description': 'Plastic waste buyback center with competitive rates',
            'is_open_now': 'true'
        },
        {
            'id': 5,
            'name': 'Colaba Paper Recycling',
            'address': 'Colaba Causeway, Mumbai, Maharashtra 400001',
            'latitude': 18.9217,
            'longitude': 72.8347,
            'phone': '+91-22-2280-7890',
            'email': 'recycle@colabapaper.com',
            'website': 'https://colabapaper.com',
            'center_type': 'recycling_center',
            'accepted_materials': ['newspapers', 'magazines', 'cardboard', 'office_paper'],
            'opening_hours': {
                'monday': '9:00 AM - 6:00 PM',
                'tuesday': '9:00 AM - 6:00 PM',
                'wednesday': '9:00 AM - 6:00 PM',
                'thursday': '9:00 AM - 6:00 PM',
                'friday': '9:00 AM - 6:00 PM',
                'saturday': '9:00 AM - 4:00 PM',
                'sunday': 'Closed'
            },
            'description': 'Specialized paper and cardboard recycling',
            'is_open_now': 'true'
        },
        {
            'id': 6,
            'name': 'Powai Glass Collection Point',
            'address': 'Powai Lake Road, Mumbai, Maharashtra 400076',
            'latitude': 19.1197,
            'longitude': 72.9064,
            'phone': '+91-22-2570-2345',
            'email': 'glass@powai.org',
            'website': 'https://powai.org',
            'center_type': 'drop_off_center',
            'accepted_materials': ['glass_bottles', 'glass_jars', 'broken_glass'],
            'opening_hours': {
                'monday': '8:00 AM - 6:00 PM',
                'tuesday': '8:00 AM - 6:00 PM',
                'wednesday': '8:00 AM - 6:00 PM',
                'thursday': '8:00 AM - 6:00 PM',
                'friday': '8:00 AM - 6:00 PM',
                'saturday': '8:00 AM - 5:00 PM',
                'sunday': 'Closed'
            },
            'description': 'Glass waste collection and recycling point',
            'is_open_now': 'true'
        },
        {
            'id': 7,
            'name': 'Thane Metal Recycling',
            'address': 'Thane West, Mumbai Metropolitan Region, Maharashtra 400601',
            'latitude': 19.2183,
            'longitude': 72.9781,
            'phone': '+91-22-2540-6789',
            'email': 'metal@thanerecycle.com',
            'website': 'https://thanerecycle.com',
            'center_type': 'recycling_center',
            'accepted_materials': ['aluminum_cans', 'steel_cans', 'copper_wire', 'iron_scrap'],
            'opening_hours': {
                'monday': '7:00 AM - 7:00 PM',
                'tuesday': '7:00 AM - 7:00 PM',
                'wednesday': '7:00 AM - 7:00 PM',
                'thursday': '7:00 AM - 7:00 PM',
                'friday': '7:00 AM - 7:00 PM',
                'saturday': '7:00 AM - 6:00 PM',
                'sunday': 'Closed'
            },
            'description': 'Metal recycling and processing center',
            'is_open_now': 'true'
        },
        {
            'id': 8,
            'name': 'Navi Mumbai Textile Hub',
            'address': 'Vashi, Navi Mumbai, Maharashtra 400703',
            'latitude': 19.0760,
            'longitude': 72.9983,
            'phone': '+91-22-2780-1234',
            'email': 'textile@navimumbai.org',
            'website': 'https://navimumbai.org',
            'center_type': 'recycling_center',
            'accepted_materials': ['old_clothes', 'fabric_scraps', 'denim', 'cotton_waste'],
            'opening_hours': {
                'monday': '9:00 AM - 6:00 PM',
                'tuesday': '9:00 AM - 6:00 PM',
                'wednesday': '9:00 AM - 6:00 PM',
                'thursday': '9:00 AM - 6:00 PM',
                'friday': '9:00 AM - 6:00 PM',
                'saturday': '9:00 AM - 4:00 PM',
                'sunday': 'Closed'
            },
            'description': 'Textile waste recycling and upcycling center',
            'is_open_now': 'true'
        }
    ]
