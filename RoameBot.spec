# -*- mode: python -*-
a = Analysis(['ROAMEbot.py'],
             pathex=['D:\\Dev\\Python\\Workspace\\RoameBot'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'RoameBot.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='Robotics-Notes-65855.ico')
