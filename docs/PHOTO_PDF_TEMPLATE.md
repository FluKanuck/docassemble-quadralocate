# Photo Page PDF Template — Image Field Requirements

## Issue: Photos Not Appearing in Exported PDF

**Root cause (confirmed via runtime logs):** Docassemble only places images into **Signature (/Sig)** form fields.Push Button fields with "Icon only" layout (**/Btn**) are **not** supported for image placement by docassemble's PDF filler.

## Required Fix for `photo_page.pdf`

The fields `photo_1`, `photo_2`, ... `photo_6` must be **Signature** fields, not Push Button fields.

### Steps in Adobe Acrobat Pro

1. Open `photo_page.pdf` in Acrobat Pro.
2. Go to **Tools → Prepare Form** (or **Forms → Edit**).
3. For each of `photo_1` through `photo_6`:
   - **If the field is a Push Button:** Delete it and create a new **Signature** field in the same position.
   - **If the field is already a Signature field:** No change needed.
4. Set each field name exactly to: `photo_1`, `photo_2`, `photo_3`, `photo_4`, `photo_5`, `photo_6`.
5. Size each signature field to the desired photo area.
6. Save the PDF.

### Same Requirement for Cover Photo

If `cover_page.pdf` has a cover photo field, it must also be a **Signature** field (not Push Button). The field name should match what `get_cover_fields()` uses: `cover_photo`.

## How Docassemble Handles Images

- Values passed as `[FILE reference]` (or DAFile objects that stringify to that) are routed to the `images` list.
- The PDF filler overlays images **only** onto fields with type `/Sig` (signature).
- Push Button (`/Btn`) fields are treated as checkboxes and cannot receive image overlays.

## Verification

After updating the template:

1. Run the interview and upload at least one photo.
2. Generate and download the PDF report.
3. Confirm the photo(s) appear in the photo page(s).
