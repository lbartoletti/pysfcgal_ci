# Install python3 from OSGeo4W
Invoke-WebRequest -Uri "https://download.osgeo.org/osgeo4w/osgeo4w-setup-v2.exe" -OutFile "osgeo4w-setup-v2.exe"
Start-Process -FilePath "osgeo4w-setup-v2.exe" -ArgumentList "--advanced --autoaccept --delete-orphans --no-desktop --quiet-mode --upgrade-also --site https://download.osgeo.org/osgeo4w/v2 --packages python3-core,python3-pip,python3-devel" -Wait
Remove-Item -Path .\osgeo4w-setup-v2.exe -Force
C:\OSGeo4W\OSGeo4W.bat python3 -m pip install -U pip build delvewheel

# Generate the wheel
$env:INCLUDE='c:\SFCGAL\build\include\'
$env:LIB='c:\SFCGAL\build\src\Release\'
C:\OSGeo4W\OSGeo4W.bat python3 -m build

# Add sfcgal dll with delvewheel
$env:WHEEL_NAME=Get-ChildItem -Path dist/* -Include *.whl
C:\OSGeo4W\OSGeo4W.bat delvewheel repair --add-path $env:LIB -w dist $env:WHEEL_NAME

# Rename dist directory to prevent issues with build from other os
Rename-Item -Path "dist" -NewName "dist_windows"
