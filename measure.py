"""Adaptive volume integration for curved fillet surfaces (mm³)."""
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps


def volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-9, True, False)
    return props.Mass()
