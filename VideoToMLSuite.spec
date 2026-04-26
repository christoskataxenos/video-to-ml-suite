# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['orchestrator.py'],
    pathex=[],
    binaries=[],
    datas=[('generator', 'generator'), ('labeler', 'labeler'), ('inspector', 'inspector'), ('trainer', 'trainer'), ('shared', 'shared'), ('engine\\build\\Debug\\engine.exe', 'engine')],
    hiddenimports=['generator.app', 'labeler.app', 'inspector.app', 'trainer.app'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoToMLSuite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='shared/icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoToMLSuite',
)
