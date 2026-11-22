# Website asset sources

## Donor kit photograph

- Asset: `site/solar-car-assets/donor-kit.webp`.
- Product: SICWUD wooden solar car kit, Solar car variant.
- Source: [Temu product 606027684660893, SKU 93361448944809](https://www.temu.com/goods.html?goods_id=606027684660893&sku_id=93361448944809).
- [Original listing image](https://img.kwcdn.com/product/open/f1f432b5b775418c9529f59d03cad2c9-goods.jpeg).
- Checked on November 22, 2026. The builder confirmed this as the kit purchased for the project.
- Resized to 800 × 800 and encoded as WebP. No objects were added or removed.
- This third-party product photo identifies the donor kit. Rights remain with its owner; **it is not licensed under this repository's MIT license**. Attribution is also displayed beside the photo on the website.

The public link contains only product and variant identifiers. Private order and session parameters are not published.

## Video poster

`site/solar-car-assets/video-poster.webp` is a real frame from Anton Pechenko's footage at approximately 00:04. It was tone-mapped from HDR to SDR and scaled to 1600 × 900. No generated imagery was used. The [published video](https://youtu.be/IwpP_UVUebM) remains on YouTube.

## Exploded assembly view

`site/solar-car-assets/assembly-exploded.webp` and `docs/assembly-exploded.png` are rendered by `scripts/render_exploded.py` using the released `models/step/assembly-reference.step` (V2.10 chassis and BF5 frames/posts). Only display positions are changed. Printed geometry is unchanged.

The motor, pinion envelope, axle gear envelope, axles and wheels are schematic references. Gear teeth, wiring and the cable tie are omitted. Numbered callouts correspond to the translated HTML legend. F1/F2/R1/R2 identify post types, with two of each.

## Separate component listings

The website and README use direct marketplace product links:

- [RF-300CA-09550 motor on AliExpress](https://www.aliexpress.com/item/1005006061376932.html), sold by Motor Studio Store. The seller’s dimension drawing shows a Ø24.3 × 12.4 mm body and 6.2 mm exposed shaft; the product title lists 1.5–6 V. The selected listing has no gear included.
- [GUDYIR wheels and axles on Temu](https://www.temu.com/goods.html?goods_id=601102406768026). The product description lists 8 wheels (Ø30 × 10 mm, fitting 2 mm shafts) and 4 steel axles (Ø2 × 100 mm).
- [ALLMEJORES panels on AliExpress](https://www.aliexpress.com/item/1005012060244981.html), sold by MSL Solar Company Store. The title and specification table list 55 × 55 mm, 2 V, 5 panels per pack, with wires. Thickness is not specified.
- [102A Long motor pinion on AliExpress](https://www.aliexpress.com/item/32963402664.html), sold by Pinion Parts Store. Title and selected options: module 0.5, 10 teeth, “2mm Tight”, 10 pieces per lot. The annotated seller photograph shows Ø5.97 mm, length 9.2 mm and bore 1.96 mm.
- [502A axle gear on AliExpress](https://www.aliexpress.com/item/32967309928.html), sold by Pinion Parts Store. Title and selected options: module 0.5, 50 teeth, “2mm Tight”, 10 pieces per lot. The annotated seller photograph shows Ø26 mm, tooth face width 1.6 mm, total width 4.4 mm and bore 1.95 mm.

Checked in the shared browser on November 22, 2026. Dimensions come from seller text, product options and annotated product images, not from AliExpress’s AI-generated overview. These components have not been tested in the car. The motor differs slightly from the donor dimensions, and panel thickness/electrical compatibility remain unverified. No price, availability or drop-in compatibility promise is made. Public URLs contain only product identifiers.

The proposed 10/50-tooth gear pairing is an engineering inference from the listed module and tooth counts, the recorded donor gear diameters and the chassis's tested 15 mm center distance. The standard center-distance formula and the need for matching module and pressure angle are supported by [KHK's spur gear technical reference](https://khkgears.net/pdf/spur-tech.pdf). The AliExpress pressure-angle fields contain “0.5M”, which is a module designation, not a usable angle. The candidate pair still needs a mesh and fit check; it does not establish the original large gear's tooth count. Gear product photos were inspected for dimensions and are not redistributed in this repository.
