"""Check binary STL topology without building a BREP for every triangle."""
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


def inspect_stl(path):
    raw = Path(path).read_bytes()
    count = int.from_bytes(raw[80:84], 'little')
    assert len(raw) == 84 + 50 * count
    dtype = np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
    triangles = np.frombuffer(raw, dtype=dtype, offset=84)['vertices'].astype(float)
    _, ids = np.unique(np.round(triangles.reshape(-1,3), 6), axis=0, return_inverse=True)
    faces = ids.reshape(-1,3)
    # Collapse sub-micron seams and ignore triangles collapsed by STL float32.
    faces = faces[(faces[:,0]!=faces[:,1]) & (faces[:,1]!=faces[:,2]) & (faces[:,2]!=faces[:,0])]
    directed = np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    edges, inverse, counts = np.unique(np.sort(directed,axis=1),axis=0,return_inverse=True,return_counts=True)
    winding = np.bincount(inverse,weights=np.where(directed[:,0]<directed[:,1],1,-1))
    graph = coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(ids.max()+1,)*2)
    components = connected_components(graph,directed=False,return_labels=False)
    volume = np.einsum('ij,ij->i',triangles[:,0],np.cross(triangles[:,1],triangles[:,2])).sum()/6
    points = triangles.reshape(-1, 3)
    return dict(valid=bool(np.all(counts==2) and np.all(winding==0)),solids=int(components),volumeMm3=float(volume),triangles=count,topologyToleranceMm=1e-6,
                boundsMm=[points.min(axis=0).tolist(), points.max(axis=0).tolist()])
