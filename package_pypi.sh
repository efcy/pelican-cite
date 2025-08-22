python -m pip install build twine
echo "build pelican cite package"
python -m build

cat <<EOF > .pypirc
[pypi]

username = __token__
password = $PYPI_TOKEN
EOF

echo "publish pelican-cite package to pypi"
python3 -m twine upload dist/* --config-file .pypirc
