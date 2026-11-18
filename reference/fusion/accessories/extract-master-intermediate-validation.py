import adsk.core, adsk.fusion, json

def point(p): return [v*10 for v in p.asArray()]

def run(_context: str):
    d=adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    old=d.timeline.markerPosition
    out={'units':'millimeter','volumeUnit':'mm^3','sourceDocument':adsk.core.Application.get().activeDocument.name,'markerBefore':old,'stages':[]}
    try:
        c=next(c for c in d.allComponents if c.name=='AdapterBody')
        for index in [77,82,84,86,87,89,91,97,98,121,122,124,126]:
            t=d.timeline.item(index)
            t.rollTo(False)
            out['stages'].append({'afterIndex':index,'timelineName':t.name,'bodies':[{'name':b.name,'volumeMm3':b.volume*1000,'areaMm2':b.area*100,'centerOfMassMm':point(b.physicalProperties.centerOfMass),'boundingBoxMm':[point(b.boundingBox.minPoint),point(b.boundingBox.maxPoint)],'solid':b.isSolid,'faceCount':b.faces.count,'edgeCount':b.edges.count} for b in c.bRepBodies]})
    finally:
        d.timeline.markerPosition=old
    out['markerAfter']=d.timeline.markerPosition
    print(json.dumps(out))
