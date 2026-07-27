#!/usr/bin/env python3
"""Apply strict Inertia 3 / React 19 compatibility fixes to the extracted v1.7.1 source.

The runtime builder intentionally keeps the original signed source archive immutable.
This script applies deterministic, validated source migrations before typecheck/build.
"""

from pathlib import Path


def replace_exact(path: str, old: str, new: str, expected: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(
            f"{path}: expected {expected} occurrence(s) of {old!r}, found {count}"
        )
    file.write_text(text.replace(old, new), encoding="utf-8")


# Seller metadata comes from a broad API type, while the submitted form must contain
# only FormData-convertible scalar values.
replace_exact(
    "resources/js/pages/Admin/Sellers/Edit.tsx",
    "metadata: seller?.metadata ?? {},",
    "metadata: (seller?.metadata ?? {}) as SellerForm['metadata'],",
)

# HTML select values are strings; these two form fields are numeric IDs.
replace_exact(
    "resources/js/pages/Collaboration/Dashboard.tsx",
    "form.setData('owner_id',e.target.value)",
    "form.setData('owner_id',Number(e.target.value))",
)
replace_exact(
    "resources/js/pages/Collaboration/Dashboard.tsx",
    "create.setData('current_approver_id',e.target.value)",
    "create.setData('current_approver_id',Number(e.target.value))",
)

# Laravel may return form-level error keys that are intentionally not data fields.
replace_exact(
    "resources/js/pages/Installer/Index.tsx",
    "form.errors.installation",
    "(form.errors as unknown as Record<string, string | undefined>).installation",
    expected=2,
)
replace_exact(
    "resources/js/pages/Storefront/Checkout/Index.tsx",
    "form.errors.checkout",
    "(form.errors as unknown as Record<string, string | undefined>).checkout",
    expected=2,
)

# React img src accepts undefined but not null.
replace_exact(
    "resources/js/pages/Member/Orders/Show.tsx",
    "src={item.cover_image_url}",
    "src={item.cover_image_url ?? undefined}",
)
replace_exact(
    "resources/js/pages/Storefront/OriginMap.tsx",
    "src={origin.image_url}",
    "src={origin.image_url ?? undefined}",
)
replace_exact(
    "resources/js/pages/Storefront/OriginMap.tsx",
    "src={product.cover_image_url}",
    "src={product.cover_image_url ?? undefined}",
)

# MapLibre v5 expects false or an AttributionControlOptions object.
replace_exact(
    "resources/js/pages/Storefront/OriginMap.tsx",
    "attributionControl:true",
    "attributionControl:{compact:true}",
)

print("Applied strict Inertia 3 compatibility fixes.")
