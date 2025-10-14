from django.contrib import admin
from .models import ServiceProvider, ProviderNotification, ProviderEarnings

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'provider_type', 'verification_status', 'is_active', 'total_earnings', 'created_at']
    list_filter = ['provider_type', 'verification_status', 'is_active', 'created_at']
    search_fields = ['business_name', 'user__username', 'user__email', 'business_email', 'gst_number']
    readonly_fields = ['total_earnings', 'created_at', 'updated_at', 'verified_at']
    list_editable = ['verification_status', 'is_active']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Business Information', {
            'fields': ('provider_type', 'business_name', 'business_registration_number', 'gst_number')
        }),
        ('Contact Details', {
            'fields': ('business_phone', 'business_email', 'business_address')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_documents', 'verified_at', 'verified_by')
        }),
        ('Banking Details', {
            'fields': ('bank_account_number', 'bank_name', 'bank_ifsc_code', 'account_holder_name'),
            'classes': ('collapse',)
        }),
        ('Financial', {
            'fields': ('commission_rate', 'total_earnings')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['verify_providers', 'suspend_providers', 'activate_providers']
    
    def verify_providers(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(verification_status='VERIFIED', verified_at=timezone.now())
        for provider in queryset:
            provider.verified_by = request.user
            provider.save()
        self.message_user(request, f'{updated} service providers verified.')
    verify_providers.short_description = 'Verify selected providers'
    
    def suspend_providers(self, request, queryset):
        updated = queryset.update(verification_status='SUSPENDED', is_active=False)
        self.message_user(request, f'{updated} service providers suspended.')
    suspend_providers.short_description = 'Suspend selected providers'
    
    def activate_providers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} service providers activated.')
    activate_providers.short_description = 'Activate selected providers'

@admin.register(ProviderNotification)
class ProviderNotificationAdmin(admin.ModelAdmin):
    list_display = ['provider', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['provider__business_name', 'title', 'message']
    readonly_fields = ['created_at']

@admin.register(ProviderEarnings)
class ProviderEarningsAdmin(admin.ModelAdmin):
    list_display = ['provider', 'booking_amount', 'commission_amount', 'provider_earnings', 'is_settled', 'created_at']
    list_filter = ['is_settled', 'created_at']
    search_fields = ['provider__business_name', 'settlement_reference']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'