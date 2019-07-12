# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/'],
             binaries=[],
             datas=[('icons/*.png', 'icons/'), ('words_alpha.txt', '.'), ('en_dict_words.txt', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=["PyQt5"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='AngelSubTitlePro',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='AngelSubTitlePro')
app = BUNDLE(coll,
             name='AngelSubTitlePro.app',
             icon=None,
             bundle_identifier=None)
