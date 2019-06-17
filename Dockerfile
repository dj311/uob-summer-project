FROM ubuntu:rolling

RUN apt-get update && apt-get install -y \
    wget \
    llvm \
    clang \
    python3 \
    python3-pip

# Manually install the Python 3 clang bindings
RUN wget --output-document=/tmp/clang-source.tar.xz \
    "http://releases.llvm.org/$(llvm-config --version)/cfe-$(llvm-config --version).src.tar.xz"
RUN tar --extract --xz --file="/tmp/clang-source.tar.xz"
RUN mv "/cfe-$(llvm-config --version).src" "/clang-source"

ENV PYTHONPATH "${PYTHONPATH}:/clang-source/bindings/python"

# Manually install the SNAP python library for node2vec
RUN cd /tmp && wget "http://snap.stanford.edu/snappy/release/beta/snap-5.0.9-64-3.0-centos6.5-x64-py3.6.tar.gz"
RUN cd /tmp && tar --extract --gz --file="snap-5.0.9-64-3.0-centos6.5-x64-py3.6.tar.gz"
RUN cd /tmp/snap-5.0.0-64-3.0-centos6.5-x64-py3.6 && python3 setup.py install

# Install Python dependencies. These are most likely to change, so go
# near the bottom of the file.
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN python3 -m pip install --requirement /tmp/requirements.txt

# Run for a jupyter notebook by default
WORKDIR "/project"
EXPOSE 8888
CMD ["jupyter", "notebook", "--allow-root", "--ip", "0.0.0.0", "--no-browser"]