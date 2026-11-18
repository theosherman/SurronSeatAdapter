import adsk.core,adsk.fusion,json

def curve(g):
    out={'type':g.objectType}
    if isinstance(g,adsk.core.Line3D):
        out.update(start=g.startPoint.asArray(),end=g.endPoint.asArray())
    elif isinstance(g,adsk.core.Arc3D):
        ok,a,b=g.evaluator.getParameterExtents()
        ok,m=g.evaluator.getPointAtParameter((a+b)/2)
        out.update(start=g.startPoint.asArray(),mid=m.asArray(),end=g.endPoint.asArray(),center=g.center.asArray(),radius=g.radius)
    elif isinstance(g,adsk.core.Circle3D):
        out.update(center=g.center.asArray(),radius=g.radius)
    else:
        ok,a,b=g.evaluator.getParameterExtents()
        ok,points=g.evaluator.getStrokes(a,b,0.0001)
        out.update(points=[p.asArray() for p in points],approximationToleranceCm=0.0001)
    return out

def run(_context: str):
    d=adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    old=d.timeline.markerPosition
    out={'units':'cm','features':[],'datums':[]}
    try:
        for i in [9,12,14,18,75,76,77,79,84,86,89,91,97,121,124,126,186,188,194,195]:
            t=d.timeline.item(i)
            t.rollTo(True)
            f=t.entity
            if i==186:
                c=next(c for c in d.allComponents if c.name=='AdapterBodySplit')
                f=next(f for f in c.features if f.name=='Extrude1')
            ps=f.profile
            if not isinstance(ps,adsk.core.ObjectCollection): ps=[ps]
            row={'index':i,'timelineName':t.name,'featureName':f.name,'profiles':[]}
            for p in ps:
                if not isinstance(p,adsk.fusion.Profile): continue
                ap=p.areaProperties()
                row['profiles'].append({'sketch':p.parentSketch.name,'areaCm2':ap.area,'centroid':ap.centroid.asArray(),'loops':[{'outer':loop.isOuter,'curves':[curve(c.geometry) for c in loop.profileCurves]} for loop in p.profileLoops]})
            out['features'].append(row)
        for i in [80,87]:
            t=d.timeline.item(i)
            t.rollTo(True)
            f=t.entity
            pl=f.plane.geometry
            out['datums'].append({'index':i,'name':t.name,'type':'draft','angleRadians':f.draftDefinition.angle.value,'isDirectionFlipped':f.isDirectionFlipped,'neutralPlaneOrigin':pl.origin.asArray(),'neutralPlaneNormal':pl.normal.asArray(),'faces':[{'point':face.pointOnFace.asArray(),'type':face.geometry.objectType,'normal':face.geometry.normal.asArray() if isinstance(face.geometry,adsk.core.Plane) else None} for face in f.inputFaces]})
    finally:
        d.timeline.markerPosition=old
    print(json.dumps(out))

