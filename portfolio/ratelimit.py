"""
ماژول محدودیت نرخ درخواست (Rate Limiting) و استخراج امن IP کلاینت
"""
from django.core.cache import cache

def get_client_ip(request):
    """
    استخراج امن آی‌پی کلاینت با در نظر گرفتن پروکسی Nginx
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip or '127.0.0.1'

def is_rate_limited(key: str, max_attempts: int = 5, window_seconds: int = 300) -> bool:
    """
    بررسی محدودیت نرخ ارسال درخواست بر اساس کلید و پنجره زمانی (کش درون حافظه)
    اگر تعداد درخواست‌ها در بازه زمانی از max_attempts بیشتر شود True برمی‌گرداند.
    """
    cache_key = f"rl:{key}"
    try:
        count = cache.get(cache_key, 0)
        if count >= max_attempts:
            return True
        if count == 0:
            cache.set(cache_key, 1, timeout=window_seconds)
        else:
            try:
                cache.incr(cache_key)
            except Exception:
                cache.set(cache_key, count + 1, timeout=window_seconds)
    except Exception:
        # در صورت بروز خطای کش، مسدودسازی اشتباه انجام ندهد
        return False
    return False

def reset_rate_limit(key: str):
    """
    ریست کردن شمارنده محدودیت (مثلاً پس از ورود موفق ادمین)
    """
    try:
        cache.delete(f"rl:{key}")
    except Exception:
        pass
