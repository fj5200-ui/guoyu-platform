#!/usr/bin/env python3
"""Apply strict Inertia 3 / React 19 compatibility fixes to v1.7.1 sources.

The release source archive stays immutable. This migration is deterministic and
fails loudly when the expected source no longer matches, preventing silent drift.
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


def write_exact(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


write_exact(
    "resources/js/app.tsx",
    """import '../css/app.css';

import { createInertiaApp, type ResolvedComponent } from '@inertiajs/react';
import { createRoot } from 'react-dom/client';
import { Toaster } from 'sonner';

const pages = import.meta.glob<ResolvedComponent>('./pages/**/*.tsx');

createInertiaApp({
  strictMode: true,
  progress: { color: 'var(--brand-primary)' },
  resolve: (name) => {
    const resolvePage = pages[`./pages/${name}.tsx`];
    if (!resolvePage) throw new Error(`Page not found: ${name}`);
    return resolvePage();
  },
  setup({ el, App, props }) {
    if (!el) throw new Error('Inertia root element was not found.');
    createRoot(el).render(
      <>
        <App {...props} />
        <Toaster richColors position=\"top-center\" />
      </>,
    );
  },
});
""",
)

write_exact(
    "resources/js/ssr.tsx",
    """import { createInertiaApp, type ResolvedComponent } from '@inertiajs/react';
import createServer from '@inertiajs/react/server';
import ReactDOMServer from 'react-dom/server';

const pages = import.meta.glob<ResolvedComponent>('./pages/**/*.tsx');

createServer((page) =>
  createInertiaApp({
    page,
    render: ReactDOMServer.renderToString,
    resolve: (name) => {
      const resolvePage = pages[`./pages/${name}.tsx`];
      if (!resolvePage) throw new Error(`Inertia page not found: ${name}`);
      return resolvePage();
    },
    setup: ({ App, props }) => <App {...props} />,
  }),
);
""",
)

# Navigation form: remove recursively nested children and ensure all submitted
# visibility values are FormData-convertible scalars.
replace_exact(
    "resources/js/pages/Admin/Navigation/Index.tsx",
    "type NavRow = NavigationItem & { sort_order: number; is_active: boolean };",
    "type VisibilityValue = string | number | boolean | null;\n"
    "type NavRow = Omit<NavigationItem, 'children' | 'visibility'> & {\n"
    "  sort_order: number;\n"
    "  is_active: boolean;\n"
    "  visibility: Record<string, VisibilityValue>;\n"
    "};",
)
replace_exact(
    "resources/js/pages/Admin/Navigation/Index.tsx",
    "visibility: item.visibility ?? {},",
    "visibility: (item.visibility ?? {}) as Record<string, VisibilityValue>,",
)

# Seller metadata comes from a broad API type, while the submitted form must
# contain only FormData-convertible scalar values.
replace_exact(
    "resources/js/pages/Admin/Sellers/Edit.tsx",
    "metadata: Record<string, unknown>;",
    "metadata: Record<string, string | number | boolean | null>;",
)
replace_exact(
    "resources/js/pages/Admin/Sellers/Edit.tsx",
    "metadata: seller?.metadata ?? {},",
    "metadata: (seller?.metadata ?? {}) as SellerForm['metadata'],",
)

# HTML select values are strings; these form fields are numeric IDs.
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
