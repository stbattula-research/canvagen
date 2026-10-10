"""`canvagen` command-line interface."""
from __future__ import annotations

import argparse
import json
import sys


def cmd_auth(args):
    from .auth import run_auth_flow
    run_auth_flow(args.client_id, args.client_secret)
    print("Connected. Tokens stored in ~/.config/canvagen/tokens.json")


def cmd_imagine(args):
    from .generate import imagine, download_image
    image = imagine(args.prompt, aspect_ratio=args.aspect_ratio, model=args.model,
                    save_to_canva=args.save, asset_name=args.name)
    dest = args.output or f"canvagen-{image['width']}x{image['height']}.png"
    download_image(image, dest)
    print(json.dumps({"file": dest, "width": image["width"],
                      "height": image["height"],
                      "asset": image.get("asset", {}).get("id")}, indent=2))


def cmd_design_create(args):
    from .designs import create_design
    print(json.dumps(create_design(args.title, args.type), indent=2))


def cmd_template_fields(args):
    from .designs import template_dataset
    print(json.dumps(template_dataset(args.template_id), indent=2))


def cmd_autofill(args):
    from .designs import autofill, export_design, download_export
    data = json.loads(args.data)
    design = autofill(args.template_id, data)
    print(json.dumps({"design_id": design["id"],
                      "url": design.get("urls", {}).get("edit_url")}, indent=2))
    if args.export:
        for i, exp in enumerate(export_design(design["id"], args.export)):
            dest = f"canvagen-autofill-p{i+1}.{args.export}"
            download_export(exp, dest)
            print("saved", dest)


def cmd_export(args):
    from .designs import export_design, download_export
    for i, exp in enumerate(export_design(args.design_id, args.format)):
        dest = args.output or f"canvagen-export-p{i+1}.{args.format}"
        download_export(exp, dest)
        print("saved", dest)


def main(argv=None):
    p = argparse.ArgumentParser(prog="canvagen",
                                description="Generate images and designs via Canva")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("auth", help="Connect your Canva account (one-time)")
    a.add_argument("--client-id", required=True)
    a.add_argument("--client-secret", default=None)
    a.set_defaults(fn=cmd_auth)

    im = sub.add_parser("imagine", help="Generate an image from a text prompt")
    im.add_argument("prompt")
    im.add_argument("--aspect-ratio", default="square",
                    choices=["square", "landscape", "portrait"])
    im.add_argument("--model", default=None,
                    choices=["lucid_origin", "z_image_turbo"],
                    help="omit to let Canva pick")
    im.add_argument("--save", action="store_true",
                    help="also save to your Canva uploads")
    im.add_argument("--name", default=None)
    im.add_argument("--output", "-o", default=None)
    im.set_defaults(fn=cmd_imagine)

    dc = sub.add_parser("design-create", help="Create a blank design")
    dc.add_argument("--title", required=True)
    dc.add_argument("--type", default="doc")
    dc.set_defaults(fn=cmd_design_create)

    tf = sub.add_parser("template-fields",
                        help="List autofillable fields of a brand template")
    tf.add_argument("template_id")
    tf.set_defaults(fn=cmd_template_fields)

    af = sub.add_parser("autofill", help="Fill a brand template with data")
    af.add_argument("template_id")
    af.add_argument("--data", required=True,
                    help='JSON object, e.g. \'{"name":"Ava"}\'')
    af.add_argument("--export", default=None, choices=["png", "jpg", "pdf"])
    af.set_defaults(fn=cmd_autofill)

    ex = sub.add_parser("export", help="Export a design to a file")
    ex.add_argument("design_id")
    ex.add_argument("--format", default="png", choices=["png", "jpg", "pdf"])
    ex.add_argument("--output", "-o", default=None)
    ex.set_defaults(fn=cmd_export)

    args = p.parse_args(argv)
    try:
        args.fn(args)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
