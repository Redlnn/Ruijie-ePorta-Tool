# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['src/__main__.py'],
             pathex=['./'],
             binaries=[],
             datas=[],
             hiddenimports=['queue'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('wangluo.ico','src/wangluo.ico', 'BINARY')],
          name='Windows-Ruijie',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=['ucrtbase.dll','vcruntime140.dll'],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          version='version.txt',
          icon='src/wangluo.ico')
