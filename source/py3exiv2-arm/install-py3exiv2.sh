#!/bin/sh
echo "INFO  : Install Dependencies"
sudo apt-get install -y python-all-dev
sudo apt-get install -y libexiv2-dev
sudo apt-get install -y libboost-python-dev
echo "INFO  : Done Dependencies ..."

echo "install libexiv2python.so to /usr/lib/python3/dist-packages"
sudo cp libexiv2python.so /usr/lib/python3/dist-packages/libexiv2python.so
sudo chmod 755 /usr/lib/python3/dist-packages/libexiv2python.so
echo "mkdir -p /usr/lib/python3/dist-packages/pyexiv2"
sudo mkdir -p /usr/lib/python3/dist-packages/pyexiv2
sudo cp pyexiv2/__init__.py /usr/lib/python3/dist-packages/pyexiv2/__init__.py
sudo cp pyexiv2/exif.py /usr/lib/python3/dist-packages/pyexiv2/exif.py
sudo cp pyexiv2/iptc.py /usr/lib/python3/dist-packages/pyexiv2/iptc.py
sudo cp pyexiv2/metadata.py /usr/lib/python3/dist-packages/pyexiv2/metadata.py
sudo cp pyexiv2/preview.py /usr/lib/python3/dist-packages/pyexiv2/preview.py
sudo cp pyexiv2/utils.py /usr/lib/python3/dist-packages/pyexiv2/utils.py
sudo cp pyexiv2/xmp.py /usr/lib/python3/dist-packages/pyexiv2/xmp.py
echo "Done Install"