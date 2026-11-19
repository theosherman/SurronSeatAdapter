"""Display the split adapter with two seated keys in OCP CAD Viewer."""
from pathlib import Path

from build123d import import_step
from ocp_vscode import Camera, set_port, show


def main():
    exports = Path(__file__).resolve().parent / "exports"
    front = import_step(exports / "adapter-body-split-front.step")
    rear = import_step(exports / "adapter-body-split-rear.step")
    top_key = import_step(exports / "butterfly-key-top.step")
    cavity_key = import_step(exports / "butterfly-key-cavity.step")
    set_port(3939)
    show(
        front,
        rear,
        top_key,
        cavity_key,
        names=["Front", "Rear", "Top key", "Cavity key (negative X)"],
        colors=["steelblue", "orange", "mediumseagreen", "mediumseagreen"],
        reset_camera=Camera.RESET,
    )


if __name__ == "__main__":
    main()
