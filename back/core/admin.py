from django.contrib import admin
from .models import Material, MaterialSpec, RegulationMapping, Supplier, SupplyHistory, Demand


class MaterialSpecInline(admin.StackedInline):
    model = MaterialSpec
    extra = 0


class RegulationMappingInline(admin.StackedInline):
    model = RegulationMapping
    extra = 0


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display  = ["name", "ks_code", "ks_grade", "diameter", "category", "is_seismic", "is_weldable"]
    list_filter   = ["category", "ks_grade", "is_seismic"]
    search_fields = ["name", "ks_code", "ks_grade"]
    inlines       = [MaterialSpecInline, RegulationMappingInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display  = ["name", "address", "phone", "has_coordinates", "source"]
    search_fields = ["name", "business_no", "address"]
    list_filter   = ["source"]

    @admin.display(boolean=True, description="좌표 있음")
    def has_coordinates(self, obj):
        return obj.has_coordinates


@admin.register(SupplyHistory)
class SupplyHistoryAdmin(admin.ModelAdmin):
    list_display  = ["supplier", "material", "contract_date", "unit_price", "quantity"]
    list_filter   = ["material", "contract_date"]
    search_fields = ["supplier__name", "material__name"]
    date_hierarchy = "contract_date"


@admin.register(Demand)
class DemandAdmin(admin.ModelAdmin):
    list_display  = ["site_name", "material", "quantity", "deadline", "created_at"]
    list_filter   = ["deadline"]
    search_fields = ["site_name"]