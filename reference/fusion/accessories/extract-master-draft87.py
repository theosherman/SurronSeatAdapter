import adsk.core, adsk.fusion, json

def point(p): return [v*10 for v in p.asArray()]

def face(f):
    g=f.geometry
    return {'pointMm':point(f.pointOnFace),'planeOriginMm':point(g.origin),'surfaceNormal':g.normal.asArray(),'isParamReversed':f.isParamReversed,'areaMm2':f.area*100,'verticesMm':[point(v.geometry) for v in f.vertices],'loops':[{'outer':loop.isOuter,'edges':[{'type':e.geometry.objectType,'startMm':point(e.startVertex.geometry) if e.startVertex else None,'endMm':point(e.endVertex.geometry) if e.endVertex else None} for e in loop.edges]} for loop in f.loops]}

def run(_context: str):
    d=adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    old=d.timeline.markerPosition
    out={'units':'millimeter','markerBefore':old,'stages':[]}
    try:
        c=next(c for c in d.allComponents if c.name=='AdapterBody')
        for index in [86,87]:
            d.timeline.item(index).rollTo(False)
            b=c.bRepBodies.item(0)
            out['stages'].append({'afterIndex':index,'volumeMm3':b.volume*1000,'planarFaces':[face(f) for f in b.faces if isinstance(f.geometry,adsk.core.Plane)]})
    finally:
        d.timeline.markerPosition=old
    out['markerAfter']=d.timeline.markerPosition
    print(json.dumps(out))
