"""Display the two saved adapter halves in OCP CAD Viewer."""
from pathlib import Path

from build123d import import_step
from ocp_vscode import Camera, set_port, show


def main():
    exports = Path(__file__).resolve().parent / "exports"
    front = import_step(exports / "adapter-body-split-front.step")
    rear = import_step(exports / "adapter-body-split-rear.step")
    set_port(3939)
    show(
        front,
        rear,
        names=["Front", "Rear"],
        colors=["steelblue", "orange"],
        reset_camera=Camera.RESET,
    )


if __name__ == "__main__":
    main()
