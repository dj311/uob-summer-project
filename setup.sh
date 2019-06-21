#! /usr/bin/env bash

if [ "$*" == "$s2" ] then
    echo "Run this script in root:"
    cd /

    echo "Install Ubuntu packages:"
    xargs -a ubuntu-dependencies.txt apt install -y

    echo "Install Python clang bindings:"
    wget --output-document=/tmp/clang-source.tar.xz \
        "http://releases.llvm.org/$(llvm-config --version)/cfe-$(llvm-config --version).src.tar.xz"
    tar --extract --xz --file="/tmp/clang-source.tar.xz"
    mv "/cfe-$(llvm-config --version).src" "/clang-source"
    export PYTHONPATH="${PYTHONPATH}:/clang-source/bindings/python"

    echo "Install snap-python:"
    cd /tmp && wget "http://snap.stanford.edu/snappy/release/beta/snap-5.0.9-64-3.0-centos6.5-x64-py3.6.tar.gz"
    cd /tmp && tar --extract --gz --file="snap-5.0.9-64-3.0-centos6.5-x64-py3.6.tar.gz"
    cd /tmp/snap-5.0.0-64-3.0-centos6.5-x64-py3.6 && python3 setup.py install

    echo "Download the graph2vec source code:"
    RUN git clone https://github.com/benedekrozemberczki/graph2vec.git

    echo "Install Python 2 dependencies:"
    python -m pip install --upgrade pip
    cp requirements-py2.txt /tmp/
    python -m pip install --requirement /tmp/requirements-py2.txt

    echo "Install Python 3 dependencies:"
    python3 -m pip install --upgrade pip
    cp requirements-py3.txt /tmp/
    python3 -m pip install --requirement /tmp/requirements-py3.txt

    echo "Add python 2 as a kernel for jupyter"
    RUN python -m pip install ipykernel
    RUN python -m ipykernel install

else
    echo "
# ------------------------------------------------------------------------- #
# THIS SETUP SCRIPT ASSUMES IT OWNS YOUR WHOLE MACHINE AND IS RUNNING IN A
# VM OR CONTAINER. DON'T RUN THIS ON YOUR OWN COMPUTER IT WILL MELT.
#
# Run this command with --i-know-what-im-doing do get this script to run.
# ------------------------------------------------------------------------- #
"
fi
