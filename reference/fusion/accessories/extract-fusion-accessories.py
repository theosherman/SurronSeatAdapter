"""Inspect Latch and SaddleBagMount; roll timeline temporarily, restore in finally.
No CAD geometry is created, changed, deleted, or saved. Raw lengths cm, angles rad.
Run through Fusion MCP script with readOnly omitted because timeline rolling is required.
"""
import adsk.core, adsk.fusion, json

ERRORS = []

def get(obj, name, default=None):
    try:
        return getattr(obj, name)
    except Exception as exc:
        ERRORS.append({'objectType':getattr(obj,'objectType',str(type(obj))), 'property':name,'error':str(exc)})
        return default

def xyz(p):
    return p.asArray() if p else None

def parameter(p):
    if p is None: return None
    return {'name':p.name,'expression':p.expression,'value':p.value,'unit':p.unit}

def plane(g):
    if isinstance(g,adsk.core.Plane): return {'origin':xyz(g.origin),'normal':xyz(g.normal)}
    return {'type':g.objectType}

def geom(g):
    out={'type':g.objectType}
    if isinstance(g,adsk.core.Line3D): out.update(start=xyz(g.startPoint),end=xyz(g.endPoint))
    elif isinstance(g,adsk.core.Arc3D):
        ok,a,b=g.evaluator.getParameterExtents()
        ok,m=g.evaluator.getPointAtParameter((a+b)/2)
        out.update(start=xyz(g.startPoint),mid=xyz(m),end=xyz(g.endPoint),center=xyz(g.center),radius=g.radius,normal=xyz(g.normal))
    elif isinstance(g,adsk.core.Circle3D): out.update(center=xyz(g.center),radius=g.radius,normal=xyz(g.normal))
    elif isinstance(g,(adsk.core.EllipticalArc3D,adsk.core.Ellipse3D)):
        out.update(center=xyz(g.center),normal=xyz(g.normal),majorAxis=xyz(g.majorAxis),majorRadius=g.majorRadius,minorRadius=g.minorRadius)
        if isinstance(g,adsk.core.EllipticalArc3D): out.update(startAngle=g.startAngle,endAngle=g.endAngle)
    elif isinstance(g,adsk.core.Plane): out.update(plane(g))
    elif isinstance(g,adsk.core.Cylinder): out.update(origin=xyz(g.origin),axis=xyz(g.axis),radius=g.radius)
    else:
        ev=get(g,'evaluator')
        if ev:
            ok,a,b=ev.getParameterExtents()
            ok,pts=ev.getStrokes(a,b,0.0001)
            out.update(points=[xyz(p) for p in pts],approximationToleranceCm=0.0001)
    return out

def ref(e):
    if e is None: return None
    out={'type':e.objectType}
    if hasattr(e,'name'): out['name']=e.name
    if isinstance(e,adsk.fusion.SketchCurve):
        out.update(sketch=e.parentSketch.name,curve=next((i for i,c in enumerate(e.parentSketch.sketchCurves) if c==e),None))
    elif isinstance(e,adsk.fusion.SketchPoint): out.update(point=xyz(e.geometry))
    elif isinstance(e,adsk.fusion.BRepFace):
        out.update(body=e.body.name,component=e.body.parentComponent.name,point=xyz(e.pointOnFace),area=e.area,geometry=geom(e.geometry),isParamReversed=e.isParamReversed)
    elif isinstance(e,adsk.fusion.BRepEdge): out.update(body=e.body.name,length=e.length,geometry=geom(e.geometry))
    elif isinstance(e,adsk.fusion.ConstructionPlane): out['plane']=plane(e.geometry)
    elif hasattr(e,'timelineObject'): out['index']=e.timelineObject.index
    return out

def items(obj):
    if obj is None: return []
    if isinstance(obj,(list,tuple,adsk.core.ObjectCollection)): return list(obj)
    if hasattr(obj,'count') and hasattr(obj,'item'): return [obj.item(i) for i in range(obj.count)]
    return [obj]

def profiles(obj):
    result=[]
    for p in items(obj):
        if isinstance(p,adsk.fusion.Profile):
            a=p.areaProperties()
            result.append({'sketch':p.parentSketch.name,'areaCm2':a.area,'centroid':xyz(a.centroid),'loops':[{'outer':loop.isOuter,'curves':[geom(c.geometry) for c in loop.profileCurves]} for loop in p.profileLoops]})
        else: result.append({'nonSketchProfile':ref(p)})
    return result

def extent(e):
    if e is None: return None
    out={'type':e.objectType}
    for k in ['distance','offset','angle','wallThickness']:
        if hasattr(e,k): out[k]=parameter(get(e,k))
    for k in ['direction','isSymmetric','isFullLength','isChained','isMinimumSolution','isPositiveDirection']:
        if hasattr(e,k): out[k]=get(e,k)
    for k in ['entity']:
        if hasattr(e,k): out[k]=ref(get(e,k))
    if hasattr(e,'directionHint'): out['directionHint']=xyz(get(e,'directionHint'))
    if hasattr(e,'profilePlane'): out['profilePlane']=plane(e.profilePlane)
    return out

def sketch(s):
    curves=[]
    for i,c in enumerate(s.sketchCurves):
        curves.append({'index':i,'type':c.objectType,'construction':c.isConstruction,'reference':c.isReference,'geometry':geom(c.geometry)})
    constraints=[]
    for c in s.geometricConstraints:
        row={'type':c.objectType}
        for k in ['entityOne','entityTwo','entityThree','line','lineOne','lineTwo','point','pointOne','pointTwo','curve','symmetryLine']:
            if hasattr(c,k): row[k]=ref(get(c,k))
        constraints.append(row)
    return {'name':s.name,'index':s.timelineObject.index,'origin':xyz(s.origin),'xAxis':xyz(s.xDirection),'yAxis':xyz(s.yDirection),'referencePlane':ref(get(s,'referencePlane')),'isFullyConstrained':s.isFullyConstrained,'curves':curves,'dimensions':[{'type':v.objectType,'parameter':parameter(v.parameter),'isDriving':v.isDriving} for v in s.sketchDimensions],'constraints':constraints}

def bodies(c):
    return [{'name':b.name,'isSolid':b.isSolid,'volumeCm3':b.volume,'areaCm2':b.area,'boundingBox':[xyz(b.boundingBox.minPoint),xyz(b.boundingBox.maxPoint)],'faceCount':b.faces.count,'edgeCount':b.edges.count} for b in c.bRepBodies]

def feature(f):
    out={'name':f.name,'index':f.timelineObject.index,'type':f.objectType,'healthState':f.healthState,'message':f.errorOrWarningMessage}
    if isinstance(f,adsk.fusion.ExtrudeFeature):
        out.update(operation=get(f,'operation'),extentType=get(f,'extentType'),extentOne=extent(get(f,'extentOne')),extentTwo=extent(get(f,'extentTwo')),startExtent=extent(get(f,'startExtent')),taperOne=parameter(get(f,'taperAngleOne')),taperTwo=parameter(get(f,'taperAngleTwo')),profiles=profiles(f.profile),participantBodies=[b.name for b in get(f,'participantBodies',[])])
    elif isinstance(f,adsk.fusion.MirrorFeature): out.update(inputEntities=[ref(e) for e in f.inputEntities],mirrorPlane=ref(f.mirrorPlane),isCombine=f.isCombine,computeOption=f.patternComputeOption)
    elif isinstance(f,adsk.fusion.OffsetFacesFeature): out.update(distance=parameter(f.distance),inputFaces=[ref(e) for e in f.inputFaces])
    elif isinstance(f,adsk.fusion.FilletFeature):
        out['sourceOnlyDoNotBuild']=True
        out['edgeSets']=[{'type':es.objectType,'radius':parameter(get(es,'radius')),'edges':[ref(e) for e in es.edges]} for es in f.edgeSets]
    else: out['unsupportedFeatureType']=True
    return out

def run(_context: str):
    app=adsk.core.Application.get()
    d=adsk.fusion.Design.cast(app.activeProduct)
    old=d.timeline.markerPosition
    result={'sourceDocument':app.activeDocument.name,'units':'cm','angleUnit':'radian','timelineIndices':'zero-based','markerBefore':old,'parts':[],'errors':ERRORS,'externalSketches':[],'masterEarlyStageValidation':[],'userParameters':[parameter(p) for p in d.userParameters]}
    try:
        adapter=next(c for c in d.allComponents if c.name=='AdapterBody')
        shared=next(s for s in adapter.sketches if s.name=='TrunkDovetailSketch')
        d.timeline.item(shared.timelineObject.index).rollTo(True)
        result['externalSketches'].append(dict(sketch(shared),component='AdapterBody'))
        d.timeline.markerPosition=old
        for index in [15,18]:
            d.timeline.item(index).rollTo(False)
            result['masterEarlyStageValidation'].append({'afterIndex':index,'bodies':bodies(adapter)})
            d.timeline.markerPosition=old
        for c in d.allComponents:
            if c.name not in ['Latch','SaddleBagMount']: continue
            row={'name':c.name,'sketches':[],'finalBodies':bodies(c),'parameters':[parameter(p) for p in c.modelParameters],'features':[],'occurrences':[{'name':o.fullPathName,'transform':o.transform2.asArray()} for o in d.rootComponent.allOccurrences if o.component==c]}
            for s in c.sketches:
                d.timeline.item(s.timelineObject.index).rollTo(True)
                row['sketches'].append(sketch(s))
                d.timeline.markerPosition=old
            featureList=sorted([(f.timelineObject.index,f.name) for f in c.features])
            for index,name in featureList:
                d.timeline.item(index).rollTo(True)
                f=next(f for f in c.features if f.name==name)
                fr=feature(f)
                fr['bodiesBefore']=bodies(c)
                d.timeline.item(index).rollTo(False)
                fr['bodiesAfter']=bodies(c)
                row['features'].append(fr)
            result['parts'].append(row)
            d.timeline.markerPosition=old
    finally:
        d.timeline.markerPosition=old
    result['markerAfter']=d.timeline.markerPosition
    print(json.dumps(result))


