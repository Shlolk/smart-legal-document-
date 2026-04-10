# Design System Documentation

## 1. Overview & Creative North Star: "The Sovereign Intelligence"

This design system is engineered to bridge the gap between institutional authority and the frontier of Artificial Intelligence. We move beyond the static, "form-heavy" nature of traditional government portals to create a **"Sovereign Intelligence"**—a digital environment that feels as stable as a constitutional pillar but as fluid as a modern AI engine.

**The Creative North Star:** *The Sovereign Intelligence.*
This concept balances the weight of civic duty with the clarity of technological foresight. We achieve this through "Editorial Weight"—using high-contrast typography, expansive white space, and a layered, glass-like depth that suggests transparency and modern governance. We reject the "boxed-in" layout of legacy portals in favor of asymmetric compositions and organic depth.

---

## 2. Color Theory & Tonal Architecture

Our palette is rooted in patriotic tradition but refined through a premium, digital-first lens. We utilize a sophisticated "Sovereign Blue" foundation complemented by the "Dharmic Saffron" and "Growth Green" of the national identity.

### The "No-Line" Rule
To maintain a high-end, editorial feel, **1px solid borders are strictly prohibited for sectioning.** Boundaries must be defined through background color shifts or tonal transitions.
*   *Implementation:* Use `surface-container-low` for secondary sections sitting atop a `surface` background. The change in hex value provides the boundary, not a stroke.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. Use the `surface-container` tiers to create "stacked" importance.
*   **Surface Lowest (#ffffff):** Reserved for primary interactive cards and modals.
*   **Surface Low (#f3f3f9):** The standard canvas for main content areas.
*   **Surface High/Highest (#e7e8ee / #e2e2e8):** Used for navigation sidebars or utility panels to "recede" or "ground" the interface.

### The "Glass & Gradient" Rule
For AI-driven elements (like chat interfaces or real-time analysis), use **Glassmorphism**.
*   **Token:** `primary_container` (#0c2d57) at 80% opacity with a `24px` backdrop-blur. 
*   **Signature Texture:** Apply a subtle linear gradient (e.g., `primary` to `primary_container`) on hero sections to create a sense of infinite digital space.

---

## 3. Typography: Editorial Authority

We use **Inter** for its mathematical precision and neutral clarity. The hierarchy is designed to feel like a modern legal document: authoritative, yet highly readable.

*   **The Display Scale:** Use `display-lg` (3.5rem) for hero statements. This scale is intentionally oversized to convey power and "Digital Rights" prominence.
*   **The Title/Body Relationship:** 
    *   `title-lg` (1.375rem) serves as the "Clause Header"—bold and decisive.
    *   `body-lg` (1rem) is the workhorse for constitutional text, utilizing ample line-height (1.6) to ensure accessibility for all citizens.
*   **Labels:** `label-md` and `label-sm` are always set in All-Caps with a `0.05em` letter-spacing when used in navigation or metadata to mimic the "official document" stamp aesthetic.

---

## 4. Elevation, Depth & Ambient Light

Traditional shadows feel "heavy" and dated. We use **Tonal Layering** and **Ambient Shadows** to create a premium sense of lift.

### The Layering Principle
Depth is achieved by stacking:
1.  **Level 0 (Base):** `surface` (#f9f9ff)
2.  **Level 1 (Section):** `surface-container-low` (#f3f3f9)
3.  **Level 2 (Interactive Card):** `surface-container-lowest` (#ffffff)

### Ambient Shadows
When an element must float (e.g., an AI suggestion card), use an expanded, low-opacity shadow:
*   **Shadow Specs:** `0px 20px 40px rgba(0, 27, 61, 0.06)`. 
*   **Note:** The shadow color is a tint of `on_primary_fixed` (#001b3d), not pure black. This makes the shadow feel like it’s reflecting the environment.

### The "Ghost Border" Fallback
If accessibility requires a border (e.g., Input Fields), use a **Ghost Border**:
*   **Token:** `outline-variant` (#c4c6d0) at **20% opacity**. It should be felt, not seen.

---

## 5. Signature Components

### Buttons: The "Sovereign" Action
*   **Primary:** Solid `primary_container` (#0c2d57) with `on_primary` text.
*   **Secondary:** Glassmorphic style. Background: `primary` at 10% opacity, no border, `primary` text.
*   **Interactive State:** On hover, primary buttons should exhibit a "Hover Glow" using a subtle outer glow of `primary_fixed_dim` (#acc7fa).

### Cards: The "Constitutional" Module
*   **Construction:** Zero borders. Background: `surface-container-lowest`. 
*   **Interaction:** "Card Lifting" effect. On hover, the card translates `-4px` Y-axis and the Ambient Shadow opacity increases from 6% to 12%.
*   **Content Separation:** Use vertical white space (`2rem` - `3rem`) instead of dividers to separate sections.

### Input Fields: The "Secure Entry"
*   **Style:** Minimalist. Only a bottom "Ghost Border" is used by default. On focus, the border transitions to a `2px` solid `secondary` (Saffron) to symbolize the "spark" of citizen engagement.

### AI Engine Chips
*   **Visual:** Use `tertiary_container` (#013600) with `on_tertiary_container` (#3eaa2e) for status indicators. This "Green" represents the health and legality of the AI engine's results.

---

## 6. Do’s and Don’ts

### Do:
*   **Use Intentional Asymmetry:** Align the main text to a 12-column grid, but allow AI-generated insights or "Guardian" sidebars to float slightly off-axis.
*   **Embrace Breathing Room:** If you think there is enough margin, add 20% more. Premium design requires "Oxygen."
*   **Prioritize High Contrast:** Ensure all `on_surface` text meets WCAG AAA standards against its respective surface container.

### Don't:
*   **Don't use Divider Lines:** Never use a horizontal rule to separate list items. Use a background shift (`surface-container-low` vs `surface`) or increased spacing.
*   **Don't use Standard Drop Shadows:** Avoid "blurry black" shadows. If it doesn't look like light passing through glass or paper, refine the opacity.
*   **Don't Overuse Saffron:** The Saffron accent (`secondary`) is a "High-Value Indicator." Use it only for critical CTAs or focus states, never for large background areas.