from django.contrib import admin
from .models import (
    Material,
    MaterialSpec,
    RegulationMapping,
    Supplier,
    SupplyHistory,
    CategoryContractHistory,
    Demand,
    SupplierMaterialRegistration,
)


class MaterialSpecInline(admin.StackedInline):
    model = MaterialSpec
    extra = 0


class RegulationMappingInline(admin.StackedInline):
    model = RegulationMapping
    extra = 0


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display  = ["name", "material_group", "material_subtype", "ks_code", "ks_grade", "diameter", "category", "is_seismic", "is_weldable"]
    list_filter   = ["material_group", "material_subtype", "category", "ks_grade", "is_seismic"]
    search_fields = ["name", "ks_code", "ks_grade", "material_subtype"]
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


@admin.register(CategoryContractHistory)
class CategoryContractHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "supplier", "material_category", "contract_name", "contract_date",
        "mapping_status", "mapping_reason",
    ]
    list_filter = ["material_category", "mapping_status", "source_api", "contract_date"]
    search_fields = ["supplier__name", "contract_name", "external_id", "keyword"]
    date_hierarchy = "contract_date"


@admin.register(Demand)
class DemandAdmin(admin.ModelAdmin):
    list_display  = ["site_name", "owner", "material", "quantity", "deadline", "created_at"]
    list_filter   = ["deadline"]
    search_fields = ["site_name", "owner__email"]


@admin.register(SupplierMaterialRegistration)
class SupplierMaterialRegistrationAdmin(admin.ModelAdmin):
    list_display = ["supplier_name", "owner", "material_name", "standard", "recent_price", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["supplier_name", "owner__email", "material_name", "standard"]
