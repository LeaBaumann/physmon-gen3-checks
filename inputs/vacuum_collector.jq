# Keep every surface entry, but empty the calorimeter-collector surfaces:
# each of their bins becomes vacuum with zero thickness, the format the map
# already uses for empty bins. Every designated material key stays present.
.surfaces |= map(
  if (.target.key | startswith("CaloMaterialCollector"))
  then .material.values |= map({"material": {"kind": "vacuum"}, "thickness": 0.0})
  else . end)
