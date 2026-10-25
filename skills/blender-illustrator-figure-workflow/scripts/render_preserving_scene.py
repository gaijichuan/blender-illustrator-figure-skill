"""Run in a fresh background Blender process; never saves the input blend file."""
import argparse
import json
import sys
import time
from pathlib import Path


def load_jobs(manifest):
    manifest = Path(manifest).resolve()
    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    jobs = data.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("jobs must be a non-empty list")
    result, outputs = [], set()
    for item in jobs:
        source = (manifest.parent / item["source"]).resolve()
        output = (manifest.parent / item["output"]).resolve()
        if not source.is_file() or source.suffix.lower() != ".blend":
            raise ValueError(f"Missing .blend source: {source}")
        if output.suffix.lower() != ".png" or output in outputs:
            raise ValueError(f"Output must be a unique PNG: {output}")
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite: {output}")
        width, height = item["resolution"]
        if any(type(v) is not int or v <= 0 for v in (width, height)):
            raise ValueError("resolution must contain two positive integers")
        samples = item.get("samples")
        if samples is not None and (type(samples) is not int or samples <= 0):
            raise ValueError("samples must be a positive integer")
        outputs.add(output)
        result.append(dict(source=source, output=output, width=width,
                           height=height, samples=samples, scene=item.get("scene")))
    return result


def snapshot(scene):
    def matrix(o):
        return [list(row) for row in o.matrix_world]
    cam = scene.camera
    return {
        "engine": scene.render.engine,
        "camera": cam.name if cam else None,
        "camera_matrix": matrix(cam) if cam else None,
        "lens": cam.data.lens if cam else None,
        "ortho_scale": cam.data.ortho_scale if cam else None,
        "dof": {"enabled": cam.data.dof.use_dof,
                "distance": cam.data.dof.focus_distance,
                "fstop": cam.data.dof.aperture_fstop,
                "focus_object": cam.data.dof.focus_object.name
                if cam.data.dof.focus_object else None} if cam else None,
        "world": scene.world.name if scene.world else None,
        "film_transparent": scene.render.film_transparent,
        "view_transform": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "exposure": scene.view_settings.exposure,
        "gamma": scene.view_settings.gamma,
        "lights": [{"name": o.name, "type": o.data.type,
                    "energy": o.data.energy, "color": list(o.data.color),
                    "matrix": matrix(o)} for o in scene.objects if o.type == "LIGHT"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--cpu", action="store_true", help="Override Cycles device only")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    jobs = load_jobs(args.manifest)
    if args.validate_only:
        print(f"Validated {len(jobs)} jobs; source files not opened")
        return
    import bpy
    for job in jobs:
        started = time.monotonic()
        bpy.ops.wm.open_mainfile(filepath=str(job["source"]))
        scene = bpy.data.scenes.get(job["scene"]) if job["scene"] else bpy.context.scene
        if scene is None or scene.camera is None:
            raise ValueError("Requested scene or its active camera is missing")
        if job["samples"] is not None and scene.render.engine != "CYCLES":
            raise ValueError("samples override is supported only for Cycles")
        if args.cpu and scene.render.engine != "CYCLES":
            raise ValueError("--cpu is a Cycles-only override")
        before = snapshot(scene)
        if args.cpu:
            scene.cycles.device = "CPU"
        if job["samples"] is not None:
            scene.cycles.samples = job["samples"]
        # Preserve lighting, color management, materials, compositing and transparency.
        scene.render.resolution_x = job["width"]
        scene.render.resolution_y = job["height"]
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.image_settings.color_depth = "8"
        scene.render.filepath = str(job["output"])
        if scene.render.use_border:
            raise ValueError("Render border enabled; review framing before HD export")
        # Avoid unrequested writes from existing compositor File Output nodes.
        tree = getattr(scene, "node_tree", None)
        if tree and any(n.bl_idname == "CompositorNodeOutputFile" and not n.mute
                        for n in tree.nodes):
            raise ValueError("Active compositor File Output node: review outputs first")
        if snapshot(scene) != before:
            raise RuntimeError("Scene appearance settings changed unexpectedly")
        job["output"].parent.mkdir(parents=True, exist_ok=True)
        if job["output"].exists():
            raise FileExistsError(job["output"])
        report_path = job["output"].with_suffix(".render.json")
        if report_path.exists():
            raise FileExistsError(report_path)
        print(f"START {job['output'].name}", flush=True)
        bpy.ops.render.render(write_still=True, scene=scene.name)
        if not job["output"].is_file() or snapshot(scene) != before:
            raise RuntimeError("Output missing or scene appearance changed during render")
        report = dict(source=str(job["source"]), output=str(job["output"]),
                      resolution=[job["width"], job["height"]],
                      seconds=round(time.monotonic()-started, 2), appearance=before,
                      samples=scene.cycles.samples if scene.render.engine == "CYCLES" else None)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"DONE {job['output'].name}", flush=True)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
    main(argv)
