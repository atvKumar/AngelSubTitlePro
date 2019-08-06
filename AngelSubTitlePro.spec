# -*- mode: python -*-
import sys
block_cipher = None


a = Analysis(['main.py'],
             pathex=['/' if sys.platform == 'win32' else 'G:\\Kumar_Development\\AngelSubTitlePro'],
             binaries=[],
             datas=[('icons/*.png', 'icons/'), ('dictionary/*.txt', 'dictionary/')],
             hiddenimports=['numpy.random.common', 'numpy.random.bounded_integers', 'numpy.random.entropy'],
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
          a.binaries + [('C:\\Program Files\\VideoLAN\\VLC\\libvlc.dll', '.'),
                        ('C:\\Program Files\\VideoLAN\\VLC\\libvlccore.dll', '.'),
                        ('C:\\Users\\MO7\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\shiboken2\\shiboken2.abi3.dll', '.'),
                        ('C:\\Users\\MO7\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\shiboken2\\msvcp140.dll', '.')]
                        if sys.platform == 'win32' else [],
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
               (Tree('C:\\Program Files\\VideoLAN\\VLC\\plugins', prefix='plugins\\') if sys.platform == 'win32' else []),
               strip=False,
               upx=True,
               upx_exclude=[],
               name='AngelSubTitlePro')

if sys.platform == 'darwin':
    app = BUNDLE(coll,
                name='AngelSubTitlePro.app',
                icon=None,
                bundle_identifier=None)
