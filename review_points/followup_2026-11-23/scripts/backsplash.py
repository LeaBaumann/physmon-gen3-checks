"""Collector secondaries and tracker hits from secondaries born outside the tracker.

Usage: python3 backsplash.py <run dir>   (reads <run dir>/<variant>/out/ele_truth_smeared/{hits,particles_simulation}.root)
"""
import uproot,numpy as np,awkward as ak,sys
R=sys.argv[1]
for v in ["gen1","gen3","gen3nocalo"]:
    d=f"{R}/{v}/out/ele_truth_smeared"
    h=uproot.open(d+"/hits.root")["hits"].arrays(["event_id","barcode_vertex_primary","barcode_vertex_secondary","barcode_particle","barcode_generation","barcode_sub_particle","tz","tx","ty"],library="np")
    p=uproot.open(d+"/particles_simulation.root")["particles"].arrays(["event_id","vertex_primary","vertex_secondary","particle","generation","sub_particle","vz","vx","vy"])
    # particle lookup
    ev=ak.flatten(ak.broadcast_arrays(p.event_id,p.vz)[0]).to_numpy()
    key=lambda e,a,b,c,g,s: (e.astype(np.int64)<<40)^(a.astype(np.int64)<<30)^(b.astype(np.int64)<<20)^(c.astype(np.int64)<<8)^(g.astype(np.int64)<<4)^s.astype(np.int64)
    pk=key(ev,*[ak.flatten(p[k]).to_numpy() for k in ["vertex_primary","vertex_secondary","particle","generation","sub_particle"]])
    pvz=ak.flatten(p.vz).to_numpy(); pvr=np.hypot(ak.flatten(p.vx).to_numpy(),ak.flatten(p.vy).to_numpy())
    o=np.argsort(pk); pk=pk[o]; pvz=pvz[o]; pvr=pvr[o]
    hk=key(h["event_id"],h["barcode_vertex_primary"],h["barcode_vertex_secondary"],h["barcode_particle"],h["barcode_generation"],h["barcode_sub_particle"])
    i=np.clip(np.searchsorted(pk,hk),0,len(pk)-1); found=pk[i]==hk
    vz=np.where(found,abs(pvz[i]),np.nan); vr=np.where(found,pvr[i],np.nan)
    sec=(h["barcode_generation"]>0)|(h["barcode_sub_particle"]>0)
    outside=found&((vz>3000)|(vr>1100))
    hz=abs(h["tz"])
    print(f"{v:11s} hits {len(hk):7d}  matched {found.mean():.3f}  from secondaries {sec.mean()*100:5.2f}%  from particles born at |z|>3000 or r>1100: {outside.sum():6d} ({outside.mean()*100:.2f}%)  of these hit |z|>2000: {(outside&(hz>2000)).sum()}")

# Secondaries born outside the tracker (collector), their direction and hits
for v in ["gen1","gen3","gen3nocalo"]:
    p=uproot.open(f"{R}/{v}/out/ele_truth_smeared/particles_simulation.root")["particles"].arrays(["vz","vx","vy","pz","q","number_of_hits"])
    vz=ak.flatten(p.vz).to_numpy(); vr=np.hypot(ak.flatten(p.vx).to_numpy(),ak.flatten(p.vy).to_numpy()); pz=ak.flatten(p.pz).to_numpy(); q=ak.flatten(p.q).to_numpy()
    nh=ak.flatten(p.number_of_hits).to_numpy()
    out=(abs(vz)>3000)|(vr>1100)
    back=out&(np.sign(pz)!=np.sign(vz))
    print(f"{v:11s} particles {len(vz):7d}  born outside tracker {out.sum():7d} (charged {(out&(q!=0)).sum():6d})  moving back toward IP {back.sum():4d} (charged {(back&(q!=0)).sum()})  with hits {(out&(nh>0)).sum()}")
