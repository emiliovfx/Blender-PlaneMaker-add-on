
# CIS Flight Model Generator – Project Status Summary

## 1. Project State (Baseline Complete)

The unified CIS OBJ → PlaneMaker Generator system is now **fully functional** and stable.  
This version serves as the **official baseline** for future development (including the Blender 4.5 add‑on).

---

## 2. Modules Included in Baseline

### ✅ cis_PMGenerator.py
- Fully functional GUI  
- Dark theme applied consistently  
- Group titles styled via `GROUP_LABEL_FG`  
- Correct detection of body vs wing groups  
- Supports:
  - **Create New Aircraft** (from acfnew template)
  - **Modify Existing ACF** (backup + replace body/wing blocks)
- Correctly passes dihedral angle to wings and cowlings  
- Correctly aggregates body and wing blocks for injection  

### ✅ cis_bodies2pm.py
- Reads OBJ groups using both `g` and `o`  
- Topology-based station detection  
- Correct ring winding logic (j0..j8 +X, j9..j17 −X)  
- Handles meshes not centered on X-axis  
- Supports special cowling handling:  
  - LF_Cowling → +phi  
  - RT_Cowling → −phi  

### ✅ cis_wings2pm.py
- Detects Wing1, Wing2, HStab, VStab  
- Template-driven geometry injection  
- Airfoil logic fully implemented:  
  - Wings → NACA 2412  
  - Stabs → NACA 0009  
- Handles OBJs containing bodies and wings simultaneously  

---

## 3. Template System

### Templates/  
- `body_block_template_zeroed.txt`  
- `wing_block_template_zeroed.txt`  

Both are fully integrated and read dynamically at runtime.

---

## 4. ACF Processing Logic

### Supports:
- Full block strip + reinsertion  
- Clean creation of new aircraft files  
- Backup creation (`*_bak.acf`) for modification mode  
- Two‑stage write process for reliability  

---

## 5. GUI Visual Integration

- Entire application themed dark  
- Group frame labels readable (using global variable)  
- Logs and I/O elements clearly styled  

---

## 6. PyInstaller Readiness

The project is now fully compatible with PyInstaller.

Recommended command:

```
pyinstaller --noconsole --name CIS_PMGenerator ^
  --add-data "Templates;Templates" ^
  --add-data "acfnew;acfnew" ^
  cis_PMGenerator.py
```

A `resource_path` wrapper is required (already confirmed in code).

---

## 7. Next Phase

The next step will be the **Blender 4.5 Add‑On port**, which we will handle in a new clean chat to ensure clarity and modular development.

Before starting the new chat, this summary captures the complete working baseline.

---

## 8. Files Confirmed as “Stable Baseline”

- `cis_PMGenerator.py`  
- `cis_bodies2pm.py`  
- `cis_wings2pm.py`  
- `Templates/` folder  
- `acfnew/` folder  

These should be considered the authoritative versions going forward.

---

End of summary.
